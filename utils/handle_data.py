import pandas as pd
import polars as pl
import json

def handle_data(df, decimal_places=2, date_format=None):
    """
    Função que verifica o tipo de cada coluna de um DataFrame (Pandas ou Polars) 
    e realiza tratamentos específicos:
    - Colunas numéricas são arredondadas para o número especificado de casas decimais.
    - Colunas de data são formatadas com base na máscara fornecida (apenas Pandas).
    
    Parâmetros:
        df (pd.DataFrame | pl.DataFrame): DataFrame a ser tratado (Pandas ou Polars).
        decimal_places (int): Número de casas decimais para arredondar colunas numéricas.
        date_format (str): Máscara para formatar colunas de data (apenas Pandas).
        
    Retorna:
        pd.DataFrame | pl.DataFrame: DataFrame com as colunas tratadas.
    """
    if not isinstance(df, pd.DataFrame):
        try:
            # If data is a JSON string, try to parse it first
            if isinstance(df, str):
                df = json.loads(df)
            
            # Convert to DataFrame
            df = pd.DataFrame(df)
            
            # If DataFrame is empty, return None
            if df.empty:
                return None
                
        except Exception as e:
            print(f"Error converting data to DataFrame: {str(e)}")
            return None
    
    if isinstance(df, pd.DataFrame):
        # Tratamento para Pandas DataFrame
        for coluna in df.columns:
            # Verifica se a coluna é do tipo numérico
            if pd.api.types.is_numeric_dtype(df[coluna]):
                df[coluna] = df[coluna].round(decimal_places)
            # Verifica se a coluna é do tipo datetime
            elif pd.api.types.is_datetime64_any_dtype(df[coluna]) and date_format:
                df[coluna] = df[coluna].dt.strftime(date_format)
        return df

    elif isinstance(df, pl.DataFrame):
        # Tratamento para Polars DataFrame
        for coluna in df.columns:
            tipo_coluna = df.schema[coluna]
            # Verifica se a coluna é do tipo numérico
            if tipo_coluna in [pl.Float32, pl.Float64, pl.Int32, pl.Int64]:
                df = df.with_columns(pl.col(coluna).round(decimal_places))
            # Verifica se a coluna é do tipo datetime
            elif tipo_coluna == pl.Date or tipo_coluna == pl.Datetime and decimal_places:
                df = df.with_columns(pl.col(coluna).dt.strftime(decimal_places))
        return df

    else:
        raise TypeError("O objeto fornecido não é um DataFrame válido (Pandas ou Polars).")
