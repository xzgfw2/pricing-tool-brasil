import pandas as pd
import dash_ag_grid as dag
import dash_bootstrap_components as dbc
from dash import html, callback, Input, Output, State, no_update, ctx
from api.get_initial_data_configs import get_initial_data_configs
from api.send_to_approval import send_to_approval
from api.get_requests_for_approval import get_requests_for_approval
from api.update_approval_status import update_approval_status
from pages.approvals.approval_utils import container_approval_reject_buttons
from components.Helper_button_with_modal import create_help_button_with_modal
from components.Toast import Toast
from utils.modify_column_if_other_column_changed import modify_column_if_other_column_changed
from utils.handle_nothing_to_approve import handle_nothing_to_approve
from utils.user_has_permission_to_edit import user_has_permission_to_edit
from static_data.helper_text import helper_text
from styles import CONTAINER_BUTTONS_STYLE, CONTAINER_TABLE_STYLE, CONTAINER_HELPER_BUTTON_STYLE
from translations import _, setup_translations

def create_columns(pathname, user_data):
    return [
        {"headerName": "CPC1_3_6", "field": "cpc1_3_6" },
        {"headerName": "BuildUp Type", "field": "buildup_type" },
        {
            "headerName": "Genuine",
            "children": [
                {"headerName": "Mg Min", "field": "mg_min Genuine", "editable": user_has_permission_to_edit(pathname, user_data)},
                {"headerName": "Mg Max", "field": "mg_max Genuine", "editable": user_has_permission_to_edit(pathname, user_data)},
            ],
        },
        {
            "headerName": "ACDelco",
            "children": [
                {"headerName": "Mg Min", "field": "mg_min ACDelco", "editable": user_has_permission_to_edit(pathname, user_data)},
                {"headerName": "Mg Max", "field": "mg_max ACDelco", "editable": user_has_permission_to_edit(pathname, user_data)},
            ],
        },
        {
            "headerName": "ACDelco AM",
            "children": [
                {"headerName": "Mg Min", "field": "mg_min ACDelco AM", "editable": user_has_permission_to_edit(pathname, user_data)},
                {"headerName": "Mg Max", "field": "mg_max ACDelco AM", "editable": user_has_permission_to_edit(pathname, user_data)},
            ],
        },
        {
            "headerName": _("Acessórios"),
            "children": [
                {"headerName": "Mg Min", "field": "mg_min Acessorios", "editable": user_has_permission_to_edit(pathname, user_data)},
                {"headerName": "Mg Max", "field": "mg_max Acessorios", "editable": user_has_permission_to_edit(pathname, user_data)},
            ],
        },
        {"headerName": "Manual", "field": "manual"},
    ]

def columns_approval():
    return [
        {"headerName": "CPC1_3_6", "field": "cpc1_3_6" },
        {"headerName": _("BuildUp Type"), "field": "buildup_type" },
        {
            "headerName": "Genuine",
            "children": [
                {"headerName": _("Mg Min"), "field": "mg_min Genuine", "editable": False},
                {"headerName": _("Mg Max"), "field": "mg_max Genuine", "editable": False},
            ],
        },
        {
            "headerName": "ACDelco",
            "children": [
                {"headerName": _("Mg Min"), "field": "mg_min ACDelco", "editable": False},
                {"headerName": _("Mg Max"), "field": "mg_max ACDelco", "editable": False},
            ],
        },
        {
            "headerName": "ACDelco AM",
            "children": [
                {"headerName": _("Mg Min"), "field": "mg_min ACDelco AM", "editable": False},
                {"headerName": _("Mg Max"), "field": "mg_max ACDelco AM", "editable": False},
            ],
        },
        {
            "headerName": _("Acessórios"),
            "children": [
                {"headerName": _("Mg Min"), "field": "mg_min Acessorios", "editable": False},
                {"headerName": _("Mg Max"), "field": "mg_max Acessorios", "editable": False},
            ],
        },
        {"headerName": _("UUID Alteração"), "field": "uuid_alteracoes"}, # temporário para testes
        {"headerName": _("Status"), "field": "status"}, # temporário para testes
        {"headerName": _("Manual"), "field": "manual"},
    ]

def create_mg_columns(df):
    df_pivot = df.pivot_table(
        index=['cpc1_3_6', 'buildup_type'],
        columns='marca',
        values=['mg_min', 'mg_max'],
        aggfunc='first'
    )

    # Ajustar os nomes das colunas
    df_pivot.columns = [f"{stat} {brand}" for stat, brand in df_pivot.columns]
    df_pivot = df_pivot.reset_index()

    # Verifica se 'status' e 'uuid' estão no DataFrame antes de tentar adicioná-los
    columns_to_merge = [col for col in ['status', 'uuid_alteracoes'] if col in df.columns]

    if columns_to_merge:
        df_status = df[['cpc1_3_6', 'buildup_type'] + columns_to_merge].drop_duplicates()
        df_pivot = df_pivot.merge(df_status, on=['cpc1_3_6', 'buildup_type'], how='left')

    return df_pivot


