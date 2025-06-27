import os
from dotenv import load_dotenv
from databricks import sql
import pandas as pd
import polars as pl

load_dotenv()

def get_initial_data_configs(process_name, cpc=None, quarter=None, year=None):
    """
    Retrieves data configurations from the database based on the process name and filters.
    
    Args:
        process_name (str): The name of the process to retrieve data for.
        cpc (list, optional): List of CPC codes to filter by. Defaults to None.
        quarter (str, optional): Quarter to filter by. Defaults to None.
        year (str, optional): Year to filter by. Defaults to None.
        
    Returns:
        DataFrame: A pandas or polars DataFrame containing the requested data.
        If an error occurs or no data is found, returns a dictionary with an error message.
    """
    connection = None
    cursor = None
    
    try:
        DB_SERVER = os.getenv('DB_SERVER')
        DB_HTTP_PATH = os.getenv('DB_HTTP_PATH')
        DB_TOKEN = os.getenv('DB_TOKEN')

        if not all([DB_SERVER, DB_HTTP_PATH, DB_TOKEN]):
            return {"error": "Configurações de banco de dados incompletas. Verifique as variáveis de ambiente."}

        connection = sql.connect(
            server_hostname=DB_SERVER,
            http_path=DB_HTTP_PATH,
            access_token=DB_TOKEN
        )

        base_name_db = {
            "buildup": 'maxis_sandbox.pricing_db.de_para_buildup',
            "buildup_fx": 'maxis_sandbox.tabelas_cca.mpg_fx_actuals',
            "captain": 'maxis_sandbox.pricing_db.d_capitao',
            "captain_variables": "maxis_sandbox.pricing_db.var_fatores_capitao",
            "strategy": 'maxis_sandbox.pricing_db.d_estrategia_comercial',
            "marketing": 'maxis_sandbox.pricing_db.d_mercado',
            "captain_margin": 'maxis_sandbox.pricing_db.d_par_margem_cap',
            "delta": 'maxis_sandbox.pricing_db.d_par_delta_preco',
        }

        if process_name not in base_name_db:
            return {"error": f"Processo '{process_name}' não encontrado. Processos válidos: {', '.join(base_name_db.keys())}"}

        cursor = connection.cursor()

        if cpc in (None, []):
            if process_name == "buildup":
                cursor.execute(f"SELECT * FROM {base_name_db['buildup']}")
            else:
                cursor.execute(f"SELECT * FROM {base_name_db[process_name]}")
        else:
            cpc_filter = "', '".join(cpc)
            cursor.execute(f"SELECT * FROM {base_name_db[process_name]} WHERE cpc1_3_6 IN ('{cpc_filter}')")

        result = cursor.fetchall()
        if not result:
            return {"error": f"Nenhum dado retornado para o processo de '{process_name}', por favor verificar com o suporte técnico."}

        if process_name == "buildup":
            df = pl.DataFrame(result, orient="row", schema=[desc[0] for desc in cursor.description])
        else:
            df = pd.DataFrame(result, columns=[desc[0] for desc in cursor.description])

        return df

    except sql.Error as e:
        return {"error": f"Erro de banco de dados: {str(e)}"}
    except Exception as e:
        return {"error": f"Erro inesperado: {str(e)}"}
    finally:
        if cursor:
            try:
                cursor.close()
            except:
                pass
        if connection:
            try:
                connection.close()
            except:
                pass
