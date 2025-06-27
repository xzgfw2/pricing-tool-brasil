"""Módulo de conexão com o Databricks para trazer dados do banco de dados"""

import os
import pandas as pd
from dotenv import load_dotenv
from databricks import sql

load_dotenv()

def get_permissions():
    print("get_permissions")

    base_name_db = 'maxis_sandbox.pricing_db.de_para_roles_telas'

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

                cursor.execute(f"SELECT * from {base_name_db}")
                result = cursor.fetchall()

                if not result:
                    raise ValueError("Erro: A consulta retornou resultados vazios.")

                df = pd.DataFrame(result, columns=[desc[0] for desc in cursor.description])
                # print("[desc[0] for desc in cursor.description]", [desc[0] for desc in cursor.description])                

                # print("df", df[])
                for coluna in df.columns:
                    print(f"Coluna: {coluna}")
                    print(df[coluna].head())
                    print("-" * 20)  # Separador para melhor visualização

                cursor.close()
                connection.close()

    except Exception as e:
        raise ConnectionError(f"Erro ao conectar ou executar a query: {str(e)}") from e

    return df

# get_permissions()
