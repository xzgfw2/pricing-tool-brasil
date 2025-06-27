import json
import os
import requests
from dotenv import load_dotenv

load_dotenv()

def update_approval_status(data_variables):

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
    NOTEBOOK_PRICE_PATH = f'{BASE_NOTEBOOK_PATH}/proc_aprovar_arquitetura'
    NOTEBOOK_OTHERS_PATH = f'{BASE_NOTEBOOK_PATH}/proc_aprovar_configuracoes'

    NOTEBOOK_PATH = NOTEBOOK_PRICE_PATH if data_variables['target_table'] == "price" else NOTEBOOK_OTHERS_PATH

    TABLES = {
        "buildup": f"{BASE_NAME_DB}historico_buildup",
        "catlote": f"{BASE_NAME_DB}historico_catlote",
        "captain": f"{BASE_NAME_DB}historico_capitao",
        "captain_margin": f"{BASE_NAME_DB}historico_margem_do_capitao",
        "delta": f"{BASE_NAME_DB}historico_delta_preco",
        "marketing": f"{BASE_NAME_DB}historico_posicionamento_de_mercado",
        "price": f"{BASE_NAME_DB}historico_simulacoes",
        "optimization": f"{BASE_NAME_DB}historico_otimizacao",
        "strategy": f"{BASE_NAME_DB}historico_estrategia_comercial",
    }

    payload = {
        "existing_cluster_id": DB_CLUSTER_ID,
        "notebook_task": {
            "notebook_path": NOTEBOOK_PATH,
            "base_parameters": {
                'uuidAlteracoes': data_variables['uuid_alteracoes'],
                'statusAlteracoesId': data_variables['status'],
                'user_token': data_variables['user_token'],
                'targetTable': TABLES[data_variables['target_table']],
            }
        }
    }

    response = requests.post(
        ENDPOINT,
        headers=HEADERS,
        data=json.dumps(payload),
        timeout=120,
    )

    if response.status_code == 200: ### a API retorna 200 ou 401/403 no momento exato da requisicao, e nao para determinar sucesso na execucao ou nao
        run_id = response.json().get('run_id')
        print(f"Notebook initiated successfully. Run ID: {run_id}")

        # Polling the job run status
        job_status_endpoint = f'{DB_SERVER}/api/2.0/jobs/runs/get?run_id={run_id}'
        while True:
            job_status_response = requests.get(
                job_status_endpoint,
                headers=HEADERS,
                timeout=120,
            )
            job_status = job_status_response.json()
            if job_status['state']['life_cycle_state'] == 'TERMINATED':
                if job_status['state']['result_state'] == 'SUCCESS':
                    print("Notebook run completed successfully.")
                    output_endpoint = f'{DB_SERVER}/api/2.0/jobs/runs/get-output?run_id={run_id}'
                    output_response = requests.get(
                        output_endpoint,
                        headers=HEADERS,
                        timeout=120,
                    )
                    output = output_response.json()
                    log_json = output.get('notebook_output', {}).get('result')
                    print("Log JSON:", log_json)
                    print(output)
                else:
                    print("Notebook run failed.")
                break
            elif job_status['state']['life_cycle_state'] == 'INTERNAL_ERROR':
                print("Notebook run encountered an internal error.")
                break
            else:
                print("Notebook run is still in progress...")
    else:
        print(f"Failed to initiate notebook. Status Code: {response.status_code}")
        print("Response:", response.text)

    response.close()

    return True if job_status['state']['life_cycle_state'] == 'TERMINATED' and job_status['state']['result_state'] == 'SUCCESS' else False

