from dash import Dash, dcc, html, callback, dash_table, State, Input, Output, no_update, ctx
import dash_bootstrap_components as dbc
from dash.dash_table import FormatTemplate
from dash.dash_table.Format import Format
import polars as pl
import pandas as pd
from pages.approvals.approval_utils import container_approval_reject_buttons
from components.Card import Card
from components.Toast import Toast
from components.Helper_button_with_modal import create_help_button_with_modal
from components.Modal import create_modal
from api.api_get_last_sim_user import get_last_sim_user
from api.get_requests_for_approval import get_requests_for_approval
from api.send_to_approval import send_to_approval
from api.update_approval_status import update_approval_status
from utils.sum_df_col import sum_df_col
from utils.calculation_division import calculation_division
from utils.handle_nothing_to_approve import handle_nothing_to_approve
from static_data.helper_text import helper_text
from styles import CONTAINER_BUTTONS_DUAL_STYLE, CONTAINER_CARD_STYLE, CONTAINER_TABLE_STYLE, TABLE_HEADER_STYLE, TABLE_CELL_STYLE, TABLE_STYLE, CONTAINER_HELPER_BUTTON_STYLE
from translations import _, setup_translations

CONTAINER_CONTENT_STYLE = {
    "display": "flex",
    "gap": "20px",
    "justify-content": "space-between",
}

CONTAINER_TABLE_STYLE = {
    "width": "100%",
}

def COLUMNS(_):
    return [
        {"name": ["", _("Peça")], "id": "peca", "selectable": True, "hideable": True},
        {"name": ["", _("Descrição")], "id": "descricao", "selectable": True, "hideable": True},
        {"name": ["", _("CPC 1 3 6")], "id": "cpc1_3_6", "selectable": True},
        {"name": [_("Preço Venda"), "AS IS"], "id": "preco_venda", "selectable": True, "hideable": True},
        {"name": [_("Preço Venda"), "TO BE"], "id": "preco_venda_cap", "selectable": True, "hideable": True, "type": "numeric", "format": {"specifier": ".2f", "locale": {"group": ".", "decimal": ","}}},
        {"name": [_("Preço Venda"), "Delta %"], "id": "dp_cap", "selectable": True, "hideable": True, "type": "numeric", "format": FormatTemplate.percentage(2)},
        {"name": [_("Volume"), "AS IS"], "id": "qtd_volume", "selectable": True, "hideable": True},
        {"name": [_("Volume"), "TO BE"], "id": "vol_cap2", "selectable": True, "hideable": True, "type": "numeric", "format": {"specifier": ".2f", "locale": {"group": ".", "decimal": ","}}},
        {"name": [_("Volume"), "Delta %"], "id": "dv_cap2", "selectable": True, "hideable": True, "type": "numeric", "format": FormatTemplate.percentage(2)},
        {"name": [_("Fat Bruto"), "AS IS"], "id": "gross_sales", "selectable": True, "hideable": True},
        {"name": [_("Fat Bruto"), "TO BE"], "id": "gross_cap", "selectable": True, "hideable": True, "type": "numeric", "format": {"specifier": ".2f", "locale": {"group": ".", "decimal": ","}}},
        {"name": [_("Fat Bruto"), "Delta %"], "id": "delta_gross_sales", "selectable": True, "hideable": True, "type": "numeric", "format": FormatTemplate.percentage(2)},
        {"name": [_("Fat Liq"), "AS IS"], "id": "net_sales", "selectable": True, "hideable": True},
        {"name": [_("Fat Liq"), "TO BE"], "id": "net_cap", "selectable": True, "hideable": True, "type": "numeric", "format": {"specifier": ".2f", "locale": {"group": ".", "decimal": ","}}},
        {"name": [_("Fat Liq"), "Delta %"], "id": "delta_net_sales", "selectable": True, "hideable": True, "type": "numeric", "format": FormatTemplate.percentage(2)},
        {"name": [_("Margem ABS"), "AS IS"], "id": "mc_abs", "selectable": True, "hideable": True},
        {"name": [_("Margem ABS"), "TO BE"], "id": "mc_cap", "selectable": True, "hideable": True},
        {"name": [_("Margem ABS"), "Delta %"], "id": "delta_mc_abs", "selectable": True, "hideable": True, "type": "numeric", "format": FormatTemplate.percentage(2)}
    ]

