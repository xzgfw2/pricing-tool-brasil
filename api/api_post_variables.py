import json
import os
import requests
from dotenv import load_dotenv

load_dotenv()

def post_variables(data_variables):
    print("post_variables")

    DB_SERVER = os.getenv('DB_SERVER')
    DB_TOKEN = os.getenv('DB_TOKEN')
    DB_CLUSTER_ID = os.getenv('DB_CLUSTER_ID')
    BASE_NOTEBOOK_PATH = os.getenv('BASE_NOTEBOOK_PATH')

    if not all([DB_SERVER, DB_TOKEN, DB_CLUSTER_ID]):
        raise ValueError("Uma ou mais variáveis de ambiente estão ausentes. Verifique seu arquivo .env.")

    ENDPOINT = f'{DB_SERVER}/api/2.0/jobs/runs/submit'

    HEADERS = {
        'Authorization': f'Bearer {DB_TOKEN}',
        'Content-Type': 'application/json'
    }

    BASE_NAME_DB = 'maxis_sandbox.pricing_db.'
    NOTEBOOK_PATH = f'{BASE_NOTEBOOK_PATH}/proc_atualizar_porcentagens'
    NOTEBOOK_PATH_MARCA_ELASTICIDADE = f'{BASE_NOTEBOOK_PATH}/proc_atualizar_porcentagens_marca_elasticidade'

    tables_parameters = {
        'marca': BASE_NAME_DB + 'var_marca_sim',
        'elasticidade': BASE_NAME_DB + 'var_elasticidade_sim',
        'frota': BASE_NAME_DB + 'var_frota_disponivel_sim',
        'ano frota': BASE_NAME_DB + 'var_ano_frota_sim',
        'aplicacoes': BASE_NAME_DB + 'var_aplicacoes_sim',
        'estoque': BASE_NAME_DB + 'var_meses_em_estoque_sim',
        'price index': BASE_NAME_DB + 'var_price_index_sim',
    }

    data_dict = json.loads(data_variables)

    for key, value in data_dict.items():

        notebook_path = NOTEBOOK_PATH_MARCA_ELASTICIDADE if key in ['marca', 'elasticidade'] else NOTEBOOK_PATH

        payload = {
            "run_name": f"Notebook Run for {key}",
            "existing_cluster_id": DB_CLUSTER_ID,
            "notebook_task": {
                "notebook_path": notebook_path,
                "base_parameters": {
                    'targetTable': tables_parameters[key],
                    'updateValues': json.dumps(value),
                }
            }
        }

        response = requests.post(
            ENDPOINT,
            headers=HEADERS,
            data=json.dumps(payload),
            timeout=120,
        )

        if response.status_code == 200:
            print(f"Notebook run for {key} initiated successfully.")
            print("Run ID:", response.json().get('run_id'))
        else:
            print(f"Failed to initiate notebook run for {key}. Status Code: {response.status_code}")
            print("Response:", response.text)

    response.close()

    return True
