import pandas as pd
import dash_bootstrap_components as dbc
import dash_ag_grid as dag
from dash import html, callback, Input, Output, State, no_update, ctx
from components.Toast import Toast
from components.Modal import create_modal
from components.Helper_button_with_modal import create_help_button_with_modal
from api.get_initial_data_configs import get_initial_data_configs
from api.send_to_approval import send_to_approval
from api.get_requests_for_approval import get_requests_for_approval
from api.update_approval_status import update_approval_status
from static_data.helper_text import helper_text
from pages.approvals.approval_utils import container_approval_reject_buttons
from utils.user_has_permission_to_edit import user_has_permission_to_edit
from utils.modify_column_if_other_column_changed import modify_column_if_other_column_changed
from styles import CONTAINER_BUTTONS_STYLE, CONTAINER_TABLE_STYLE, CONTAINER_HELPER_BUTTON_STYLE, MAIN_TITLE_STYLE
from utils.handle_nothing_to_approve import handle_nothing_to_approve
from utils.handle_no_data_to_show import handle_no_data_to_show
from translations import _, setup_translations

def columns(pathname, user_data):
    return [
        {"headerName": "CPC1_3_6", "field": "cpc1_3_6"},
        {
            "headerName": _("Estratégia"), 
            "field": "estrategia_utilizada", 
            "editable": user_has_permission_to_edit(pathname, user_data),
            "cellEditor": "agSelectCellEditor",
            "cellEditorParams": {
                "values": [_("MARGEM"), _("FATURAMENTO"), _("EFEITO PREÇO")]
            },
        },
        {
            "headerName": _("Efeito Preço"),
            "field": "efeito_preco",
            "type": "numericColumn",
            "editable": {
                "function": "params.data.estrategia_utilizada === 'EFEITO PREÇO'"
            },
            "valueParser": {"function": "Number(params.newValue)"},
            "cellEditorParams": {"min": -1000, "max": 1000},
        },
        {"headerName": _("Manual"), "field": "manual"},
    ]

def columns_approval():
    return [
        {"headerName": _("CPC1_3_6"), "field": "cpc1_3_6"},
        {"headerName": _("Estratégia"), "field": "estrategia_utilizada" },
        {"headerName": _("Efeito Preço"), "field": "efeito_preco"},
        {"headerName": _("Manual"), "field": "manual"},
        {"headerName": _("UUID Alteração"), "field": "uuid_alteracoes"},
    ]

def create_approval_buttons(pathname, user_data):
    return html.Div(
        children=[
            dbc.Button(
                _("Aprovar"), 
                id="button-approval-strategy",
                color="success",
                # disabled=False if user_has_permission_to_edit(pathname, user_data) else True,
                disabled=True,
                n_clicks=0
            ),
            dbc.Tooltip(
                _("Enviar para aprovação"),
                target="button-approval-strategy",
                placement="top",
            ),
        ],
        style=CONTAINER_BUTTONS_STYLE,
    )

def get_strategy_data(cpc):
    table_data = get_initial_data_configs("strategy", cpc=cpc)
    table_data["manual"] = ""  
    table_data["efeito_preco"] = "" 
    return table_data

def create_date_dropdown(data):
    unique_dates = sorted(set(row.get('data_alteracoes', '') for row in data if row.get('data_alteracoes')), reverse=True)
    return dbc.Select(
        id='date-filter-dropdown',
        options=[{'label': date, 'value': date} for date in unique_dates],
        value=unique_dates[0] if unique_dates else None,
        className="dropdown-date"
    )

helper_button = html.Div(
    create_help_button_with_modal(
        modal_title=helper_text["strategy"]["title"],
        modal_body=helper_text["strategy"]["description"],
    ), style=CONTAINER_HELPER_BUTTON_STYLE,
)

