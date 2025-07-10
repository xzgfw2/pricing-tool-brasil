import os
from dotenv import load_dotenv
from databricks import sql
import pandas as pd
import polars as pl

load_dotenv()

def get_requests_for_approval_by_id(request_id):
    print("get_requests_for_approval_by_id")
    print("request_id", request_id)

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

        # Search through all tables for the request ID
        for table_name, config in APPROVAL_TABLE.items():
            # Determine which identifier column to use based on the table
            identifier = "hash_simulacao" if table_name == "price" else "uuid_alteracoes"
            
            # Query to find the request in the historic table
            cursor = connection.cursor()
            historic_query = f"SELECT * FROM {config['historic_table']} WHERE {identifier} = '{request_id}'"
            cursor.execute(historic_query)
            historic_result = cursor.fetchall()
            
            # If we found the request in the historic table
            if historic_result:
                print(f"Found request in {table_name} table")
                historic_columns = [desc[0] for desc in cursor.description]
                
                # Now get the corresponding data from the dump table
                dump_query = f"SELECT a.* FROM {config['dump_table']} a JOIN {config['historic_table']} b ON a.{identifier} = b.{identifier} WHERE b.{identifier} = '{request_id}'"
                cursor.execute(dump_query)
                dump_result = cursor.fetchall()
                
                if dump_result:
                    dump_columns = [desc[0] for desc in cursor.description]
                    
                    # Create the appropriate dataframe based on the table
                    if table_name == "buildup":
                        df = pl.DataFrame(dump_result, orient="row", schema=dump_columns)
                    else:
                        df = pd.DataFrame(dump_result, columns=dump_columns)
                    
                    # Add metadata about which table this came from
                    df['source_table'] = table_name
                    
                    print(f"Found data in {table_name} table")
                    print("df", df.head(10))
                    
                    cursor.close()
                    connection.close()
                    return df
        
        # If we got here, we didn't find the request in any table
        cursor.close()
        connection.close()
        print(f"No data found for request ID: {request_id}")
        return None

    except Exception as e:
        print(f"Erro ao buscar aprovações: {str(e)}")
        return None
