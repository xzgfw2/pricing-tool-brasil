import os
import asyncio
from dotenv import load_dotenv
from databricks import sql
import pandas as pd
from concurrent.futures import ThreadPoolExecutor

load_dotenv()

def select_table(selected_table):
    base = {
        "zero_cost": 'maxis_sandbox.pricing_db.cc_custo_zerado',
        "negative_cost": 'maxis_sandbox.pricing_db.cc_custo_negativo',
        "low_cost_high_margin": 'maxis_sandbox.pricing_db.cc_baixo_custo_mg_alta',
        "low_cost_negative_margin": 'maxis_sandbox.pricing_db.cc_baixo_custo_mg_negativa',
        "low_cost_zero_margin": 'maxis_sandbox.pricing_db.cc_baixo_custo_mg_zerada',
        "low_cost_high_sales": 'maxis_sandbox.pricing_db.cc_baixo_custo_venda_alta',
        "low_price_negative_margin": 'maxis_sandbox.pricing_db.cc_baixo_preco_mg_negativa',
        "negative_margin_and_others": 'maxis_sandbox.pricing_db.cc_mg_negativa_outros_casos',
        "price_gm": 'maxis_sandbox.pricing_db.cc_preco_gm',
        "price_research": 'maxis_sandbox.pricing_db.cc_preco_pesquisa',
        "update_cpc": 'maxis_sandbox.pricing_db.cc_atualizar_cpc',
    }
    return base[selected_table]

def get_data_for_table(selected_table):
    """Execute a single database query"""
    DB_SERVER = os.getenv('DB_SERVER')
    DB_HTTP_PATH = os.getenv('DB_HTTP_PATH')
    DB_TOKEN = os.getenv('DB_TOKEN')

    connection = sql.connect(
        server_hostname=DB_SERVER,
        http_path=DB_HTTP_PATH,
        access_token=DB_TOKEN
    )

    cursor = connection.cursor()
    cursor.execute(f"SELECT * from {select_table(selected_table)}")

    result = cursor.fetchall()
    df = pd.DataFrame(result, columns=[desc[0] for desc in cursor.description])

    cursor.close()
    connection.close()

    return selected_table, df

async def get_command_center_async(table_names):
    print("table_names", table_names)

    """
    Fetch data for multiple tables concurrently using a thread pool
    """
    with ThreadPoolExecutor(max_workers=11) as executor:
        loop = asyncio.get_event_loop()
        futures = [
            loop.run_in_executor(executor, get_data_for_table, table_name)
            for table_name in table_names
        ]
        results = await asyncio.gather(*futures)
        return dict(results)

def get_all_command_center_data():
    """
    Synchronous wrapper for getting all command center data
    """
    table_names = [
        "zero_cost",
        "negative_cost",
        "low_cost_high_margin",
        "low_cost_negative_margin",
        "low_cost_zero_margin",
        "low_cost_high_sales",
        "low_price_negative_margin",
        "negative_margin_and_others",
        "price_gm",
        "price_research",
        "update_cpc"
    ]
    
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        return loop.run_until_complete(get_command_center_async(table_names))
    finally:
        loop.close()
