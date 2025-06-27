import polars as pl
from api.get_initial_data_configs import get_initial_data_configs
from copy import deepcopy

def get_month_from_quarter(quarter):
    quarter_to_months = {
        'Q1': 1,
        'Q2': 4,
        'Q3': 7,
        'Q4': 10
    }

    return quarter_to_months.get(quarter, "Trimestre inválido")

def fetch_tax_rates(table_currency, currency_code, month, year):
    year = int(year)
    month = int(month)

    mask = (
        (table_currency["TOCURRENCY"].astype(str).str.strip() == currency_code) & 
        (table_currency["RATEYEAR"].astype(int) == year) & 
        (table_currency["RATEMONTH"].astype(int) == month)
    )

    filtered_df = table_currency[mask]

    if filtered_df.empty:
        raise ValueError(f"No exchange rate found for {currency_code} in year {year}, month {month}")

    rate = filtered_df["RATE"].iloc[0]

    return float(rate) if rate is not None else rate

def get_tax_rates(table_currency, currency_selected, month, year):
    """
    Converte taxas de câmbio com base na moeda selecionada e período específico.
    Aqui faço uma "conversão" de moeda. Na aplicação os valores são em reais, mas na tabela de fx os valores são em dólares.

    :param table_currency: DataFrame contendo as taxas de câmbio.
    :param currency_selected: Moeda de destino ("BRL", "USD", "JPY").
    :param quarter: Trimestre para filtrar as taxas.
    :param year: Ano para filtrar as taxas.
    :return: Taxa de conversão.
    """

    currency_code = None
    currency_rate = None  # Evita problemas caso não seja atualizado

    if currency_selected == "BRL":
        currency_code = "USD"
        currency_rate = fetch_tax_rates(table_currency, currency_code, month, year)

    elif currency_selected == "USD":
        currency_code = "BRL"
        currency_rate = fetch_tax_rates(table_currency, currency_code, month, year)

    elif currency_selected == "JPY":
        currency_rate_USD_to_BRL = fetch_tax_rates(table_currency, currency_code="BRL", month=month, year=year)
        currency_rate_USD_to_JPY = fetch_tax_rates(table_currency, currency_code="JPY", month=month, year=year)
        currency_rate = currency_rate_USD_to_JPY / currency_rate_USD_to_BRL

    return currency_rate

def handle_raw_dataframe(df):
    if df is None:
        return None

    # Converter uuid_alteracoes para string se existir
    if "uuid_alteracoes" in df.columns:
        df = df.with_columns(pl.col("uuid_alteracoes").cast(pl.Utf8))

    not_show_rows_if_buildup_is = [
        # 'quarter',
        # 'formatted_year',
        # 'concatenated_column',
        'year',
        'custom',
        'quarter_year',
        'buildup',
        'import_tax',
        'uuid_alteracoes',
    ]

    buildup_factors = [col for col in df.columns if col not in not_show_rows_if_buildup_is]
    id_vars = ["buildup", "quarter", "formatted_year"]

    if "uuid_alteracoes" in df.columns:
        id_vars.append("uuid_alteracoes")

    melt_table = df.melt(
            id_vars=id_vars,
            value_vars=buildup_factors,
            variable_name="buildup_factors",
            value_name="valor"
        ).with_columns([
            pl.col("buildup").str.to_uppercase(),
        ])

    pivot_index = ["buildup_factors", "quarter", "formatted_year"]

    if "uuid_alteracoes" in melt_table.columns:
        pivot_index.append("uuid_alteracoes")

    result = melt_table.pivot(
        values="valor",
        index=pivot_index,
        columns=["buildup"],
        maintain_order=True,
        aggregate_function="first"
    )

    # Ordenamos as colunas alfabeticamente
    columns = [col for col in result.columns if col not in ["buildup_factors", "uuid_alteracoes"]]

    columns.sort()
    ordered_columns = ["buildup_factors"] + columns

    if "uuid_alteracoes" in result.columns:
        ordered_columns.append("uuid_alteracoes")

    # Selecionamos as colunas na nova ordem
    result = result.select(ordered_columns)

    return result

def reverse_raw_dataframe(df):
    """
    Reverte as transformações feitas pela função handle_raw_dataframe.
    
    Args:
        df (polars.DataFrame): DataFrame no formato pivotado (resultado do handle_raw_dataframe)
        
    Returns:
        polars.DataFrame: DataFrame no formato original
    """
    unpivoted = df.melt(
        id_vars=["buildup_factors"],
        variable_name="buildup",
        value_name="valor"
    )

    # Convertemos o buildup de volta para lowercase
    unpivoted = unpivoted.with_columns(
        pl.col("buildup").str.to_lowercase()
    )

    # Reorganizamos as colunas para o formato original
    result = unpivoted.pivot(
        values="valor",
        index="buildup",
        columns="buildup_factors",
        # aggregate_function="first"  # Adicionando função de agregação para lidar com duplicatas
    )

    return result

def merge_with_original_data(reversed_df):
    """
    Combina o DataFrame revertido com as colunas originais do get_initial_data_configs.
    Mantém os dados do reversed_df e adiciona apenas as colunas que existem somente na original_data.
    
    Args:
        reversed_df (polars.DataFrame): DataFrame resultado da função reverse_raw_dataframe
        
    Returns:
        polars.DataFrame: DataFrame com dados do reversed_df mais as colunas exclusivas do original_data
    """
    original_data = get_initial_data_configs(process_name="buildup")
    # Converte para polars se necessário
    # if not isinstance(original_data, pl.DataFrame):
    #     original_data = pl.from_pandas(original_data)

    # # Identifica colunas que existem apenas no DataFrame original
    # original_only_columns = [col for col in original_data.columns if col not in reversed_df.columns]

    # print("original_only_columns")
    # print(original_only_columns)



    # Se não houver colunas exclusivas do original_data, retorna o reversed_df como está
    # if not original_only_columns:
    #     return reversed_df

    # Seleciona apenas as colunas exclusivas do original_data mais a coluna de join
    # original_data_subset = original_data.select(['buildup'] + original_only_columns)
    
    # Faz o join mantendo todos os dados do reversed_df e adicionando as colunas do original_data
    # result = reversed_df.join(
    #     original_data_subset,
    #     on="buildup",
    #     how="left"
    # )

    # join = original_data.join(
    #     reversed_df,
    #     on="concatenated_column",
    #     how="left"
    # )

    df_resultado = (
        original_data
        .join(reversed_df, on="concatenated_column", how="left")
        .select(original_data.columns)  # Mantém apenas colunas originais da tabela da esquerda
        # .with_columns(
        #     pl.coalesce(["valor_novo", "valor"]).alias("valor")  # Atualiza valores onde houver correspondência
        # )
    )

    print("merge_with_original_data - result")
    print(df_resultado)

    return df_resultado
