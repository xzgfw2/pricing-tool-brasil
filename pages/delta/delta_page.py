import pandas as pd
import gettext
import os
import dash_bootstrap_components as dbc
import dash_ag_grid as dag
from dash import html, callback, Input, Output, State, no_update, ctx
from translations import _, update_language
from pages.approvals.approval_utils import container_approval_reject_buttons
from api.get_initial_data_configs import get_initial_data_configs
from api.send_to_approval import send_to_approval
from api.get_requests_for_approval import get_requests_for_approval
from api.update_approval_status import update_approval_status
from utils.modify_column_if_other_column_changed import modify_column_if_other_column_changed
from utils.user_has_permission_to_edit import user_has_permission_to_edit
from static_data.helper_text import helper_text
from components.Helper_button_with_modal import create_help_button_with_modal
from components.Toast import Toast
from components.Modal import create_modal
from styles import CONTAINER_BUTTONS_STYLE, CONTAINER_TABLE_STYLE, CONTAINER_HELPER_BUTTON_STYLE, MAIN_TITLE_STYLE
from translations import _, setup_translations
from utils.handle_nothing_to_approve import handle_nothing_to_approve
from utils.handle_no_data_to_show import handle_no_data_to_show

def columns(pathname, user_data):
    return [
        {"headerName": _("CPC1_3_6"), "field": "cpc1_3_6"},
        {"headerName": _("Delta Preço Min."), "field": "dp_min", "editable": user_has_permission_to_edit(pathname, user_data)},
        {"headerName": _("Delta Preço Max."), "field": "dp_max", "editable": user_has_permission_to_edit(pathname, user_data)},
        {"headerName": _("Manual"), "field": "manual"},
    ]

def columns_approval():
    return [
        {"headerName": _("CPC1_3_6"), "field": "cpc1_3_6"},
        {"headerName": _("Delta Preço Min."), "field": "dp_min", "editable": False},
        {"headerName": _("Delta Preço Max."), "field": "dp_max", "editable": False},
        {"headerName": _("UUID Alteração"), "field": "uuid_alteracoes"},
        {"headerName": _("Status"), "field": "status"},
    ]

def create_approval_buttons(pathname, user_data):
    return html.Div(
            children=[
                dbc.Button(
                    _("Aprovar"),
                    id="button-approval-delta",
                    color="success",
                    disabled=True,
                    n_clicks=0,
                ),
                dbc.Tooltip(
                    _("Enviar para aprovação"),
                    target="button-approval-delta",
                    placement="top",
                ),
            ],
            style=CONTAINER_BUTTONS_STYLE
        )

def get_delta_data(cpc):
    table_data = get_initial_data_configs(process_name="delta", cpc=cpc)
    table_data["manual"] = ""
    return table_data

helper_button = html.Div(
    create_help_button_with_modal(
        modal_title=helper_text["delta"]["title"],
        modal_body=helper_text["delta"]["description"],
    ), style=CONTAINER_HELPER_BUTTON_STYLE,
)