def COLUMNS_APPROVAL(_): 
    return [
        {"name": ["", _("Peça")], "id": "peca", "selectable": True, "hideable": True},
        {"name": ["", _("Descrição")], "id": "descricao", "selectable": True, "hideable": True},
        {"name": ["", "CPC 1 3 6"], "id": "cpc1_3_6", "selectable": True},
        {"name": [_("Preço Venda"), "AS IS"], "id": "preco_venda", "selectable": True, "hideable": True},
        {"name": [_("Preço Venda"), "TO BE"], "id": "preco_venda_cap", "selectable": True, "hideable": True},
        {"name": [_("Preço Venda"), "Delta %"], "id": "dp_cap", "selectable": True, "hideable": True, "type": "numeric", "format": {"specifier": ".2f", "locale": {"group": ".", "decimal": ","}}},
        {"name": [_("Volume"), "AS IS"], "id": "qtd_volume", "selectable": True, "hideable": True},
        {"name": [_("Volume"), "TO BE"], "id": "vol_cap2", "selectable": True, "hideable": True},
        {"name": [_("Volume"), "Delta %"], "id": "dv_cap2", "selectable": True, "hideable": True, "type": "numeric", "format": {"specifier": ".2f", "locale": {"group": ".", "decimal": ","}}},
        {"name": [_("Fat Bruto"), "AS IS"], "id": "gross_sales", "selectable": True, "hideable": True},
        {"name": [_("Fat Bruto"), "TO BE"], "id": "gross_cap", "selectable": True, "hideable": True},
        {"name": [_("Fat Bruto"), "Delta %"], "id": "delta_gross_sales", "selectable": True, "hideable": True, "type": "numeric", "format": {"specifier": ".2f", "locale": {"group": ".", "decimal": ","}}},
        {"name": [_("Fat Liq"), "AS IS"], "id": "net_sales", "selectable": True, "hideable": True},
        {"name": [_("Fat Liq"), "TO BE"], "id": "net_cap", "selectable": True, "hideable": True},
        {"name": [_("Fat Liq"), "Delta %"], "id": "delta_net_sales", "selectable": True, "hideable": True, "type": "numeric", "format": {"specifier": ".2f", "locale": {"group": ".", "decimal": ","}}},
        {"name": [_("Margem ABS"), "AS IS"], "id": "mc_abs", "selectable": True, "hideable": True},
        {"name": [_("Margem ABS"), "TO BE"], "id": "mc_cap", "selectable": True, "hideable": True},
        {"name": [_("Margem ABS"), "Delta %"], "id": "delta_mc_abs", "selectable": True, "hideable": True, "type": "numeric", "format": {"specifier": ".2f", "locale": {"group": ".", "decimal": ","}}},
        {"name": _("UUID Alteração"), "id": "uuid_alteracoes"}, # temporário para testes
        {"name": _("Status"), "id": "status"}, # temporário para testes
    ]

HIDDEN_COLUMNS = [
    "preco_venda",
    "preco_venda_cap",
    "qtd_volume",
    "vol_cap2",
    "gross_sales",
    "gross_cap",
    "net_sales",
    "net_cap",
    "mc_abs",
    "mc_cap",
]

def create_price_simulation_table(data, pathname):
    return dash_table.DataTable(
        id='table-price-simulation',
        data=data.to_dict("records"),
        columns=COLUMNS_APPROVAL(_) if pathname == "/approval" else COLUMNS(_),
        hidden_columns=HIDDEN_COLUMNS,
        merge_duplicate_headers=True,
        style_table=TABLE_STYLE,
        style_header=TABLE_HEADER_STYLE,
        style_cell=TABLE_CELL_STYLE,
        style_data_conditional=[],
        style_data={
            'whiteSpace': 'normal',
            'height': 'auto',
        },
        style_header_conditional=[
            {
                'if': {'column_id': ['dp_cap', 'dv_cap2', 'delta_gross_sales', 'delta_net_sales', 'delta_mc_abs']},
                'fontWeight': '600'
            }
        ],
        filter_action="native",
        sort_action="native",
        sort_mode="multi",
        sort_by=[{'column_id': 'delta_mc_abs', 'direction': 'desc'}],
        selected_columns=[],
        selected_rows=[],
        page_action="native",
        page_current=0,
        page_size=20,
        style_as_list_view=True,  # Remove bordas verticais
    )

modal_confirm_approval = create_modal(
    modal_id="modal-confirm-approval-price",
    modal_title="Solicitar Aprovação",
    modal_body=html.P("Tem certeza que deseja enviar para aprovação?"),
    modal_footer=html.Div([
        dbc.Button("Não", id="btn-cancel-approval", color="secondary", className="me-2"),
        dbc.Button("Sim", id="btn-confirm-approval", color="success")
    ]),
    is_open=False
)


