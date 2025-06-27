import json
import os
import requests
from dotenv import load_dotenv
from utils.serialize_to_json import serialize_to_json

load_dotenv()

def update_optimization():
    print("update_optimization")
    
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
    

    NOTEBOOK_PATH = f'{BASE_NOTEBOOK_PATH}/proc_otimizacao'

    payload = {
        "existing_cluster_id": DB_CLUSTER_ID,
        "notebook_task": {
            "notebook_path": NOTEBOOK_PATH,
        }
    }

    response = requests.post(
        ENDPOINT,
        headers=HEADERS,
        data=json.dumps(payload),
        timeout=120,
    )

    print(response.json())

    if response.status_code == 200: ### a API retorna 200 ou 401/403 no momento exato da requisicao, e nao para determinar sucesso na execucao ou nao
        run_id = response.json().get('run_id')
        print(f"Notebook initiated successfully. Run ID: {run_id}")

        # # Polling the job run status
        # job_status_endpoint = f'{DB_SERVER}/api/2.0/jobs/runs/get?run_id={run_id}'
        # while True:
        #     job_status_response = requests.get(
        #         job_status_endpoint,
        #         headers=HEADERS,
        #         timeout=120,
        #     )
        #     job_status = job_status_response.json()
        #     if job_status['state']['life_cycle_state'] == 'TERMINATED':
        #         if job_status['state']['result_state'] == 'SUCCESS':
        #             print("Notebook run completed successfully.")
        #             output_endpoint = f'{DB_SERVER}/api/2.0/jobs/runs/get-output?run_id={run_id}'
        #             output_response = requests.get(
        #                 output_endpoint,
        #                 headers=HEADERS,
        #                 timeout=120,
        #             )
        #             output = output_response.json()
        #             log_json = output.get('notebook_output', {}).get('result')
        #             print("Log JSON:", log_json)
        #             print(output)
        #         else:
        #             print("Notebook run failed.")
        #         break
        #     elif job_status['state']['life_cycle_state'] == 'INTERNAL_ERROR':
        #         print("Notebook run encountered an internal error.")
        #         break
        #     else:
        #         print("Notebook run is still in progress...")
    else:
        print(f"Failed to initiate notebook. Status Code: {response.status_code}")
        print("Response:", response.text)

    response.close()

    return True