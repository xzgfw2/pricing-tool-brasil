import dash_bootstrap_components as dbc
import dash_ag_grid as dag
import pandas as pd
import polars as pl
from dash import Input, Output, callback, State, html, ctx, no_update, dcc
from components.Card import Card
from components.Toast import Toast
from components.Modal import create_modal
from pages.approvals.approval_utils import container_approval_reject_buttons
from api.get_requests_for_approval import get_requests_for_approval
from api.api_get_captain_simulation import get_captain_simulation
from api.send_to_approval import send_to_approval
from api.update_approval_status import update_approval_status
from utils.handle_data import handle_data
from utils.deserialize_json import deserialize_json
from utils.handle_nothing_to_approve import handle_nothing_to_approve
from utils.handle_no_data_to_show import handle_no_data_to_show
from static_data.helper_text import helper_text
from components.Helper_button_with_modal import create_help_button_with_modal
from styles import CONTAINER_BUTTONS_DUAL_STYLE, CONTAINER_CARD_STYLE, HELPER_MESSAGE, CAPTAIN_CARD_INSIDE_STYLE, CONTAINER_HELPER_BUTTON_STYLE, MAIN_TITLE_STYLE
from translations import _, setup_translations

def columns(): 
    return [
        {"headerName": "CPC1_3_6", "field": "cpc1_3_6"},
        {"headerName": _("Rank"), "field": "rank"},
        {"headerName": _("Part Number"), "field": "part_number"},
        {"headerName": _("Descrição"), "field": "descricao"},
        {"headerName": _("Critério"), "field": "criterio"},
        {"headerName": _("Repres. Vol"), "field": "vol"},
        {"headerName": _("Repres. Faturamento"), "field": "gross_sales"},
        {"headerName": _("Data Inclusão"), "field": "data_inclusao"},
        {"headerName": _("Penetração"), "field": "penetracao"},
        {"headerName": _("Capitão (atual)"), "field": "capitao_atual"},
        {"headerName": _("Manual / Sistema"), "field": "manual_ou_sistema"},
        {"headerName": _("Capitão (sistema)"), "field": "capitao_sistema"},
        {
            "headerName": _("Aprovar Mudança?"),
            "field": "approve_change",
            "editable": True,
            "cellEditor": "agSelectCellEditor",
            "cellEditorParams": {
                "values": ["Aceitar", "Anterior", "Recusar"],
                "value": "Aceitar"
            },
        },
        {
            "headerName": _("Capitão (novo)"),
            "field": "novo_capitao",
            "editable": True,
            "cellEditor": "agSelectCellEditor",
            "cellEditorParams": {
                "values": ["1", ""],
            },
        }
    ]

def columns_approval():
    return [
        {"headerName": _("CPC1_3_6"), "field": "cpc1_3_6"},
        {"headerName": _("Rank"), "field": "rank"},
        {"headerName": _("Part Number"), "field": "part_number"},
        {"headerName": _("Descrição"), "field": "descricao"},
        {"headerName": _("Critério"), "field": "criterio"},
        {"headerName": _("Repres. Vol"), "field": "vol"},
        {"headerName": _("Repres. Faturamento"), "field": "gross_sales"},
        {"headerName": _("Data Inclusão"), "field": "data_inclusao"},
        {"headerName": _("Penetração"), "field": "penetracao"},
        {"headerName": _("Capitão (atual)"), "field": "capitao_atual"},
        {"headerName": _("Manual / Sistema"), "field": "manual_ou_sistema"},
        {"headerName": _("Capitão (sistema)"), "field": "capitao_sistema"},
        {"headerName": _("Aprovar Mudança ?"), "field": "approve_change"},
        {"headerName": _("Capitão (novo)"), "field": "novo_capitao"},
        {"headerName": _("UUID Alteração"), "field": "uuid_alteracoes"}, # temporário para testes
        # {"headerName": _("Status"), "field": "status"}, # temporário para testes
    ]

def get_simulation_data():
    table_data = get_captain_simulation()
    table_data["approve_change"] = "Aceitar"
    table_data["novo_capitao"] = None
    return table_data

helper_button = html.Div(
    create_help_button_with_modal(
        modal_title=helper_text["captain_simulation"]["title"],
        modal_body=helper_text["captain_simulation"]["description"],
    ), style=CONTAINER_HELPER_BUTTON_STYLE,
)


