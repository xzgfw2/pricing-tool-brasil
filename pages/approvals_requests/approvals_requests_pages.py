import dash_bootstrap_components as dbc
import pandas as pd
from dash import html, Input, Output, State, callback
from components.Table_plain import create_table_plain
from components.Modal import create_modal
# from components.Table import create_table
from api.get_requests_for_approval_by_user import get_requests_for_approval_by_user
from components.Helper_button_with_modal import create_help_button_with_modal
from static_data.helper_text import helper_text
from styles import MAIN_TITLE_STYLE, CONTAINER_HELPER_BUTTON_STYLE
from translations import _, setup_translations
from utils.handle_no_data_to_show import handle_no_data_to_show

# details_data = [
#     {"cpc1_3_6": "123456", "dp_min": "10%", "dp_max": "20%", "uuid_alteracoes": 1 },
#     {"cpc1_3_6": "234567", "dp_min": "15%", "dp_max": "25%", "uuid_alteracoes": 2 },
#     {"cpc1_3_6": "345678", "dp_min": "8%", "dp_max": "18%", "uuid_alteracoes": 3 },
#     {"cpc1_3_6": "456789", "dp_min": "12%", "dp_max": "22%", "uuid_alteracoes": 4 },
#     {"cpc1_3_6": "567890", "dp_min": "5%", "dp_max": "15%", "uuid_alteracoes": 5 },
#     {"cpc1_3_6": "678901", "dp_min": "20%", "dp_max": "30%", "uuid_alteracoes": 6 },
#     {"cpc1_3_6": "789012", "dp_min": "7%", "dp_max": "17%", "uuid_alteracoes": 7 },
#     {"cpc1_3_6": "890123", "dp_min": "13%", "dp_max": "23%", "uuid_alteracoes": 8 },
#     {"cpc1_3_6": "901234", "dp_min": "9%", "dp_max": "19%", "uuid_alteracoes": 9 },
#     {"cpc1_3_6": "012345", "dp_min": "11%", "dp_max": "21%", "uuid_alteracoes": 10 },
#     {"cpc1_3_6": "123457", "dp_min": "14%", "dp_max": "24%", "uuid_alteracoes": 11 },
#     {"cpc1_3_6": "234568", "dp_min": "6%", "dp_max": "16%", "uuid_alteracoes": 12 },
#     {"cpc1_3_6": "345679", "dp_min": "16%", "dp_max": "26%", "uuid_alteracoes": 13 },
#     {"cpc1_3_6": "456780", "dp_min": "8%", "dp_max": "18%", "uuid_alteracoes": 14 },
#     {"cpc1_3_6": "567891", "dp_min": "17%", "dp_max": "27%", "uuid_alteracoes": 15 },
#     {"cpc1_3_6": "678902", "dp_min": "10%", "dp_max": "20%", "uuid_alteracoes": 16 },
#     {"cpc1_3_6": "789013", "dp_min": "12%", "dp_max": "22%", "uuid_alteracoes": 17 },
#     {"cpc1_3_6": "890124", "dp_min": "15%", "dp_max": "25%", "uuid_alteracoes": 18 },
#     {"cpc1_3_6": "901235", "dp_min": "9%", "dp_max": "19%", "uuid_alteracoes": 19 },
#     {"cpc1_3_6": "012346", "dp_min": "13%", "dp_max": "23%", "uuid_alteracoes": 20 },
#     {"cpc1_3_6": "123458", "dp_min": "11%", "dp_max": "21%", "uuid_alteracoes": 21 },
# ]

helper_button = html.Div(
    create_help_button_with_modal(
        modal_title=helper_text["approvals_requests"]["title"],
        modal_body=helper_text["approvals_requests"]["description"],
    ), style=CONTAINER_HELPER_BUTTON_STYLE,
)

def columns_approval():
    return [
        {"headerName": "CPC1_3_6", "field": "cpc1_3_6"},
        {"headerName": "Delta Preço Min.", "field": "dp_min"},
        {"headerName": "Delta Preço Max.", "field": "dp_max"},
        {"headerName": "UUID Alteração", "field": "uuid_alteracoes"}
    ]

def get_table_data(user_data):

    user_id = user_data.get('id') # caso queira visualizar um exemplo temporario mude para "123"

    df = get_requests_for_approval_by_user(user_id)

    if df is None:
        return []
    else:
        df['aprovadores_lista'] = df['aprovadores_lista'].apply(lambda x: ', '.join(x) if isinstance(x, list) else str(x))

    df['data_alteracoes'] = pd.to_datetime(df['data_alteracoes'])
    df['data_alteracoes_data'] = df['data_alteracoes'].dt.strftime('%d/%m/%Y')
    df['data_alteracoes_hora'] = df['data_alteracoes'].dt.strftime('%H:%M')

    status_map = {
        1: "Aprovado",
        2: "Reprovado",
        3: "Pendente"
    }
    df['status'] = df['status'].map(status_map).fillna(df['status'])

    return df.to_dict('records')

columns = [
    {"name": "Data", "id": "data_alteracoes_data"},
    {"name": "Hora", "id": "data_alteracoes_hora"},
    {"name": "Status", "id": "status"},
    {"name": "Processo", "id": "source_table"},
    {"name": "ID Requisição", "id": "uuid_alteracoes"},
]

modal = create_modal(
    modal_id="produto-modal",
    modal_title="Detalhes da Solicitação",
    modal_body_id="produto-modal-body",
    modal_footer_id="produto-modal-footer",
    modal_body="",
    modal_footer="",
    size="xl",
)

no_data = handle_no_data_to_show(message="Nenhuma requisição encontrada para este usuário")

def get_layout(user_data):

    data = get_table_data(user_data)

    table = html.Div([
        create_table_plain(
            data=data,
            columns=columns,
            table_id="approval-requests-table"
        ),
        modal
    ], style={'margin': '20px'})

    return html.Div([
        html.Div([
            html.H1(_("Requisições de Aprovação"), style=MAIN_TITLE_STYLE),
            helper_button
        ], className="container-title"),
        table if data else no_data,
    ])

approval_requests_page = html.Div([
    dbc.Spinner(
        html.Div(id="approval-requests-content"),
        color="primary",
        size="lg",
        fullscreen=True,
    )
])

@callback(
    Output("approval-requests-content", "children"),
    [
        Input("store-token", "data"),
        Input("store-language", "data"),
    ],
)
def update_marketing_content(user_data, language):

    global _
    _ = setup_translations(language)

    return get_layout(user_data)

# @callback(
#     Output("produto-modal", "is_open"),
#     Output("produto-modal-body", "children"),
#     Input("approval-requests-table", "active_cell"),
#     Input("approval-requests-table", "selected_cells"),
#     State("approval-requests-table", "data"),
# )
# def open_modal_on_click(active_cell, selected_cells, table_data):
#     if active_cell and table_data:
#         col = active_cell.get("column_id")
        
#         if col == "detalhes":
#             details = html.Div([
#                 create_table(
#                     table_id="approval-details-table",
#                     row_data=details_data,
#                     column_size="sizeToFit",
#                     column_defs=columns_approval(),
#                     style={'height': '500px', 'width': '100%'}
#                 ),
#             ])
#             return True, details
#     return False, None
