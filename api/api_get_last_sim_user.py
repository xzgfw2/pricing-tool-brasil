import os
from dotenv import load_dotenv
from databricks import sql
import pandas as pd

load_dotenv()

def get_last_sim_user():
    print("get_last_sim_user")
    print("Chamada para obter a simulação")

    DB_SERVER = os.getenv('DB_SERVER')
    DB_HTTP_PATH = os.getenv('DB_HTTP_PATH')
    DB_TOKEN = os.getenv('DB_TOKEN')

    BASE_NAME_DB = 'maxis_sandbox.pricing_db.v_ultima_sim'

    try:
        connection = sql.connect(
            server_hostname=DB_SERVER,
            http_path=DB_HTTP_PATH,
            access_token=DB_TOKEN
        )
        print("Conexão com o banco de dados estabelecida com sucesso.")
    except Exception as e:
        print(f"Erro ao conectar ao banco de dados: {e}")
        raise

    try:
        cursor = connection.cursor()
        cursor.execute(f"SELECT * from {BASE_NAME_DB}")

        result = cursor.fetchall()

        df = pd.DataFrame(result, columns=[desc[0] for desc in cursor.description])

        print("Fields:", [desc[0] for desc in cursor.description])
        print("DF:", df.head(10))

        cursor.close()  # Fechar o cursor após a execução
        return df

    except Exception as e:
        print(f"Ocorreu um erro ao executar a consulta: {e}")
        return None  # Retornar None em caso de erro
