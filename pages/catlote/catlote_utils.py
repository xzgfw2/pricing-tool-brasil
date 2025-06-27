import pandas as pd

def generate_code_string(index: str, type: str) -> str:
    code_number = index[-1]
    
    if "participation-input" in type:
        type_code = "P"
    elif "discount-input" in type:
        type_code = "D"
    else:
        type_code = ""
    
    return f"{type_code}{code_number}"

def update_property(data, property_name, new_value):
    """
    Atualiza o valor de uma propriedade dentro de uma lista de dicionários.
    
    Parâmetros:
        data (list): Lista contendo um dicionário.
        property_name (str): Nome da propriedade a ser alterada.
        new_value: Novo valor a ser atribuído.
        
    Retorna:
        list: Lista de dicionários com a propriedade alterada.
    """
    if data and isinstance(data, list) and isinstance(data[0], dict):
        if property_name in data[0]:
            data[0][property_name] = int(new_value) / 100
    return data

def get_unique_values(df, column_name):
    """
    Retorna uma lista com os valores únicos de uma coluna de um DataFrame.

    Parâmetros:
    df (pd.DataFrame): O DataFrame de onde os valores serão extraídos.
    column_name (str): O nome da coluna.

    Retorno:
    list: Uma lista com os valores únicos da coluna.
    """
    if column_name in df.columns:
        return df[column_name].drop_duplicates().tolist()
    else:
        raise ValueError(f"A coluna '{column_name}' não existe no DataFrame.")

def get_catlote_ids(catlote_data):

    catlotes_id = []

    for row in catlote_data:
        catlote_id = row.get('CATLOTE_1') or row.get('CATLOT1')
        if catlote_id:
            catlotes_id.append(catlote_id)
    return catlotes_id

def calculate_catlote(catlote_inputs, catlote_data_products, new_values=None):
    """
    Função para calcular faturamento baseado em dados de Catlote
    
    Parâmetros:
    - catlote_inputs: Lista de dicionários com informações de Catlote
    - catlote_data_products: DataFrame com dados de produtos
    - new_values: Dicionário com informações sobre a célula alterada
    
    Retorna:
    - DataFrame com cálculos de faturamento
    """

    df = pd.DataFrame(catlote_data_products).fillna(0)

    # Se não houver alterações ou se for a primeira vez, calcula todas as linhas
    if new_values is None or all(value is None for value in new_values.values()):
        # Calcula para todas as linhas
        for index, row in df.iterrows():
            df = calculate_row(df, index, row, catlote_inputs, None)
    else:
        # Calcula apenas para a linha alterada
        row_index = new_values.get("row_index")
        if row_index is not None:
            row = df.iloc[row_index]
            df = calculate_row(df, row_index, row, catlote_inputs, new_values)

    return {
        "table": df,
        "totals": calculate_totals(df)
    }

