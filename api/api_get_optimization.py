"""Módulo de conexão com o Databricks para trazer dados do banco de dados"""

import os
import platform
import pathlib
import time
from datetime import datetime
import polars as pl
from dotenv import load_dotenv
from databricks import sql

load_dotenv()

def get_cache_path():
    """Retorna o caminho do arquivo de cache"""

    current_dir = pathlib.Path(__file__).parent
    cache_dir = current_dir / "cache"
    cache_dir.mkdir(exist_ok=True)

    return cache_dir / "optimization_cache.parquet"

def is_cache_valid():
    """Verifica se o cache é válido (do mesmo dia)"""

    cache_path = get_cache_path()
    if not cache_path.exists():
        return False

    file_date = ""
    stat = os.stat(cache_path)

    if platform.system() == 'Windows':
        file_date = datetime.fromtimestamp(stat.st_ctime).date()
    else:
        # Fallback no Linux: usar o st_mtime (modificação) como estimativa
        file_date = datetime.fromtimestamp(stat.st_mtime).date()
    now = datetime.now().date()
    return file_date == now

def get_optimization(cpc=None):
    """Conecta ao Databricks e retorna os produtos da tabela d_otimizacao.

    Esta função primeiro verifica se existe um cache válido do dia atual.
    Se existir, retorna os dados do cache. Caso contrário, busca os dados
    do Databricks e cria um novo cache.

    Returns:
        pl.DataFrame: Um DataFrame (do Polars) contendo os produtos da tabela d_otimizacao.

    Raises:
        EnvironmentError: Se as variáveis de ambiente não estiverem configuradas corretamente.
        ValueError: Se a consulta ao banco de dados retornar resultados vazios.
        ConnectionError: Se houver um erro na conexão ao banco de dados ou na execução da consulta.
    """

    start_time = time.time()
    print("Iniciando get_optimization...")
    
    cache_path = get_cache_path()
    
    # Tenta usar o cache se for válido
    if is_cache_valid():
        try:
            print("Usando cache de produtos...")
            df = pl.read_parquet(cache_path)
            end_time = time.time()
            print(f"Tempo total (cache): {end_time - start_time:.2f} segundos")
            return df
        except Exception as e:
            print(f"Erro ao ler cache: {e}")
            # Se houver erro na leitura do cache, continua para buscar dados novos
    
    # Se não há cache válido, busca dados do Databricks
    print("Buscando dados do Databricks...")

    base_name_db = 'maxis_sandbox.pricing_db.d_otimizacao'

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
                query_start = time.time()

                print("cpc", cpc)

                if cpc in (None, []):
                    cursor.execute(f"SELECT * from {base_name_db} WHERE status <> 'algoritmo - garantia/reman' AND record_sales = 'yes'")
                else:
                    cpc_filter = "', '".join(cpc)
                    cursor.execute(f"SELECT * from {base_name_db} WHERE status <> 'algoritmo - garantia/reman' AND record_sales = 'yes' AND cpc1_3_6 IN ('{cpc_filter}')")

                result = cursor.fetchall()
                query_end = time.time()
                print(f"Tempo da query: {query_end - query_start:.2f} segundos")

                if not result:
                    raise ValueError("Erro: A consulta retornou resultados vazios.")

                df = pl.DataFrame(result, orient="row", schema=[desc[0] for desc in cursor.description])
                df.with_row_index()

                # Salva o resultado no cache
                try:
                    cache_start = time.time()
                    df.write_parquet(cache_path)
                    cache_end = time.time()
                    print(f"Tempo para salvar cache: {cache_end - cache_start:.2f} segundos")
                    print("Cache atualizado com sucesso")
                except Exception as e:
                    print(f"Erro ao salvar cache: {e}")
                    # Mesmo se falhar ao salvar o cache, retorna os dados obtidos

                cursor.close()
                connection.close()

    except Exception as e:
        raise ConnectionError(f"Erro ao conectar ou executar a query: {str(e)}") from e

    end_time = time.time()
    print(f"Tempo total (dados novos): {end_time - start_time:.2f} segundos")
    return df
