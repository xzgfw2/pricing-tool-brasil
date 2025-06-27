import json
import os
import requests
from dotenv import load_dotenv
from utils.serialize_to_json import serialize_to_json

load_dotenv()

def send_to_approval(notebook_name, data_variables):
    print(f"send_{notebook_name}_to_approval")

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


    handler = {
        'buildup': {
            "table_name": "buildup",
            "notebook_path_end": "proc_receber_buildup",
            "output_key": "outputBuildUp",
        },
        'captain': {
            "table_name": "captain",
            "notebook_path_end": "proc_receber_simulacao_capitao",
            "output_key": "simulationOutput",
        },
        'captain_margin': {
            "table_name": "captain_margin",
            "notebook_path_end": "proc_receber_margem_do_capitao",
            "output_key": "outputMargemDoCapitao",
        },
        'catlote': {
            "table_name": "catlote",
            "notebook_path_end": "proc_receber_catlote",
            "output_key": "outputCatlote",
        },
        'delta': {
            "table_name": 'delta_preco',
            "notebook_path_end": "proc_receber_delta_preco",
            "output_key": "outputDeltaPreco",
        },
        'marketing': {
            "table_name": "marketing",
            "notebook_path_end": "proc_receber_posicionamento_de_mercado",
            "output_key": "outputPosicionamentoDeMercado",
        },
        'optimization': {
            "table_name": "optimization",
            "notebook_path_end": "proc_receber_otimizacao",
            "output_key": "outputOptimization",
        },
        'price_simulation': {
            "table_name": "price_simulation",
            "notebook_path_end": "proc_enviar_simulacao_para_aprovacao",
            "output_key": "uuidAlteracoes",
        },
        'strategy': {
            "table_name": "strategy",
            "notebook_path_end": "proc_receber_estrategia_comercial",
            "output_key": "outputEstrategiaComercial",
        },
    }

    NOTEBOOK_PATH = f'{BASE_NOTEBOOK_PATH}/{handler[notebook_name]["notebook_path_end"]}'
    output_key = handler[notebook_name]["output_key"]

    payload = {
        "existing_cluster_id": DB_CLUSTER_ID,
        "notebook_task": {
            "notebook_path": NOTEBOOK_PATH,
            "base_parameters": {
                'user_token': data_variables['user_token'],
                output_key: data_variables['uuid_alteracoes'] if notebook_name == "price_simulation" else serialize_to_json(data_variables['table_data']),
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