# Callback para processar a aprovação
@callback(
    Output("modal-confirm-approval-price", "is_open", allow_duplicate=True),
    Input("btn-confirm-approval", "n_clicks"),
    prevent_initial_call=True,
)
def handle_approval(n_clicks):
    if not n_clicks or n_clicks == 0:
        raise PreventUpdate
    try:
        # Lógica de aprovação aqui (ex: enviar para API, atualizar status, etc)
        return False
    except Exception as e:
        return False

def create_buttons(_):
    return html.Div(
        [
            html.Div(
                dbc.Button(
                    _("← Voltar"),
                    href="/price",
                    color="secondary"
                ),
            ),
            html.Div(
                [
                    dbc.Button(
                        _("Baixar Excel"),
                        id="btn-download-excel-price-simulation",
                        color="success",
                        n_clicks=0
                    ),
                    dbc.Tooltip(
                        _("Baixar arquivo em Excel"),
                        target="btn-download-excel-price-simulation",
                        placement="top",
                    ),
                    dcc.Download(id="download-excel-price-simulation"),
                    dbc.Button(
                        _("Detalhes"),
                        id="button-details",
                        color="success",
                        href="https://app.powerbi.com/groups/3bad649e-c2a9-4609-b993-b4187212586e/reports/f1ed294c-33b6-4f5f-9090-7e95d46eccd3/e84520c2176fca2421f9?experience=power-bi",
                        external_link=True,
                        target="_blank",
                        n_clicks=0
                    ),
                    dbc.Tooltip(
                        _("Ver detalhes no Power BI"),
                        target="button-details",
                        placement="top",
                    ),
                    dbc.Button(
                        _("Aprovar"), 
                        id="button-approval-price-simulation",
                        color="success",
                        disabled=False,
                        n_clicks=0
                    ),
                    dbc.Tooltip(
                        _("Enviar para aprovação"),
                        target="button-approval-price-simulation",
                        placement="top",
                    ),
                ], 
                className="button-group"
            ),
        ],
        style=CONTAINER_BUTTONS_DUAL_STYLE,
    )

def create_cards(df):
    if isinstance(df, list):
        df = pl.DataFrame(df)

    return html.Div([
        dbc.Row([
            dbc.Col(
                Card(
                    title=_("Preço"),
                    value_as_is=calculation_division(df=df, column1="gross_sales", column2="qtd_volume"),
                    value_to_be=calculation_division(df=df, column1="gross_cap", column2="vol_cap2"),
                    show_decimal=True,
                    icon=""
                ),
                width=3,
                className="px-2"
            ),
            dbc.Col(
                Card(
                    title=_("Volume"),
                    value_as_is=sum_df_col(df=df, column="qtd_volume"),
                    value_to_be=sum_df_col(df=df, column="vol_cap2"),
                    show_decimal=False,
                    icon=""
                ),
                width=3,
                className="px-2"
            ),
            dbc.Col(
                Card(
                    title=_("Faturamento Bruto"),
                    value_as_is=sum_df_col(df=df, column="gross_sales"),
                    value_to_be=sum_df_col(df=df, column="gross_cap"),
                    show_decimal=False,
                    icon=""
                ),
                width=3,
                className="px-2"
            ),
            dbc.Col(
                Card(
                    title=_("Margem"),
                    value_as_is=sum_df_col(df=df, column="mc_abs"),
                    value_to_be=sum_df_col(df=df, column="mc_cap"),
                    show_decimal=False,
                    icon=""
                ),
                width=3,
                className="px-2"
            ),
        ], className="g-0 mb-3"),
    ], className="card-container")

helper_button = html.Div(
    create_help_button_with_modal(
        modal_title=helper_text["price_simulation"]["title"],
        modal_body=helper_text["price_simulation"]["description"],
    ), style=CONTAINER_HELPER_BUTTON_STYLE,
)

def get_layout(pathname):
    table_data = get_requests_for_approval(table="price") if pathname == "/approval" else get_last_sim_user()

    if table_data is None:
        return handle_nothing_to_approve()

    simulation_store = dcc.Store(id='stored-simulation-results', storage_type="session")

    header = None
    if pathname != "/approval":
        header = html.Div([
            html.H1(_('Simulação do Resultado'), style=MAIN_TITLE_STYLE),
            helper_button
        ], className="container-title")

    action_buttons = container_approval_reject_buttons(table="price") if pathname == "/approval" else create_buttons(_)

    cards = html.Div(
        children=create_cards(table_data),
        id="cards-container",
        style=CONTAINER_CARD_STYLE
    )

    toast_approval = Toast(id="toast-approval-price")

    container_table = dbc.Spinner(
        html.Div(
            html.Div(
                create_price_simulation_table(table_data, pathname)
            ),
            style=CONTAINER_TABLE_STYLE
        ),
        size="md",
        color="primary",
        fullscreen=False,
    )

    return [
        simulation_store,
        header,
        action_buttons,
        cards,
        toast_approval,
        container_table
    ]


