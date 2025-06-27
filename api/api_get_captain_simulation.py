import os
from dotenv import load_dotenv
from databricks import sql
import pandas as pd

load_dotenv()

def connect_sql():
    try:
        DB_SERVER = os.getenv('DB_SERVER')
        DB_HTTP_PATH = os.getenv('DB_HTTP_PATH')
        DB_TOKEN = os.getenv('DB_TOKEN')

        connection = sql.connect(
            server_hostname=DB_SERVER,
            http_path=DB_HTTP_PATH,
            access_token=DB_TOKEN
        )
        return connection
    except Exception as e:
        print(f"Erro ao conectar ao SQL: {e}")
        return None

def get_captain_simulation():
    print("get_captain_simulation")

    BASE_NAME_DB = 'maxis_sandbox.pricing_db.dump_capitao_temp'
    
    connection = connect_sql()
    if connection is None:
        # print("Conexão não foi estabelecida.")
        return None

    try:
        with connection.cursor() as cursor:
            cursor.execute(f"SELECT * FROM {BASE_NAME_DB} WHERE data_simulacao = (SELECT MAX(data_simulacao) FROM {BASE_NAME_DB})")
            result = cursor.fetchall()
            columns = [desc[0] for desc in cursor.description]
            
            df = pd.DataFrame(result, columns=columns)
            # print("Primeiras 10 linhas do dataframe:\n", df.head(10))
            
        return df
    except Exception as e:
        print(f"Erro ao obter simulação: {e}")
        return None
    finally:
        connection.close()