def get_layout(pathname, user_data):
    cpc = user_data.get('cpc1_3_6_list')
    table_data = get_requests_for_approval(table="delta") if pathname == "/approval" else get_delta_data(cpc)

    table = handle_no_data_to_show(table_data.get("error")) if table_data.get("error") else dag.AgGrid(
        id='table-delta',
        rowData=table_data.to_dict("records") if table_data is not None else [],
        columnDefs=columns_approval() if pathname == "/approval" else columns(pathname, user_data),
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

    header = html.Div([
        html.H1(_('Delta Preço'), style=MAIN_TITLE_STYLE),
        helper_button
    ], className="container-title")

    container_change_approval = container_approval_reject_buttons(table="delta")
    container_send_approval = create_approval_buttons(pathname, user_data)

    toast_approval = Toast(
        id="toast-approval-delta",
        header=_("Aprovação"),
        toast_message=_("Enviado para aprovação"),
    )

    toast_reject = Toast(
        id="toast-approval-reject-delta",
    )

    container_table = html.Div(
        table,
        style=CONTAINER_TABLE_STYLE
    )

    return handle_nothing_to_approve() if table_data is None else html.Div([
        None if pathname == "/approval" else header,
        container_change_approval if pathname == "/approval" else container_send_approval,
        toast_approval,
        toast_reject,
        container_table,
    ])

modal_confirm_approval = create_modal(
    modal_id="modal-confirm-approval-delta",
    modal_title="Solicitar Aprovação",
    modal_body=html.P("Tem certeza que deseja enviar para aprovação?"),
    modal_footer=html.Div([
        dbc.Button("Não", id="btn-cancel-approval", color="secondary", className="me-2"),
        dbc.Button("Sim", id="btn-confirm-approval", color="success")
        ]),
    is_open=False
)

delta_page = html.Div([
    dbc.Spinner(
        html.Div(id="delta-content"),
        color="primary",
        size="lg",
        fullscreen=True,
    ),
    modal_confirm_approval,
])

@callback(
    Output("delta-content", "children"),
    [
        Input("url", "pathname"),
        Input("store-token", "data"),
        Input("store-language", "data"),
    ],
)
def update_delta_content(pathname, user_data, language):

    global _
    _ = setup_translations(language)

    if pathname in ["/delta", "/approval"]:
        return get_layout(pathname, user_data)
    return no_update

@callback(
    Output('table-delta', 'rowData'),
    Output('button-approval-delta', 'disabled'),
    Input('table-delta', 'cellValueChanged'),
    State('table-delta', 'rowData'),
    prevent_initial_call=True,
)
def update_cell_value(cellValueChanged, table_data):
    if cellValueChanged:
        updated_row_data = modify_column_if_other_column_changed(
            cellValueChanged,
            table_data,
            column_to_change="manual",
            value_to_input="1"
        )

        return updated_row_data, False
    return no_update, no_update

# Callback para abrir o modal de confirmação de aprovação
@callback(
    Output("modal-confirm-approval-delta", "is_open"),
    Input("button-approval-delta", "n_clicks"),
    prevent_initial_call=True,
)
def open_confirm_approval_modal(n_clicks):
    if n_clicks:
        return True
    return False

# Callback para processar a confirmação de aprovação
@callback(
    Output("modal-confirm-approval-delta", "is_open", allow_duplicate=True),
    Output("toast-approval-delta", "is_open", allow_duplicate=True),
    Input("btn-confirm-approval","n_clicks"),
    Input("btn-cancel-approval","n_clicks"),
    State("table-delta", "rowData"),
    State("store-token", "data"),
    prevent_initial_call=True,
)
def handle_send_approval(confirm_clicks, cancel_clicks, table_data, user_data):
    triggered_id = ctx.triggered_id

    if triggered_id == "btn-cancel-approval" and cancel_clicks:
        return False, False

    if triggered_id == "btn-confirm-approval" and confirm_clicks:

        df = pd.DataFrame(table_data)
        filtered_df = df.loc[df["manual"] == "1"]

        variables_to_send = {
            "user_token": user_data["access_token"],
            "table_data": filtered_df,
        }

        send_to_approval("delta", variables_to_send)

        return False, True
    return False, False

@callback(
    Output("toast-approval-reject-delta", "is_open"),
    Output("toast-approval-reject-delta", "header"),
    Output("toast-approval-reject-delta", "children"),
    Input("button-approval-accept-delta", "n_clicks"),
    Input("button-approval-reject-delta", "n_clicks"),
    State("table-delta", "rowData"),
    State("store-token", "data"),
    prevent_initial_call=True
)
def handle_approval(accept_clicks, reject_clicks, table_data, user_data):
    if not ctx.triggered_id:
        return no_update

    button_id = ctx.triggered_id
    status = "1" if "accept" in button_id else "2"
    status_text = "aprovado" if status == "1" else "recusado"

    if not table_data:
        return True, _("Erro"), _("Não há dados para aprovar/recusar")

    try:
        uuid_alteracoes = table_data[0]["uuid_alteracoes"]

        variables_to_send = {
            "uuid_alteracoes": uuid_alteracoes,
            "status": status,
            "user_token": user_data["access_token"],
            "target_table": "delta",
        }

        update_approval_status(variables_to_send)
        return True, status_text, _("Status alterado para {}").format(status_text)

    except Exception as e:
        print(f"Erro ao processar aprovação: {str(e)}")
        return True, _("Erro"), _("Erro ao processar aprovação: {}").format(str(e))
