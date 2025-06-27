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
from styles import CONTAINER_BUTTONS_STYLE, CONTAINER_TABLE_STYLE, CONTAINER_HELPER_BUTTON_STYLE
from translations import _, setup_translations
from utils.handle_nothing_to_approve import handle_nothing_to_approve

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

def get_delta_data(cpc):
    table_data = get_initial_data_configs(process_name="delta", cpc=cpc)
    table_data["manual"] = ""
    return table_data

def get_layout(pathname, user_data):
    cpc = user_data.get('cpc1_3_6_list')
    table_data = get_requests_for_approval(table="delta") if pathname == "/approval" else get_delta_data(cpc)

    table = dag.AgGrid(
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

    return handle_nothing_to_approve() if table_data is None else [
        None if pathname == "/approval" else html.Div(
            [
                html.Div(className="flexible-spacer"),
                create_help_button_with_modal(
                    modal_title=helper_text["delta"]["title"],
                    modal_body=helper_text["delta"]["description"],
                ),
            ], style=CONTAINER_HELPER_BUTTON_STYLE,
        ),
        container_approval_reject_buttons(table="delta") if pathname == "/approval" else html.Div(
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
        ),
        Toast(id="toast-approval-delta"),
        html.Div(
            table,
            style=CONTAINER_TABLE_STYLE
        ),
    ]

delta_page = html.Div([
    dbc.Spinner(
        html.Div(id="delta-content"),
        color="primary",
        size="lg",
        fullscreen=True,
    )
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
    Input('button-approval-delta', 'n_clicks'),
    State('table-delta', 'rowData'),
    State("store-token", "data"),
    prevent_initial_call=True,
)
def update_cell_value(cellValueChanged, n_clicks, table_data, user_data):
    if cellValueChanged:
        updated_row_data = modify_column_if_other_column_changed(
            cellValueChanged,
            table_data,
            column_to_change="manual",
            value_to_input="1"
        )

        if n_clicks > 0:
            df = pd.DataFrame(table_data)
            filtered_df = df.loc[df["manual"] == "1"]

            variables_to_send = {
                "user_token": user_data["access_token"],
                "table_data": filtered_df,
            }

            send_to_approval("delta", variables_to_send)

        return updated_row_data, False
    return no_update, no_update

@callback(
    Output("toast-approval-delta", "is_open"),
    Output("toast-approval-delta", "header"),
    Output("toast-approval-delta", "children"),
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