def get_layout(pathname):

    table_data = get_requests_for_approval(table="captain") if pathname == "/approval" else get_simulation_data()
    formated_data = handle_data(table_data, decimal_places=2, date_format='%m-%d-%y')

    table = handle_no_data_to_show(table_data.get("error")) if table_data.get("error") else dag.AgGrid(
        id='table-simulation-captain',
        rowData=formated_data.to_dict("records") if formated_data is not None else [],
        columnDefs=columns_approval() if pathname == "/approval" else columns(),
        columnSize="autoSize",
        defaultColDef={
            "sortable": True,
            "filter": True,
            "resizable": True,
            "singleClickEdit": True,
        },
        dashGridOptions={
            "pagination": True,
            "paginationPageSize": 20,
        },
        style={'height': '500px'},
    )

    return handle_nothing_to_approve() if table_data is None else [
        Toast(
            id="toast-approval-captain",
            header=_("Aprovação"),
            toast_message=_("Enviado para aprovação"),
        ),
        Toast(id="toast-approval-captain-simulation"),
        None if pathname == "/approval" else html.Div(
            [
                html.H1(_('Simulação do Capitão'), style=MAIN_TITLE_STYLE),
                helper_button
            ], className="container-title"),
        container_approval_reject_buttons(table="captain") if pathname == "/approval" else html.Div(
            [
                dbc.Button(
                    _("← Voltar"),
                    href="/captain",
                    color="secondary"
                ),
                html.Div([
                    dbc.Button(
                        _("Baixar Excel"),
                        id="btn-download-excel-captain",
                        color="success",
                        className="me-2",
                        n_clicks=0
                    ),
                    dbc.Tooltip(
                        _("Baixar arquivo em Excel"),
                        target="btn-download-excel-captain",
                        placement="top",
                    ),
                    dcc.Download(id="download-excel-captain"),
                    dbc.Button(
                        _("Aprovar"),
                        id="button-approval-captain",
                        color="success",
                        disabled=True,
                        n_clicks=0
                    ),
                    dbc.Tooltip(
                        _("Enviar para aprovação"),
                        target="button-approval-captain",
                        placement="top",
                    ),
                ]),
            ],
            style=CONTAINER_BUTTONS_DUAL_STYLE,
        ),
        html.Div(
            id="variables-cards",
            style=CONTAINER_CARD_STYLE,
        ),
        html.Div(
            id="error-message",
            style=HELPER_MESSAGE
        ),
        html.Div(table),
    ]

modal_confirm_approval = create_modal(
    modal_id="modal-confirm-approval-captain",
    modal_title="Solicitar Aprovação",
    modal_body=html.P("Tem certeza que deseja enviar para aprovação?"),
    modal_footer=html.Div([
        dbc.Button("Não", id="btn-cancel-approval", color="secondary", className="me-2"),
        dbc.Button("Sim", id="btn-confirm-approval", color="success")
    ]),
    is_open=False
)

captain_simulation_page = html.Div([
    dbc.Spinner(
        html.Div(id="captain-simulation-content"),
        color="primary",
        size="lg",
        fullscreen=True,
    ),
    modal_confirm_approval,
])

@callback(
    Output("captain-simulation-content", "children"),
    Input("url", "pathname"),
    Input("store-token", "data"),
    Input("store-language", "data"),
)
def update_simulation_content(pathname, user_data, language):

    global _
    _ = setup_translations(language)

    if pathname in ["/captain-simulation", "/approval"]:
        return get_layout(pathname)
    return no_update

# Callback para baixar a tabela em Excel
@callback(
    Output("download-excel-captain", "data"),
    Input("btn-download-excel-captain", "n_clicks"),
    State("table-simulation-captain", "rowData"),
    prevent_initial_call=True
)
def handle_excel_download_captain(n_clicks, row_data):
    if n_clicks is None or not row_data:
        return None
    df = pd.DataFrame(row_data)
    return dcc.send_data_frame(df.to_excel, "captain_simulation_data.xlsx", index=False)

# Callback para lidar com as mudancas na coluna "approve_change" e refletir a mudança em todo o grupo (CPC 1_3_6)
@callback(
    Output("table-simulation-captain", "rowData"),
    Input("table-simulation-captain", "cellValueChanged"),
    State("table-simulation-captain", "rowData"),
    prevent_initial_call=True
)
def update_approve_change(cellValueChanged, rowData):

    if cellValueChanged and cellValueChanged[0]["colId"] == "approve_change":
        # Converte os dados da tabela em um DataFrame Polars
        df = pl.DataFrame(rowData)

        # Obtém o cpc1_3_6 da célula que foi alterada
        changed_cpc1_3_6 = cellValueChanged[0]["data"]["cpc1_3_6"]
        new_value = cellValueChanged[0]["value"]

        # Atualiza todos os valores de 'approve_change' para o mesmo valor da célula alterada
        df = df.with_columns(
            pl.when(df["cpc1_3_6"] == changed_cpc1_3_6)
            .then(pl.lit(new_value))
            .otherwise(df["approve_change"])
            .alias("approve_change")
        )

        return df.to_dicts()

    return no_update