def calculate_row(df, index, row, catlote_inputs, new_values):
    """
    Calcula os valores para uma linha específica
    """
    matching_catlote = next((catlote for catlote in catlote_inputs if catlote['CATLOT1'] == row['CATLOTE_1']), None)

    if matching_catlote is None:
        print(f" Nenhum Catlote encontrado para {row['CATLOT1']}")
        return df

    # Parâmetros para cálculo
    desconto = row['desconto']
    media_promo = row['media_promo']
    imp = row['imp']
    imp_icms = row['imp_icms']
    
    # Verifica qual campo foi alterado e usa o novo valor
    if new_values and new_values["changed_col_name"] == "custo_medio_unit":
        custo_medio_unit = float(new_values["new_value"])
        df.at[index, 'custo_medio_unit'] = custo_medio_unit
    else:
        custo_medio_unit = row['custo_medio_unit']

    if new_values and new_values["changed_col_name"] == "preco_sap_atual":
        price_sap_new = float(new_values["new_value"])
        df.at[index, 'preco_sap_atual'] = price_sap_new
    else:
        price_sap_new = row['preco_sap_atual']

    price_sap_old = new_values["old_value"] if new_values and new_values["changed_col_name"] == "preco_sap_atual" else price_sap_new
    media_regular = row['media_regular']
    elasticity = row['e']

    new_price_with_taxes = round(price_sap_new * imp_icms, 2)
    old_price_with_taxes = row['preco_com_impostos'] if 'preco_com_impostos' in row else new_price_with_taxes

    delta_price = round(price_sap_new / price_sap_old - 1, 4) if price_sap_old != 0 else 0

    # Cálculo da média regular
    new_avg_regular = 0 if media_regular == 0 else media_regular * (1 + delta_price) ** elasticity
    delta_volume_regular = 0 if media_regular == 0 else (new_avg_regular / media_regular - 1)

    # Atualiza os valores no DataFrame com os tipos corretos
    df.at[index, 'media_regular'] = int(round(new_avg_regular, 0))
    df.at[index, 'delta_volume_regular'] = float(delta_volume_regular)

    # Cálculo da média promo
    new_avg_promo = 0 if media_promo == 0 else media_promo * (1 + delta_price) ** elasticity
    delta_volume_promo = 0 if media_promo == 0 else (new_avg_promo / media_promo - 1)
    avg_promo_final = int(round(new_avg_promo, 0))

    # Atualiza os valores calculados na linha específica
    df.at[index, 'media_promo'] = avg_promo_final
    df.at[index, 'preco_com_impostos'] = new_price_with_taxes

    # Cálculos sem campanha
    df.at[index, 'faturamento_l1_sc'] = new_price_with_taxes * (1 - desconto) * matching_catlote['P1'] * int(round(new_avg_regular, 0))
    df.at[index, 'faturamento_l2_sc'] = new_price_with_taxes * (1 - desconto) * matching_catlote['P2'] * int(round(new_avg_regular, 0))
    df.at[index, 'faturamento_l3_sc'] = new_price_with_taxes * (1 - desconto) * matching_catlote['P3'] * int(round(new_avg_regular, 0))
    df.at[index, 'faturamento_l4_sc'] = new_price_with_taxes * (1 - desconto) * matching_catlote['P4'] * int(round(new_avg_regular, 0))

    df.at[index, 'faturamento_liq_l1_sc'] = (new_price_with_taxes * (1 - desconto) * imp) * matching_catlote['P1'] * int(round(new_avg_regular, 0))
    df.at[index, 'faturamento_liq_l2_sc'] = (new_price_with_taxes * (1 - desconto) * imp) * matching_catlote['P2'] * int(round(new_avg_regular, 0))
    df.at[index, 'faturamento_liq_l3_sc'] = (new_price_with_taxes * (1 - desconto) * imp) * matching_catlote['P3'] * int(round(new_avg_regular, 0))
    df.at[index, 'faturamento_liq_l4_sc'] = (new_price_with_taxes * (1 - desconto) * imp) * matching_catlote['P4'] * int(round(new_avg_regular, 0))

    df.at[index, 'margem_l1_sc'] = ((new_price_with_taxes * (1 - desconto) * imp) - custo_medio_unit) * matching_catlote['P1'] * int(round(new_avg_regular, 0))
    df.at[index, 'margem_l2_sc'] = ((new_price_with_taxes * (1 - desconto) * imp) - custo_medio_unit) * matching_catlote['P2'] * int(round(new_avg_regular, 0))
    df.at[index, 'margem_l3_sc'] = ((new_price_with_taxes * (1 - desconto) * imp) - custo_medio_unit) * matching_catlote['P3'] * int(round(new_avg_regular, 0))
    df.at[index, 'margem_l4_sc'] = ((new_price_with_taxes * (1 - desconto) * imp) - custo_medio_unit) * matching_catlote['P4'] * int(round(new_avg_regular, 0))

    # Cálculos com campanha
    df.at[index, 'faturamento_l1_cc'] = new_price_with_taxes * (1 + matching_catlote['D1']) * matching_catlote['E1'] * avg_promo_final
    df.at[index, 'faturamento_l2_cc'] = new_price_with_taxes * (1 + matching_catlote['D2']) * matching_catlote['E2'] * avg_promo_final
    df.at[index, 'faturamento_l3_cc'] = new_price_with_taxes * (1 + matching_catlote['D3']) * matching_catlote['E3'] * avg_promo_final
    df.at[index, 'faturamento_l4_cc'] = new_price_with_taxes * (1 + matching_catlote['D4']) * matching_catlote['E4'] * avg_promo_final

    df.at[index, 'faturamento_liq_l1_cc'] = (new_price_with_taxes * (1 + matching_catlote['D1']) * imp) * matching_catlote['E1'] * avg_promo_final
    df.at[index, 'faturamento_liq_l2_cc'] = (new_price_with_taxes * (1 + matching_catlote['D2']) * imp) * matching_catlote['E2'] * avg_promo_final
    df.at[index, 'faturamento_liq_l3_cc'] = (new_price_with_taxes * (1 + matching_catlote['D3']) * imp) * matching_catlote['E3'] * avg_promo_final
    df.at[index, 'faturamento_liq_l4_cc'] = (new_price_with_taxes * (1 + matching_catlote['D4']) * imp) * matching_catlote['E4'] * avg_promo_final

    df.at[index, 'margem_l1_cc'] = ((new_price_with_taxes * (1 + matching_catlote['D1']) * imp) - custo_medio_unit) * matching_catlote['E1'] * avg_promo_final
    df.at[index, 'margem_l2_cc'] = ((new_price_with_taxes * (1 + matching_catlote['D2']) * imp) - custo_medio_unit) * matching_catlote['E2'] * avg_promo_final
    df.at[index, 'margem_l3_cc'] = ((new_price_with_taxes * (1 + matching_catlote['D3']) * imp) - custo_medio_unit) * matching_catlote['E3'] * avg_promo_final
    df.at[index, 'margem_l4_cc'] = ((new_price_with_taxes * (1 + matching_catlote['D4']) * imp) - custo_medio_unit) * matching_catlote['E4'] * avg_promo_final

    # Cálculo das margens relativas
    for i in range(1, 5):
        try:
            denominator = new_price_with_taxes * (1 + matching_catlote[f'D{i}']) * imp
            if denominator == 0:
                df.at[index, f'margem_rel_l{i}_cc'] = 0
            else:
                numerator = (new_price_with_taxes * (1 + matching_catlote[f'D{i}']) * imp) - custo_medio_unit
                df.at[index, f'margem_rel_l{i}_cc'] = pd.to_numeric(numerator / denominator, errors='coerce')
        except (KeyError, ZeroDivisionError):
            df.at[index, f'margem_rel_l{i}_cc'] = 0

    return df.round(2)