def get_layout(pathname, user_data):

    cpc = user_data.get('cpc1_3_6_list')

    table_data = get_requests_for_approval(table="captain_margin") if pathname == "/approval" else get_initial_data_configs(process_name="captain_margin", cpc=cpc)

    formated_table = None
    none_table = None

    if table_data is None:
        none_table = handle_nothing_to_approve()
    else:
        formated_table = create_mg_columns(table_data)

    table = dag.AgGrid(
        id='table-captain-margin',
        rowData=None if table_data is None else formated_table.to_dict("records"),
        columnDefs=columns_approval() if pathname == "/approval" else create_columns(pathname, user_data),
        columnSize="responsiveSizeToFit",
        defaultColDef={
            "sortable": True,
            "filter": True,
            "resizable": True,
            "singleClickEdit": True,
        },
        dashGridOptions={
            "pagination": True,
            "paginationPageSize": 10,
        },
        style={'height': '500px'},
    )

    return handle_nothing_to_approve() if table_data is None else [
        None if pathname == "/approval" else html.Div(
            [
                html.Div(className="flexible-spacer"),
                create_help_button_with_modal(
                    modal_title=helper_text["captain_margin"]["title"],
                    modal_body=helper_text["captain_margin"]["description"],
                ),
            ], style=CONTAINER_HELPER_BUTTON_STYLE,
        ),
        container_approval_reject_buttons(table="captain-margin") if pathname == "/approval" else html.Div(
            children=[
                dbc.Button(
                    _("Aprovar"),
                    id="button-approval-captain-margin",
                    color="success",
                    disabled=True,
                    n_clicks=0
                ),
                dbc.Tooltip(
                    _("Enviar para aprovação"),
                    target="button-approval-captain-margin",
                    placement="top",
                ),
            ],
            style=CONTAINER_BUTTONS_STYLE,
        ),
        Toast(id="toast-approval-captain-margin"),
        html.Div(
            table,
            style=CONTAINER_TABLE_STYLE
        )
    ]

captain_margin_page = html.Div([
    dbc.Spinner(
        html.Div(id="captain-margin-content"),
        color="primary",
        size="lg",
        fullscreen=True,
    )
])

@callback(
    Output("captain-margin-content", "children"),
    [
        Input("url", "pathname"),
        Input("store-token", "data"),
        Input("store-language", "data"),
    ],
)
def update_captain_margin_content(pathname, user_data, language):

    global _
    _ = setup_translations(language)

    if pathname in ["/captain-margin", "/approval"]:
        return get_layout(pathname, user_data)
    return no_update

# Callback para atualizar a tabela, habilitar botão de aprovação e envio dos dados para o back-end
@callback(
    Output('table-captain-margin', 'rowData'),
    Output('button-approval-captain-margin', 'disabled'),
    Input('table-captain-margin', 'cellValueChanged'),
    Input('button-approval-captain-margin', 'n_clicks'),
    State('table-captain-margin', 'rowData'),
    State("store-token", "data"),
    prevent_initial_call=True,
)
def update_cell_value(cellValueChanged, n_clicks, row_data, user_data):
    if cellValueChanged:

        updated_row_data = modify_column_if_other_column_changed(
            cellValueChanged,
            row_data,
            column_to_change="manual",
            value_to_input="1"
        )

        if n_clicks > 0:

            df = pd.DataFrame(row_data)
            filtered_df = df.loc[df["manual"] == "1"]
            transformed_df = transform_filtered_data(filtered_df)

            variables_to_send = {
                "user_token": user_data["access_token"],
                "table_data": transformed_df,
            }

            send_to_approval("captain_margin", variables_to_send)

        return updated_row_data, False
    return no_update, no_update

def transform_filtered_data(filtered_df):
    """
    Transform filtered DataFrame from wide format to long format with columns 
    ['marca', 'cpc1_3_6', 'buildup_type', 'mg_min', 'mg_max']
    """
    transformed_data = []
    brands = ['ACDelco', 'ACDelco AM', 'Acessorios', 'Genuine']
    
    for _, row in filtered_df.iterrows():
        for brand in brands:
            transformed_row = {
                'marca': brand,
                'cpc1_3_6': row['cpc1_3_6'],
                'buildup_type': row['buildup_type'],
                'mg_min': row[f'mg_min {brand}'],
                'mg_max': row[f'mg_max {brand}']
            }
            transformed_data.append(transformed_row)
    
    return pd.DataFrame(transformed_data)


# Callback para aprovação/rejeição
@callback(
    Output("toast-approval-captain-margin", "is_open"),
    Output("toast-approval-captain-margin", "header"),
    Output("toast-approval-captain-margin", "children"),
    Input("button-approval-accept-captain-margin", "n_clicks"),
    Input("button-approval-reject-captain-margin", "n_clicks"),
    State("table-captain-margin", "rowData"),
    State("store-token", "data"),
    prevent_initial_call=True
)
def handle_approval(accept_clicks, reject_clicks, table_data, user_data):
    if not ctx.triggered_id:
        return no_update

    print("handle_approval")

    button_id = ctx.triggered_id
    status = "1" if "accept" in button_id else "2"
    status_text = "aprovado" if status == "1" else "recusado"

    if not table_data:
        return html.P("Erro: Não há dados para aprovar/recusar",className="message-danger")

    try:
        uuid_alteracoes = table_data[0]["uuid_alteracoes"]

        variables_to_send = {
            "uuid_alteracoes": uuid_alteracoes,
            "status": status,
            "user_token": user_data["access_token"],
            "target_table": "captain_margin",
        }

        update_approval_status(variables_to_send)
        return True, f"{status_text}", f"Status alterado para {status_text}"

    except Exception as e:
        print(f"Erro ao processar aprovação: {str(e)}")
        return True, "Erro", f"Erro ao processar aprovação: {str(e)}"