price_sim_architecture_page = html.Div([
    modal_confirm_approval,  # Modal de confirmação de aprovação
    dbc.Spinner(
        html.Div(id="price-simulation-content"),
        color="primary",
        size="lg",
        fullscreen=True,
    )
])

# Callback para controlar a renderização do conteúdo da página
@callback(
    Output("price-simulation-content", "children"),
    Input("url", "pathname"),
    State("store-token", "data"),
    Input("store-language", "data"),
)
def update_price_simulation_content(pathname, user_data, language):

    global _
    _ = setup_translations(language)

    if pathname in ["/price-simulation", "/approval"]:
        return get_layout(pathname)
    return no_update

# Callback para baixar a tabela em Excel
@callback(
    Output("download-excel-price-simulation", "data"),
    Input("btn-download-excel-price-simulation", "n_clicks"),
    State("table-price-simulation", "data"),
    prevent_initial_call=True
)
def handle_excel_download(n_clicks, row_data):
    if n_clicks is None or not row_data:
        return None

    col_to_export = {
        'peca': 'Peça',
        'descricao': 'Descrição',
        'cpc1_3_6': 'CPC1_3_6',
        'custo_medio': 'Custo médio',
        'preco_venda': 'Preço SAP atual',
        'preco_venda_cap': 'Preço SAP novo',
        'hash_simulacao': 'Hash da Simulação',
        'data_simulacao': 'Data da Simulação',
    }

    df = pd.DataFrame(row_data)    
    df_export = df[col_to_export.keys()].rename(columns=col_to_export)

    return dcc.send_data_frame(df_export.to_excel, "price_simulation_data.xlsx", index=False)

# Callback para controlar todas as operações de modal e aprovação
@callback(
    Output('table-price-simulation', 'data'),
    Output("modal-confirm-approval-price", "is_open"),
    Output("toast-approval-price", "is_open"),
    Output("toast-approval-price", "header"),
    Output("toast-approval-price", "children"),
    Input("button-approval-price-simulation", "n_clicks"),
    Input("btn-confirm-approval", "n_clicks"),
    Input("btn-cancel-approval", "n_clicks"),
    Input("button-approval-accept-price", "n_clicks"),
    Input("button-approval-reject-price", "n_clicks"),
    State('table-price-simulation', 'data'),
    State("store-token", "data"),
    prevent_initial_call=True,
)
def handle_all_modal_and_approval(open_clicks, confirm_clicks, cancel_clicks, 
                                accept_clicks, reject_clicks, table_data, user_data):
    triggered_id = ctx.triggered_id
    
    # Abrir o modal
    if triggered_id == "button-approval-price-simulation":
        return no_update, True, False, "", ""
    
    # Cancelar
    if triggered_id == "btn-cancel-approval" and cancel_clicks:
        return no_update, False, False, "", ""
    
    # Confirmar envio para aprovação
    if triggered_id == "btn-confirm-approval" and confirm_clicks:
        try:
            uuid_alteracoes = table_data[0]["uuid_alteracoes"]
            variables_to_send = {
                "user_token": user_data["access_token"],
                "uuid_alteracoes": uuid_alteracoes,
            }
            send_to_approval("price_simulation", variables_to_send)
            return no_update, False, True, "Sucesso", "Dados enviados para aprovação com sucesso!"
        except Exception as e:
            return no_update, False, True, "Erro", f"Erro ao enviar para aprovação: {str(e)}"
    
    # Aprovar/Rejeitar
    if triggered_id in ["button-approval-accept-price", "button-approval-reject-price"]:
        try:
            status = "1" if triggered_id == "button-approval-accept-price" else "2"
            status_text = "aprovado" if status == "1" else "recusado"
            
            uuid_alteracoes = table_data[0]["hash_simulacao"]
            variables_to_send = {
                "uuid_alteracoes": uuid_alteracoes,
                "status": status,
                "user_token": user_data["access_token"],
                "target_table": "price",
            }
            
            update_approval_status(variables_to_send)
            return no_update, False, True, f"{status_text}", f"Status alterado para {status_text}"
        except Exception as e:
            print(f"Erro ao processar aprovação: {str(e)}")
            return no_update, False, True, "Erro", f"Erro ao processar aprovação: {str(e)}"
    
    return no_update, False, False, "", ""
