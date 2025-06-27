"""Módulo de conexão com o Databricks para trazer dados do banco de dados"""

import os
# import polars as pl
import pandas as pd
from dotenv import load_dotenv
from databricks import sql

load_dotenv()

def get_catlote_sim(catlote_filter):
    print("get_catlote_sim")

    base_name_db = 'maxis_sandbox.pricing_db.d_catlote_produto_vf'

    db_server = os.getenv('DB_SERVER')
    db_http_path = os.getenv('DB_HTTP_PATH')
    db_token = os.getenv('DB_TOKEN')

    if not db_server or not db_http_path or not db_token:
        raise EnvironmentError("Erro: Uma ou mais variáveis de ambiente não foram carregadas. Verifique seu arquivo .env.")

    try:
        with sql.connect(
            server_hostname=db_server,
            http_path=db_http_path,
            access_token=db_token
        ) as connection:
            with connection.cursor() as cursor:

                placeholders = ', '.join(['?'] * len(catlote_filter))
                query = f"SELECT * FROM {base_name_db} WHERE CATLOTE_1 IN ({placeholders}) ORDER BY CATLOTE_1"
                cursor.execute(query, catlote_filter)
                # cursor.execute(f"SELECT * FROM {base_name_db}")

                result = cursor.fetchall()

                if not result:
                    raise ValueError("Erro: A consulta retornou resultados vazios.")

                df = pd.DataFrame(result, columns=[desc[0] for desc in cursor.description])

                print("[desc[0] for desc in cursor.description]", [desc[0] for desc in cursor.description])
                # print("df", df.head(10))

                cursor.close()

    except Exception as e:
        raise ConnectionError(f"Erro ao conectar ou executar a query: {str(e)}") from e

    return df
