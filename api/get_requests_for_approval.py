import os
from dotenv import load_dotenv
from databricks import sql
import pandas as pd
import polars as pl

load_dotenv()

def get_requests_for_approval(table):
    print("get_requests_for_approval")
    print("table", table)

    try:
        allowed_values = [
            "buildup",
            "catlote",
            "captain",
            "captain_margin",
            "delta",
            "marketing",
            "price",
            "optimization",
            "strategy",
        ]

        if table not in allowed_values:
            raise ValueError(f"O parâmetro 'table' deve ser um dos seguintes: {allowed_values}")
        print(f"Valor aceito: {table}")

        DB_SERVER = os.getenv('DB_SERVER')
        DB_HTTP_PATH = os.getenv('DB_HTTP_PATH')
        DB_TOKEN = os.getenv('DB_TOKEN')

        connection = sql.connect(
            server_hostname = DB_SERVER,
            http_path = DB_HTTP_PATH,
            access_token = DB_TOKEN
        )

        APPROVAL_TABLE = {
            "buildup": {
                "dump_table": "maxis_sandbox.pricing_db.dump_buildup",
                "historic_table": "maxis_sandbox.pricing_db.historico_buildup"
            },
            "catlote": {
                "dump_table": "maxis_sandbox.pricing_db.dump_catlote",
                "historic_table": "maxis_sandbox.pricing_db.historico_catlote"
            },
            "captain": {
                "dump_table": "maxis_sandbox.pricing_db.dump_capitao",
                "historic_table": "maxis_sandbox.pricing_db.historico_capitao"
            },
            "captain_margin": {
                "dump_table": "maxis_sandbox.pricing_db.dump_margem_do_capitao",
                "historic_table": "maxis_sandbox.pricing_db.historico_margem_do_capitao"
            },
            "delta": {
                "dump_table": "maxis_sandbox.pricing_db.dump_delta_preco",
                "historic_table": "maxis_sandbox.pricing_db.historico_delta_preco"
            },
            "marketing": {
                "dump_table": "maxis_sandbox.pricing_db.dump_posicionamento_de_mercado",
                "historic_table": "maxis_sandbox.pricing_db.historico_posicionamento_de_mercado"
            },
            "price": {
                "dump_table": "maxis_sandbox.pricing_db.dump_simulacao",
                "historic_table": "maxis_sandbox.pricing_db.historico_simulacoes"
            },
            "optimization": {
                "dump_table": "maxis_sandbox.pricing_db.dump_otimizacao",
                "historic_table": "maxis_sandbox.pricing_db.historico_otimizacao"
            },
            "strategy": {
                "dump_table": "maxis_sandbox.pricing_db.dump_estrategia_comercial",
                "historic_table": "maxis_sandbox.pricing_db.historico_estrategia_comercial"
            },
        }

        identifier = "hash_simulacao" if table == "price" else "uuid_alteracoes"

        cursor = connection.cursor()
        cursor.execute(f"SELECT a.* FROM {APPROVAL_TABLE[table]['dump_table']} a LEFT JOIN {APPROVAL_TABLE[table]['historic_table']} b ON a.{identifier} = b.{identifier} WHERE b.status = 3")

        result = cursor.fetchall()
        print("cursor.description", [desc[0] for desc in cursor.description])

        if not result:
            cursor.close()
            connection.close()
            return None

        if table == "buildup":
            df = pl.DataFrame(result, orient="row", schema=[desc[0] for desc in cursor.description])
        else:
            df = pd.DataFrame(result, columns=[desc[0] for desc in cursor.description])

        print("table 123", table)
        print("df", df.head(10))

        return df

    except Exception as e:
        print(f"Erro ao buscar aprovações: {str(e)}")
        return None
