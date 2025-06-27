import os
from dotenv import load_dotenv
from databricks import sql
import pandas as pd
import polars as pl

load_dotenv()

def get_requests_for_approval_by_user(user_id):
    print("get_requests_for_approval_by_user")

    try:
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
            "optimization": {
                "dump_table": "maxis_sandbox.pricing_db.dump_otimizacao",
                "historic_table": "maxis_sandbox.pricing_db.historico_otimizacao"
            },
            "strategy": {
                "dump_table": "maxis_sandbox.pricing_db.dump_estrategia_comercial",
                "historic_table": "maxis_sandbox.pricing_db.historico_estrategia_comercial"
            },
            "captain": {
                "dump_table": "maxis_sandbox.pricing_db.dump_capitao",
                "historic_table": "maxis_sandbox.pricing_db.historico_capitao"
            },
            "price": {
                "dump_table": "maxis_sandbox.pricing_db.dump_simulacao",
                "historic_table": "maxis_sandbox.pricing_db.historico_simulacoes"
            },
        }

        union_queries = []
        for table_name, config in APPROVAL_TABLE.items():
            # Definir qual coluna usar para data_alteracoes
            data_column = "data_simulacao" if table_name == "captain" or table_name == "price" else "data_alteracoes"

            # Definir qual coluna usar para uuid_alteracoes
            uuid_column = "hash_simulacao" if table_name == "price" else "uuid_alteracoes"

            union_queries.append(f"""
                SELECT 
                    '{table_name}' as source_table,
                    id,
                    usuario_id,
                    {data_column} as data_alteracoes,
                    {uuid_column} as uuid_alteracoes,
                    status,
                    aprovadores_lista
                FROM {config['historic_table']}
                WHERE usuario_id = {user_id}
            """)

        full_query = " UNION ALL ".join(union_queries)

        cursor = connection.cursor()
        cursor.execute(full_query)

        result = cursor.fetchall()
        print("cursor.description", [desc[0] for desc in cursor.description])

        if not result:
            cursor.close()
            connection.close()
            return None

        # if table == "buildup":
        #     df = pl.DataFrame(result, orient="row", schema=[desc[0] for desc in cursor.description])
        # else:
        #     df = pd.DataFrame(result, columns=[desc[0] for desc in cursor.description])

        df = pd.DataFrame(result, columns=[desc[0] for desc in cursor.description])

        print("df", df.head(10))

        return df

    except Exception as e:
        print(f"Erro ao buscar aprovações: {str(e)}")
        return None