def get_layout(pathname, user_data):

    cpc = user_data.get('cpc1_3_6_list')
    table_data = get_requests_for_approval(table="strategy") if pathname == "/approval" else get_strategy_data(cpc)

    table = handle_no_data_to_show(table_data.get("error")) if table_data.get("error") else dag.AgGrid(
        id='table-strategy',
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
        html.H1(_('Estratégia Comercial'), style=MAIN_TITLE_STYLE),
        helper_button
    ], className="container-title")
        
    container_change_approval = container_approval_reject_buttons(table="strategy")
    container_send_approval = create_approval_buttons(pathname, user_data)

    toast_approval = Toast(
        id="toast-approval-strategy",
        header=_("Aprovação"),
        toast_message=_("Enviado para aprovação"),
    )

    toast_reject = Toast(
        id="toast-approval-reject-strategy",
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
    modal_id="modal-confirm-approval-strategy",
    modal_title="Solicitar Aprovação",
    modal_body=html.P("Tem certeza que deseja enviar para aprovação?"),
    modal_footer=html.Div([
        dbc.Button("Não", id="btn-cancel-approval", color="secondary", className="me-2"),
        dbc.Button("Sim", id="btn-confirm-approval", color="success")
    ]),
    is_open=False
)

strategy_page = html.Div([
    dbc.Spinner(
        html.Div(id="strategy-content"),
        color="primary",
        size="lg",
        fullscreen=True,
    ),
    modal_confirm_approval,
])

# Callback para controlar a renderização do conteúdo da página
@callback(
    Output("strategy-content", "children"),
    [
        Input("url", "pathname"),
        Input("store-token", "data"),
        Input("store-language", "data"),
    ],
)
def update_strategy_content(pathname, user_data, language):

    global _
    _ = setup_translations(language)

    if pathname in ["/strategy", "/approval"]:
        return get_layout(pathname, user_data)
    return no_update

# Callback para atualizar a tabela e habilitar botão de aprovação
@callback(
    Output('table-strategy', 'rowData'),
    Output('button-approval-strategy', 'disabled'),
    Input('table-strategy', 'cellValueChanged'),
    State('table-strategy', 'rowData'),
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

        # Validação: efeito_preco entre -1000 e 1000
        for row in updated_row_data:
            if "efeito_preco" in row and row["efeito_preco"] != "":
                try:
                    valor = float(row["efeito_preco"])
                    if valor < -1000:
                        row["efeito_preco"] = -1000
                    elif valor > 1000:
                        row["efeito_preco"] = 1000
                except ValueError:
                    row["efeito_preco"] = ""

        return updated_row_data, False
    return no_update, no_update

# Callback para abrir o modal de confirmação de aprovação
@callback(
    Output("modal-confirm-approval-strategy", "is_open"),
    Input("button-approval-strategy", "n_clicks"),
    prevent_initial_call=True,
)
def open_confirm_approval_modal(n_clicks):
    if n_clicks:
        return True
    return False

# Callback para processar a confirmação de aprovação
@callback(
    Output("modal-confirm-approval-strategy", "is_open", allow_duplicate=True),
    Output("toast-approval-strategy", "is_open", allow_duplicate=True),
    Input("btn-confirm-approval","n_clicks"),
    Input("btn-cancel-approval","n_clicks"),
    State("table-strategy", "rowData"),
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
        
        send_to_approval("strategy", variables_to_send)

        return False, True
    return False, False


# Callback para aprovação/rejeição
@callback(
    Output("toast-approval-reject-strategy", "is_open"),
    Output("toast-approval-reject-strategy", "header"),
    Output("toast-approval-reject-strategy", "children"),
    Input("button-approval-accept-strategy", "n_clicks"),
    Input("button-approval-reject-strategy", "n_clicks"),
    State("table-strategy", "rowData"),
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
        return html.P(_("Erro: Não há dados para aprovar/recusar"), className="message-danger")

    try:
        uuid_alteracoes = table_data[0]["uuid_alteracoes"]

        variables_to_send = {
            "uuid_alteracoes": uuid_alteracoes,
            "status": status,
            "user_token": user_data["access_token"],
            "target_table": "strategy",
        }

        update_approval_status(variables_to_send)
        return True, f"{status_text}", f"Status alterado para {status_text}"

    except Exception as e:
        print(f"Erro ao processar aprovação: {str(e)}")
        return True, "Erro", f"Erro ao processar aprovação: {str(e)}"