# Callback para pegar os dados da Store e mostrar nos cards
@callback(
    Output("variables-cards", "children"),
    Input("captain-variables-store", "data"),
)
def get_stored_variables(data):

    stored_variables = deserialize_json(data)

    revenue = html.Div(stored_variables.get("fator_gsales", 0) * 100, style=CAPTAIN_CARD_INSIDE_STYLE)
    volume = html.Div(stored_variables.get("fator_qtd_faturada", 0) * 100, style=CAPTAIN_CARD_INSIDE_STYLE)
    market_share = html.Div(stored_variables.get("fator_penetracao", 0) * 100, style=CAPTAIN_CARD_INSIDE_STYLE)

    cards = [
        Card(
            title=_("Repres. Faturamento"),
            children=revenue,
            position="center",
        ),
        Card(
            title=_("Repres. Volume"),
            children=volume,
            position="center",
        ),
        Card(
            title=_("Repres. Penetração"),
            children=market_share,
            position="center",
        )
    ]

    return cards

# Callback para não permitir mais de um novo capitão por CPC 1_3_6
@callback(
    Output("error-message", "children"),
    Output("button-approval-captain", "disabled"),
    Input("table-simulation-captain", "cellValueChanged"),
    Input("table-simulation-captain", "rowData"),
    prevent_initial_call=True
)
def validate_new_captain(cellValueChanged, rowData):
    error_message = ""
    disable_button_approval = False

    if cellValueChanged:
        df = pd.DataFrame(rowData)

        # Verifica grupos de 'cpc1_3_6' com mais de uma célula preenchida em 'novo_capitao'
        grouped = df.groupby("cpc1_3_6")["novo_capitao"].apply(lambda x: x.notna().sum())
        invalid_groups = grouped[grouped > 1]

        if not invalid_groups.empty:
            error_message = _("Atenção! Só pode haver um capitão por CPC 1_3_6")

            disable_button_approval = True

    # return error_message, no_update
    return error_message, disable_button_approval


# Callback para abrir o modal de confirmação de aprovação
@callback(
    Output("modal-confirm-approval-captain", "is_open"),
    Input("button-approval-captain", "n_clicks"),
    prevent_initial_call=True,
)
def open_confirm_approval_modal(n_clicks):
    if n_clicks:
        return True
    return False


# Callback para enviar os dados da tabela para aprovacao
@callback(
    Output("modal-confirm-approval-captain", "is_open", allow_duplicate=True),
    Output("toast-approval-captain", "is_open", allow_duplicate=True),
    Input("btn-confirm-approval", "n_clicks"),
    Input("btn-cancel-approval", "n_clicks"),
    State("table-simulation-captain", "rowData"),
    State("store-token", "data"),
    prevent_initial_call=True,
)
def handle_send_approval(confirm_clicks, cancel_clicks, table_data, user_data):
    triggered_id = ctx.triggered_id

    # Se for cancelamento, não abre o toast
    if triggered_id == "btn-cancel-approval" and cancel_clicks:
        return False, False

    if triggered_id == "btn-confirm-approval" and confirm_clicks:

        filtered_col_table_data = [{
            "part_number": row["part_number"],
            "approve_change": row["approve_change"],
            "novo_capitao": row["novo_capitao"],
        } for row in table_data]

        filtered_table_data = [
            row for row in filtered_col_table_data
            if row["approve_change"] != "Aceitar"
        ]

        uuid_alteracoes = table_data[0]["uuid_simulacao"]

        variables_to_send = {
            "user_token": user_data["access_token"],
            "table_data": [
                uuid_alteracoes,
                filtered_table_data,
            ],
        }

        send_to_approval("captain", variables_to_send)

        return False, True
    return False, False

# Callback para aprovação/rejeição
@callback(
    Output("toast-approval-captain-simulation", "is_open"),
    Output("toast-approval-captain-simulation", "header"),
    Output("toast-approval-captain-simulation", "children"),
    Output("captain-simulation-content", "children", allow_duplicate=True),
    Input("button-approval-accept-captain", "n_clicks"),
    Input("button-approval-reject-captain", "n_clicks"),
    State("table-simulation-captain", "rowData"),
    State("store-token", "data"),
    prevent_initial_call=True
)
def handle_approval(accept_clicks, reject_clicks, table_data, user_data):

    if accept_clicks > 0 or reject_clicks > 0:
        print("handle_approval")

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
                "target_table": "captain",
            }

            is_true = update_approval_status(variables_to_send)

            refetch_table = get_requests_for_approval(table="captain") if is_true is True else None

            new_content = handle_nothing_to_approve() if refetch_table is None else refetch_table

            return True, f"{status_text}", f"Status alterado para {status_text}", new_content

        except Exception as e:
            print(f"Erro ao processar aprovação: {str(e)}")
            return True, "Erro", f"Erro ao processar aprovação: {str(e)}", no_update