def calculate_totals(df):
    """
    Calcula os totais para os cards
    """
    total_faturamento_sc = df[[f'faturamento_l{i}_sc' for i in range(1, 5)]].sum().sum()
    total_faturamento_cc = df[[f'faturamento_l{i}_cc' for i in range(1, 5)]].sum().sum()
    total_faturamento_liq_sc = df[[f'faturamento_liq_l{i}_sc' for i in range(1, 5)]].sum().sum()
    total_faturamento_liq_cc = df[[f'faturamento_liq_l{i}_cc' for i in range(1, 5)]].sum().sum()
    total_margem_sc = df[[f'margem_l{i}_sc' for i in range(1, 5)]].sum().sum()
    total_margem_cc = df[[f'margem_l{i}_cc' for i in range(1, 5)]].sum().sum()
    total_volume_sc = int(df['media_regular'].sum())
    total_volume_cc = int(df['media_promo'].sum())

    # Calcula as margens relativas totais
    total_margem_rel_sc = total_margem_sc / total_faturamento_liq_sc if total_faturamento_liq_sc != 0 else 0
    total_margem_rel_cc = total_margem_cc / total_faturamento_liq_cc if total_faturamento_liq_cc != 0 else 0

    return {
        "total_faturamento_sc": total_faturamento_sc,
        "total_faturamento_cc": total_faturamento_cc,
        "total_faturamento_liq_sc": total_faturamento_liq_sc,
        "total_faturamento_liq_cc": total_faturamento_liq_cc,
        "total_margem_sc": total_margem_sc,
        "total_margem_cc": total_margem_cc,
        "total_volume_sc": total_volume_sc,
        "total_volume_cc": total_volume_cc,
        "total_margem_rel_sc": total_margem_rel_sc,
        "total_margem_rel_cc": total_margem_rel_cc
    }
