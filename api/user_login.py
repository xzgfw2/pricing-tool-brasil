import json
import os
import requests
from dotenv import load_dotenv
import time

load_dotenv()

def user_login(data_variables):
    print("user_login")

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

    NOTEBOOK_PATH = f'{BASE_NOTEBOOK_PATH}/proc_login_user'

    data_dict = data_variables

    payload = {
        "existing_cluster_id": DB_CLUSTER_ID,
        "notebook_task": {
            "notebook_path": NOTEBOOK_PATH,
            "base_parameters": {
                'user_email': data_dict['user_email'],
                'user_password': data_dict['user_password'],
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
        run_id = response.json().get('run_id')
        print(f"Notebook run initiated successfully. Run ID: {run_id}")
    else:
        print(f"Failed to initiate notebook run. Status Code: {response.status_code}")
        print("Response:", response.text)
        return None

    # Aguardar a conclusão da execução do notebook
    ENDPOINT_RUN_STATUS = f'{DB_SERVER}/api/2.0/jobs/runs/get'
    while True:
        run_status_response = requests.get(
            ENDPOINT_RUN_STATUS,
            headers=HEADERS,
            params={'run_id': run_id},
            timeout=120,
        )
        run_status = run_status_response.json()
        if run_status['state']['life_cycle_state'] == 'TERMINATED':
            if run_status['state']['result_state'] == 'SUCCESS':
                break
            else:
                print(f"Notebook run failed. State: {run_status['state']['result_state']}")
                return None
        time.sleep(5)  # Esperar 5 segundos antes de verificar novamente

    # Buscar o resultado da execução do notebook
    ENDPOINT_RUN_OUTPUT = f'{DB_SERVER}/api/2.0/jobs/runs/get-output'
    run_output_response = requests.get(
        ENDPOINT_RUN_OUTPUT,
        headers=HEADERS,
        params={'run_id': run_id},
        timeout=120,
    )

    if run_output_response.status_code == 200:
        run_output = run_output_response.json()
        result = run_output.get('notebook_output', {}).get('result')
        if result:
            result_json = json.loads(result)
            print("Result:", result_json)
            return result_json
        else:
            print("No result found in notebook output.")
            return None
    else:
        print(f"Failed to get notebook output. Status Code: {run_output_response.status_code}")
        print("Response:", run_output_response.text)
        return None
