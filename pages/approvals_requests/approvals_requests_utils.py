import pandas as pd
import logging

logger = logging.getLogger(__name__)

def handle_status_name(df, column_name="status"):
    """
    Change the status received in the back-end to a user-friendly name.
    
    Args:
        df: DataFrame containing approval requests data
        column_name: Column name containing the status codes
        
    Returns:
        DataFrame with status codes mapped to user-friendly names
    """

    status_map = {
        1: "Aprovado",
        2: "Rejeitado",
        3: "Pendente",
    }

    df[column_name] = df[column_name].map(status_map).fillna(df[column_name])

    return df

def handle_process_name(df, column_name="source_table"):
    """
    Change the process name received in the back-end to a user-friendly name.
    
    Args:
        df: DataFrame containing a table with a column with the process name
        
    Returns:
        DataFrame with process names mapped to user-friendly names
    """
    process_map = {
        "buildup": "Buildup",
        "catlote": "Catlote Desc.",
        "captain": "Capitão",
        "captain_margin": "Margem do Capitão",
        "delta": "Delta Preço",
        "marketing": "Posicionamento de Mercado",
        "price": "Arquitetura de Preços",
        "optimization": "Otimização de Preços",
        "strategy": "Estratégia Comercial",
    }

    df[column_name] = df[column_name].map(process_map).fillna(df[column_name])

    return df

def handle_date_format(df, column_name="data_alteracoes"):
    """
    Change the date received in the back-end to a user-friendly format.
    
    Args:
        df: DataFrame containing a table with a column with the date
        
    Returns:
        DataFrame with date formatted as 'dd/mm/yyyy'
    """
    try:
        df[column_name] = pd.to_datetime(df[column_name])
        df['data_alteracoes_data'] = df[column_name].dt.strftime('%d/%m/%Y')
    except Exception as e:
        logger.error(f"Error processing date information: {e}")
    return df
