import os
from dotenv import load_dotenv
from databricks import sql
import pandas as pd

load_dotenv()

def get_var_arq_price(variable):
    print("get_var_arq_price")

    DB_SERVER = os.getenv('DB_SERVER')
    DB_HTTP_PATH = os.getenv('DB_HTTP_PATH')
    DB_TOKEN = os.getenv('DB_TOKEN')

    connection = sql.connect(
        server_hostname = DB_SERVER,
        http_path = DB_HTTP_PATH,
        access_token = DB_TOKEN
    )

    BASE_NAME_DB = 'maxis_sandbox.pricing_db.'

    NOTEBOOK_PATHS = {
        'marca': BASE_NAME_DB + 'var_marca_resumo',
        'elasticidade': BASE_NAME_DB + 'var_elasticidade_resumo',
        'frota': BASE_NAME_DB + 'var_frota_disponivel_resumo',
        'ano frota': BASE_NAME_DB + 'var_ano_frota_resumo',
        'aplicacoes': BASE_NAME_DB + 'var_aplicacoes_resumo',
        'estoque': BASE_NAME_DB + 'var_meses_em_estoque_resumo',
        'price index': BASE_NAME_DB + 'var_price_index_resumo',
    }

    cursor = connection.cursor()
    cursor.execute(f"SELECT * from {NOTEBOOK_PATHS[variable]}")

    result = cursor.fetchall()
    df = pd.DataFrame(result, columns=[desc[0] for desc in cursor.description])
    # print("df", df)

    cursor.close()
    connection.close()

    return df
