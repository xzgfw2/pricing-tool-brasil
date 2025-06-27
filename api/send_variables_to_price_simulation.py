import os
import json
import requests
from dotenv import load_dotenv
from utils.serialize_to_json import serialize_to_json

load_dotenv()

def send_variables_to_price_simulation(data_variables):

    DB_SERVER = os.getenv('DB_SERVER')
    JOB_ID = os.getenv('JOB_ID')
    DB_TOKEN = os.getenv('DB_TOKEN')

    HEADERS = {
        'Authorization': f'Bearer {DB_TOKEN}',
        'Content-Type': 'application/json',
    }

    params = {
        "user_token": serialize_to_json(data_variables.get("user_token", "")),
        "alteracoes_marca": serialize_to_json(data_variables.get("table_data", {}).get("marca", "")),
        "alteracoes_elasticidade": serialize_to_json(data_variables.get("table_data", {}).get("elasticidade", "")),
        "alteracoes_ano_frota": serialize_to_json(data_variables.get("table_data", {}).get("ano frota", "")),
        "alteracoes_frota_disponivel": serialize_to_json(data_variables.get("table_data", {}).get("frota", "")),
        "alteracoes_meses_em_estoque": serialize_to_json(data_variables.get("table_data", {}).get("estoque", "")),
        # Não permitir o envio do price index, será somente visualização, embora o back-end esteja preparado para aceitar esse parâmetro
        # "alteracoes_price_index": serialize_to_json(data_variables.get("table_data", {}).get("price index", "")),
        "alteracoes_aplicacoes": serialize_to_json(data_variables.get("table_data", {}).get("aplicacoes", "")),
    }

    response = requests.post(
        f"{DB_SERVER}/api/2.0/jobs/run-now",
        headers=HEADERS,
        json={
            "job_id": JOB_ID,
            "notebook_params": params
        },
        timeout=300,
    )

    if response.status_code == 200:
        run_id = response.json().get('run_id')
        print(f"Notebook initiated successfully. Run ID: {run_id}")

        job_status_endpoint = f'{DB_SERVER}/api/2.0/jobs/runs/get?run_id={run_id}'

        while True:
            job_status_response = requests.get(
                job_status_endpoint,
                headers=HEADERS,
                timeout=120,
            )

            job_status = job_status_response.json()
            print("job_status", job_status)

            if job_status['state']['life_cycle_state'] == 'TERMINATED':
                if job_status['state']['result_state'] == 'SUCCESS':
                    print("Notebook run completed successfully.")
                    
                    # Retrieve the list of tasks
                    tasks = job_status.get('tasks', [])
                    for task in tasks:
                        task_run_id = task.get('run_id')
                        output_endpoint = f'{DB_SERVER}/api/2.0/jobs/runs/get-output?run_id={task_run_id}'
                        output_response = requests.get(
                            output_endpoint,
                            headers=HEADERS,
                            timeout=120,
                        )
                        output = output_response.json()
                        log_json = output.get('notebook_output', {}).get('result')
                        print(f"Log JSON for task {task_run_id}:", log_json)
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
        print("Falha ao acionar o job. Código de status:", response.status_code)

    response.close()

    return True if job_status['state']['life_cycle_state'] == 'TERMINATED' and job_status['state']['result_state'] == 'SUCCESS' else False
