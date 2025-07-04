import pandas as pd
import dash_bootstrap_components as dbc
import dash_ag_grid as dag
from dash import html, callback, Input, Output, State, no_update, ctx
from pages.approvals.approval_utils import container_approval_reject_buttons
from api.get_initial_data_configs import get_initial_data_configs
from api.send_to_approval import send_to_approval
from api.get_requests_for_approval import get_requests_for_approval
from api.update_approval_status import update_approval_status
from utils.modify_column_if_other_column_changed import modify_column_if_other_column_changed
from utils.handle_no_data_to_show import handle_no_data_to_show
from static_data.helper_text import helper_text
from components.Toast import Toast
from components.Helper_button_with_modal import create_help_button_with_modal
from utils.user_has_permission_to_edit import user_has_permission_to_edit
from utils.handle_nothing_to_approve import handle_nothing_to_approve
from styles import CONTAINER_BUTTONS_STYLE, CONTAINER_TABLE_STYLE, CONTAINER_HELPER_BUTTON_STYLE
from translations import _, setup_translations

def create_columns(pathname, user_data):
    return [
        {"headerName": _("CPC1_3_6"), "field": "cpc1_3_6"},
        {"headerName": _("Peça"), "field": "peca"},
        {"headerName": _("Marca"), "field": "marca"},
        {"headerName": _("Preço Concorrente Distribuidor"), "field": "preco_concorrente_distribuidor"},
        {"headerName": _("Preço Dealer GM"), "field": "preco_dealer_gm"},
        {"headerName": _("Price Index Distribuidor (AS IS)"), "field": "price_index_distribuidor"},
        {"headerName": _("Meta Competitividade (TO BE)"), "field": "meta_competitividade", "editable": user_has_permission_to_edit(pathname, user_data)},
        {
            "headerName": _("Ativo"), 
            "field": "ativo", 
            "type": "numericColumn", 
            "editable": user_has_permission_to_edit(pathname, user_data),
            "cellEditor": "agSelectCellEditor",
            "cellEditorParams": {
                "values": [0, 1]
            },
        },
        {"headerName": _("Manual"), "field": "manual"},
    ]

def columns_approval():
    return [
        {"headerName": _("CPC1_3_6"), "field": "cpc1_3_6"},
        {"headerName": _("Peça"), "field": "peca"},
        {"headerName": _("Marca"), "field": "marca"},
        {"headerName": _("Preço Concorrente Distribuidor"), "field": "preco_concorrente_distribuidor"},
        {"headerName": _("Preço Dealer GM"), "field": "preco_dealer_gm"},
        {"headerName": _("Price Index Distribuidor (AS IS)"), "field": "price_index_distribuidor"},
        {"headerName": _("Meta Competitividade (TO BE)"), "field": "meta_competitividade"},
        {"headerName": _("Ativo"), "field": "ativo"},
        {"headerName": _("UUID Alteração"), "field": "uuid_alteracoes"},
    ]

def get_marketing_data(cpc):
    return get_initial_data_configs(process_name="marketing", cpc=cpc)

def create_approval_buttons(pathname, user_data):
    return html.Div(
        children=[
            dbc.Button(
                _("Aprovar"),
                id="button-approval-marketing",
                color="success",
                disabled=True,
                n_clicks=0
            ),
            dbc.Tooltip(
                _("Enviar para aprovação"),
                target="button-approval-marketing",
                placement="top",
            ),
        ],
        style=CONTAINER_BUTTONS_STYLE,
    )


def get_layout(pathname, user_data):

    cpc = user_data.get('cpc1_3_6_list')
    table_data = get_requests_for_approval(table="marketing") if pathname == "/approval" else get_marketing_data(cpc)

    table = handle_no_data_to_show(table_data.get("error")) if table_data.get("error") else dag.AgGrid(
        id='table-marketing',
        rowData=table_data.to_dict("records"),
        columnDefs=columns_approval() if pathname == "/approval" else create_columns(pathname, user_data),
        columnSize="responsiveSizeToFit" if pathname == "/approval" else "autoSize",
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
                    modal_title=helper_text["marketing"]["title"],
                    modal_body=helper_text["marketing"]["description"],
                ),
            ], style=CONTAINER_HELPER_BUTTON_STYLE,
        ),
        container_approval_reject_buttons(table="marketing") if pathname == "/approval" else create_approval_buttons(pathname, user_data),
        Toast(id="toast-approval-marketing"),
        html.Div(
            table,
            style=CONTAINER_TABLE_STYLE
        ),
    ]

marketing_page = html.Div([
    dbc.Spinner(
        html.Div(id="marketing-content"),
        color="primary",
        size="lg",
        fullscreen=True,
    )
])

@callback(
    Output("marketing-content", "children"),
    [
        Input("url", "pathname"),
        Input("store-token", "data"),
        Input("store-language", "data"),
    ],
)
def update_marketing_content(pathname, user_data, language):

    global _
    _ = setup_translations(language)

    if pathname in ["/marketing", "/approval"]:
        return get_layout(pathname, user_data)
    return no_update

# Callback para atualizar a tabela, habilitar botão de aprovação e envio dos dados para o back-end
@callback(
    Output('table-marketing', 'rowData'),
    Output('button-approval-marketing', 'disabled'),
    Input('table-marketing', 'cellValueChanged'),
    Input('button-approval-marketing', 'n_clicks'),
    State('table-marketing', 'rowData'),
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

            variables_to_send = {
                "user_token": user_data["access_token"],
                "table_data": filtered_df,
            }

            send_to_approval("marketing", variables_to_send)

        return updated_row_data, False
    return no_update, no_update

# Callback para aprovação/rejeição
@callback(
    Output("toast-approval-marketing", "is_open"),
    Output("toast-approval-marketing", "header"),
    Output("toast-approval-marketing", "children"),
    Input("button-approval-accept-marketing", "n_clicks"),
    Input("button-approval-reject-marketing", "n_clicks"),
    State("table-marketing", "rowData"),
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
        return html.P(_("Erro: Não há dados para aprovar/recusar"),className="message-danger")

    try:
        uuid_alteracoes = table_data[0]["uuid_alteracoes"]

        variables_to_send = {
            "uuid_alteracoes": uuid_alteracoes,
            "status": status,
            "user_token": user_data["access_token"],
            "target_table": "marketing",
        }

        update_approval_status(variables_to_send)
        return True, f"{status_text}", f"{_('Status alterado para')} {status_text}"

    except Exception as e:
        print(f"Erro ao processar aprovação: {str(e)}")
        return True, _("Erro"), f"{_('Erro ao processar aprovação:')} {str(e)}"
