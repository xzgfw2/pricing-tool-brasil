import ast
from dash import Dash, dcc, html, callback, State, Input, Output, dash_table, no_update, ALL, MATCH, callback_context, ctx
from dash.exceptions import PreventUpdate
import dash_ag_grid as dag
import dash_bootstrap_components as dbc
import pandas as pd
from components.Card import Card
from components.Helper_button_with_modal import create_help_button_with_modal
from components.Toast import Toast
from components.Modal import create_modal
from pages.approvals.approval_utils import container_approval_reject_buttons
from pages.catlote.catlote_utils import (
    calculate_catlote,
    calculate_totals,
    get_catlote_ids,
    update_property,
    generate_code_string,
    get_unique_values,
)
from api.api_get_catlote_sim import get_catlote_sim
from api.get_requests_for_approval import get_requests_for_approval
from api.send_to_approval import send_to_approval
from api.update_approval_status import update_approval_status
from utils.deserialize_json import deserialize_json
from utils.user_has_permission_to_edit import user_has_permission_to_edit
from utils.handle_nothing_to_approve import handle_nothing_to_approve
from static_data.helper_text import helper_text
from styles import (
    CONTAINER_BUTTONS_DUAL_STYLE,
    TABLE_HEADER_STYLE,
    TABLE_CELL_STYLE,
    CONTAINER_HELPER_BUTTON_STYLE
)
from translations import _, setup_translations

CONTAINER_CONTENT_STYLE = {
    "display": "flex",
    "gap": "20px",
    "justify-content": "space-between",
}

EDITABLE_CELL_STYLE = {
    'backgroundColor': '#e6f3ff',
    'border': '1px solid #ccc'
}

CUSTOM_HEADER_STYLE = {
    **TABLE_HEADER_STYLE,
    'height': 'auto',
    'minHeight': '60px',
    'whiteSpace': 'normal',
    'textAlign': 'center',
    'fontWeight': 'bold',
    'padding': '8px'
}

CUSTOM_CELL_STYLE = {
    **TABLE_CELL_STYLE,
    'height': 'auto',
    'minHeight': '40px',
    'whiteSpace': 'normal',
    'padding': '8px'
}

SUBTITLE = {
    "fontSize": "22px",
    "fontWeight": "bold",
}

def COLUMNS():
    return [
        {"headerName": _("Peça"), "field": "PECA"},
        {"headerName": _("Catlote"), "field": "CATLOTE_1"},
        {"headerName": _("Fornecedor"), "field": "NOME_FORNECEDOR1"},
        {"headerName": _("Custo contrato"), "field": "PRECO_UNIT1"},
        {"headerName": _("Moeda"), "field": "MOEDA1"},
        {"headerName": _("Custo Médio (unit)"), "field": "custo_medio_unit", "editable": True},
        # {"headerName": _("Preço Net"), "field": "preco_net"}, # Inserir marca
        {"headerName": _("Preço SAP Atual"), "field": "preco_sap_atual", "editable": True},
        # {"headerName": _("ICMS"), "field": "imp_icms"},
        # {"headerName": _("Preço com Impostos"), "field": "preco_com_impostos"},
        # {"headerName": _("Desconto"), "field": "desconto"},
        # {"headerName": _("Preço Venda"), "field": "preco_venda"},
        # {"headerName": _("Imposto"), "field": "imp"},
        # {"headerName": _("Preço Net"), "field": "preco_net"},
        # {"headerName": _("Elasticidade"), "field": "e"},
        {"headerName": _("Média Regular (sem campanha)"), "field": "media_regular"},
        {"headerName": _("Média Promo (com campanha)"), "field": "media_promo"},
        {
            "headerName": _("Faturamento Bruto (sem campanha)"),
            "children": [
                {"headerName": "L1", "field": "faturamento_l1_sc"},
                {"headerName": "L2", "field": "faturamento_l2_sc"},
                {"headerName": "L3", "field": "faturamento_l3_sc"},
                {"headerName": "L4", "field": "faturamento_l4_sc"},
            ],
        },
        {
            "headerName": _("Faturamento Bruto (com campanha)"),
            "children": [
                {"headerName": "L1", "field": "faturamento_l1_cc"},
                {"headerName": "L2", "field": "faturamento_l2_cc"},
                {"headerName": "L3", "field": "faturamento_l3_cc"},
                {"headerName": "L4", "field": "faturamento_l4_cc"},
            ],
        },
        {
            "headerName": _("Faturamento Líquido (sem campanha)"),
            "children": [
                {"headerName": "L1", "field": "faturamento_liq_l1_sc"},
                {"headerName": "L2", "field": "faturamento_liq_l2_sc"},
                {"headerName": "L3", "field": "faturamento_liq_l3_sc"},
                {"headerName": "L4", "field": "faturamento_liq_l4_sc"},
            ],
        },
        {
            "headerName": _("Faturamento Líquido (com campanha)"),
            "children": [
                {"headerName": "L1", "field": "faturamento_liq_l1_cc"},
                {"headerName": "L2", "field": "faturamento_liq_l2_cc"},
                {"headerName": "L3", "field": "faturamento_liq_l3_cc"},
                {"headerName": "L4", "field": "faturamento_liq_l4_cc"},
            ],
        },
        {
            "headerName": _("Margem (sem campanha)"),
            "children": [
                {"headerName": "L1", "field": "margem_l1_sc"},
                {"headerName": "L2", "field": "margem_l2_sc"},
                {"headerName": "L3", "field": "margem_l3_sc"},
                {"headerName": "L4", "field": "margem_l4_sc"},
            ],
        },
        {
            "headerName": _("Margem (com campanha)"),
            "children": [
                {"headerName": "L1", "field": "margem_l1_cc"},
                {"headerName": "L2", "field": "margem_l2_cc"},
                {"headerName": "L3", "field": "margem_l3_cc"},
                {"headerName": "L4", "field": "margem_l4_cc"},
            ],
        },
        {
            "headerName": _("Margem Relativa (com campanha)"),
            "children": [
                {"headerName": "L1", "field": "margem_rel_l1_cc"},
                {"headerName": "L2", "field": "margem_rel_l2_cc"},
                {"headerName": "L3", "field": "margem_rel_l3_cc"},
                {"headerName": "L4", "field": "margem_rel_l4_cc"},
            ],
        }
    ]

def COLUMNS_APPROVAL():
    return [
        {"headerName": _("Peça"), "field": "peca"},
        {"headerName": _("Catlote"), "field": "catlote_1"},
        {"headerName": _("Fornecedor"), "field": "nome_fornecedor1"},
        {"headerName": _("Custo contrato"), "field": "preco_unit1"},
        {"headerName": _("Moeda"), "field": "moeda1"},
        {"headerName": _("Custo Médio (unit)"), "field": "custo_medio_unit", "editable": False},
        {"headerName": _("Preço SAP Atual"), "field": "preco_sap_atual", "editable": False},
        {"headerName": _("Média Regular (sem campanha)"), "field": "media_regular"},
        {"headerName": _("Média Promo (com campanha)"), "field": "media_promo"},
        {
            "headerName": _("Faturamento Bruto (sem campanha)"),
            "children": [
                {"headerName": "L1", "field": "faturamento_l1_sc"},
                {"headerName": "L2", "field": "faturamento_l2_sc"},
                {"headerName": "L3", "field": "faturamento_l3_sc"},
                {"headerName": "L4", "field": "faturamento_l4_sc"},
            ],
        },
        {
            "headerName": _("Faturamento Bruto (com campanha)"),
            "children": [
                {"headerName": "L1", "field": "faturamento_l1_cc"},
                {"headerName": "L2", "field": "faturamento_l2_cc"},
                {"headerName": "L3", "field": "faturamento_l3_cc"},
                {"headerName": "L4", "field": "faturamento_l4_cc"},
            ],
        },
        {
            "headerName": _("Faturamento Líquido (sem campanha)"),
            "children": [
                {"headerName": "L1", "field": "faturamento_liq_l1_sc"},
                {"headerName": "L2", "field": "faturamento_liq_l2_sc"},
                {"headerName": "L3", "field": "faturamento_liq_l3_sc"},
                {"headerName": "L4", "field": "faturamento_liq_l4_sc"},
            ],
        },
        {
            "headerName": _("Faturamento Líquido (com campanha)"),
            "children": [
                {"headerName": "L1", "field": "faturamento_liq_l1_cc"},
                {"headerName": "L2", "field": "faturamento_liq_l2_cc"},
                {"headerName": "L3", "field": "faturamento_liq_l3_cc"},
                {"headerName": "L4", "field": "faturamento_liq_l4_cc"},
            ],
        },
        {
            "headerName": _("Margem (sem campanha)"),
            "children": [
                {"headerName": "L1", "field": "margem_l1_sc"},
                {"headerName": "L2", "field": "margem_l2_sc"},
                {"headerName": "L3", "field": "margem_l3_sc"},
                {"headerName": "L4", "field": "margem_l4_sc"},
            ],
        },
        {
            "headerName": _("Margem (com campanha)"),
            "children": [
                {"headerName": "L1", "field": "margem_l1_cc"},
                {"headerName": "L2", "field": "margem_l2_cc"},
                {"headerName": "L3", "field": "margem_l3_cc"},
                {"headerName": "L4", "field": "margem_l4_cc"},
            ],
        },
        {
            "headerName": _("Margem Relativa (com campanha)"),
            "children": [
                {"headerName": "L1", "field": "margem_rel_l1_cc"},
                {"headerName": "L2", "field": "margem_rel_l2_cc"},
                {"headerName": "L3", "field": "margem_rel_l3_cc"},
                {"headerName": "L4", "field": "margem_rel_l4_cc"},
            ],
        },
        {"headerName": _("Status"), "field": "status"},
        {"headerName": _("UUID Alteração"), "field": "uuid_alteracoes"},
    ]

modal_confirm_approval = create_modal(
    modal_id="modal-confirm-approval-catlote",
    modal_title="Solicitar Aprovação",
    modal_body=html.P("Tem certeza que deseja enviar para aprovação?"),
    modal_footer=html.Div([
        dbc.Button("Não", id="btn-cancel-approval", color="secondary", className="me-2"),
        dbc.Button("Sim", id="btn-confirm-approval", color="success")
    ]),
    is_open=False
)


def create_cards(totals):
    # Se totals já for um dicionário com os totais calculados, usa diretamente
    if not isinstance(totals, list):
        return html.Div([
            dbc.Row([
                dbc.Col(
                    Card(
                        title=_("Volume"),
                        value_as_is=totals["total_volume_sc"],
                        value_to_be=totals["total_volume_cc"],
                        show_decimal=False,
                        icon="📦"
                    ),
                    width=3,
                    className="px-2"
                ),
                dbc.Col(
                    Card(
                        title=_("Faturamento Líquido"),
                        value_as_is=totals["total_faturamento_liq_sc"],
                        value_to_be=totals["total_faturamento_liq_cc"],
                        show_decimal=False,
                        icon="📊"
                    ),
                    width=3,
                    className="px-2"
                ),
                dbc.Col(
                    Card(
                        title=_("Margem"),
                        value_as_is=totals["total_margem_sc"],
                        value_to_be=totals["total_margem_cc"],
                        show_decimal=False,
                        icon="📈"
                    ),
                    width=3,
                    className="px-2"
                ),
                dbc.Col(
                    Card(
                        title=_("Margem Rel"),
                        value_as_is=totals["total_margem_rel_sc"],
                        value_to_be=totals["total_margem_rel_cc"],
                        show_decimal=True,
                        option = "pp",
                        icon="% "
                    ),
                    width=3,
                    className="px-2"
                ),
            ], className="g-0 mb-3"),
        ], style={"backgroundColor": "#f8f9fa", "padding": "1rem", "borderRadius": "8px"})

    return no_update

def show_catlote_id_in_subtitle(catlotes_id):
    """Mostra os IDs dos catlotes no subtítulo"""
    if not catlotes_id:
        return ""
    
    catlotes_str = ", ".join(catlotes_id)
    return f"Catlotes: {catlotes_str}"

def create_discount_editor(catlote_data):
    """Cria o editor de descontos para cada catlote"""
    def get_numeric_value(value):
        """Converte valor para número, retorna 0 se inválido"""
        try:
            return float(value) if value is not None else 0
        except (ValueError, TypeError):
            return 0

    # Agrupar dados por catlote
    catlotes = {}
    for row in catlote_data:
        catlote_id = row.get('CATLOTE_1') or row.get('CATLOT1')
        if catlote_id:
            catlotes[catlote_id] = row

    return html.Div([
        dbc.Accordion([
            dbc.AccordionItem(
                [
                    # Linha de descontos
                    html.Div([
                        html.Div([
                            html.Label(
                                _('Desconto') + f" {i+1}",
                                style={
                                    "fontSize": "0.875rem",
                                    "color": "#6c757d",
                                    "marginBottom": "4px"
                                }
                            ),
                            dbc.Input(
                                type="number",
                                id={
                                    "type": "discount-input",
                                    "index": f"{catlote_id}-{i+1}"
                                },
                                value=get_numeric_value(catlote.get(f'D{i+1}', 0) * 100),
                                min=0,
                                max=100,
                                step=1,
                                style={
                                    "width": "120px",
                                    "marginBottom": "8px",
                                    # **EDITABLE_CELL_STYLE
                                }
                            )
                        ], style={"marginRight": "20px"})
                        for i in range(4)
                    ], style={"display": "flex", "marginBottom": "15px"}),
                    # Linha de participações estimadas
                    html.Div([
                        html.Div([
                            html.Label(
                                _("Participação % (Estim.)") + f" {i+1}",
                                style={
                                    "fontSize": "0.875rem",
                                    "color": "#6c757d",
                                    "marginBottom": "4px"
                                }
                            ),
                            dbc.Input(
                                type="number",
                                id={
                                    "type": "participation-input",
                                    "index": f"{catlote_id}-{i+1}"
                                },
                                value=get_numeric_value(catlote.get(f'E{i+1}', 0) * 100),
                                min=0,
                                max=100,
                                step=1,
                                style={
                                    "width": "120px",
                                    "marginBottom": "8px",
                                    # **EDITABLE_CELL_STYLE
                                }
                            )
                        ], style={"marginRight": "20px"})
                        for i in range(4)
                    ], style={"display": "flex", "marginBottom": "15px"}),
                    
                    # Informações adicionais
                    html.Div([
                        html.Div([
                            html.Label(_("Participações (Atuais)"), className="mb-2", style={"color": "#6c757d"}),
                            html.Div([
                                html.Span(
                                    f"P{i+1}: {get_numeric_value(catlote.get(f'P{i+1}', 0)):.1%}",
                                    style={"marginRight": "10px"}
                                )
                                for i in range(4)
                            ])
                        ], className="mb-3"),
                        html.Div([
                            html.Label(_("Participação % (Estim.)"), className="mb-2", style={"color": "#6c757d"}),
                            html.Div([
                                html.Span(
                                    f"E{i+1}: {get_numeric_value(catlote.get(f'E{i+1}', 0)):.1%}",
                                    style={"marginRight": "10px"}
                                )
                                for i in range(4)
                            ])
                        ])
                    ], style={"marginTop": "10px"})
                ],
                title=f"Catlote {catlote_id}",
                item_id=str(catlote_id)
            )
            for catlote_id, catlote in catlotes.items()
        ],
        start_collapsed=True,
        style={
            "marginBottom": "15px"
        })
    ])

# Callback para controlar o collapse
@callback(
    Output({"type": "collapse-content", "index": MATCH}, "is_open"),
    Input({"type": "collapse-button", "index": MATCH}, "n_clicks"),
    State({"type": "collapse-content", "index": MATCH}, "is_open"),
    prevent_initial_call=True
)
def toggle_collapse(n_clicks, is_open):
    if n_clicks:
        return not is_open
    return is_open

def get_layout(pathname, user_data, stored_data=None):

    if pathname == "/approval":
        table_data = get_requests_for_approval(table="catlote")

    else:
        if isinstance(stored_data, str):
            catlote_data = deserialize_json(stored_data)
            print("catlote_data", catlote_data)
        else:
            catlote_data = stored_data

        catlotes_id = get_catlote_ids(catlote_data)
        products_data = get_catlote_sim(catlote_filter=catlotes_id)

        calculated_data = calculate_catlote(
            catlote_inputs=catlote_data,
            catlote_data_products=products_data.to_dict('records'),
        )

        table_data = calculated_data["table"]

    return handle_nothing_to_approve() if table_data is None else [
        dcc.Location(id="url-catlote", refresh=True),
        Toast(id="toast-approval-catlote"),
        html.Div(
            children=[
                None if pathname == "/approval" else html.Div(
                    [
                        html.Div(className="flexible-spacer"),
                        create_help_button_with_modal(
                            modal_title=helper_text["catlote_simulation"]["title"],
                            modal_body=helper_text["catlote_simulation"]["description"],
                        ),
                    ], style=CONTAINER_HELPER_BUTTON_STYLE,
                ),
                container_approval_reject_buttons(table="catlote") if pathname == "/approval" else html.Div(
                    [
                        dbc.Button(
                            _("← Voltar"),
                            href="/catlote",
                            color="secondary"
                        ),
                        html.Div([
                            dbc.Button(
                                _("Baixar Excel"),
                                id="btn-download-excel-catlote",
                                color="success",
                                className="me-2",
                                n_clicks=0
                            ),
                            dbc.Tooltip(
                                _("Baixar arquivo em Excel"),
                                target="btn-download-excel-catlote",
                                placement="top",
                            ),
                            dcc.Download(id="download-excel-catlote"),
                            dbc.Button(
                                _("Aprovar"),
                                id="button-approval-simulation-catlote",
                                color="success",
                                disabled=False if user_has_permission_to_edit(pathname, user_data) else True,
                                n_clicks=0
                            ),
                            dbc.Tooltip(
                                _("Enviar para aprovação"),
                                target="button-approval-simulation-catlote",
                                placement="top",
                            ),
                        ]),
                    ],
                    style=CONTAINER_BUTTONS_DUAL_STYLE,
                ),
                html.Div(
                    id="cards-catlote-container",
                    children=create_cards(calculate_totals(table_data)),
                    style={"marginBottom": "2rem"}
                ),
                None if pathname == "/approval" else create_discount_editor(catlote_data),
                html.Div(
                    id="table-container",
                    children=[
                        html.H3(
                            _("Detalhamento de Produtos"),
                            style={
                                "fontSize": "1.1rem",
                                "fontWeight": "500",
                                "color": "#212529",
                                "marginBottom": "1rem",
                                "marginTop": "2rem"
                            }
                        ),
                        html.P(
                            _("Volume dos últimos 12 meses com preços e custos vigentes"),
                            style={
                                "color": "black",
                                "fontSize": "0.8rem",
                                "marginBottom": "10px",
                            }
                        ),
                        dag.AgGrid(
                            id='table-simulation-catlote',
                            rowData=table_data.to_dict("records"),
                            columnDefs=COLUMNS_APPROVAL() if pathname == "/approval" else COLUMNS(),
                            defaultColDef={
                                "sortable": True,
                                "filter": 'agTextColumnFilter',
                                "filterParams": {
                                    "buttons": ["apply", "reset"],
                                    "closeOnApply": True,
                                },
                                "resizable": True,
                                "minWidth": 80,
                                "autoSize": True,
                                "suppressSizeToFit": False
                            },
                            dashGridOptions={
                                "pagination": True,
                                "paginationPageSize": 15,
                                "enableRangeSelection": True,
                                "enableFilter": True,
                                "domLayout": 'autoHeight',
                                "stopEditingWhenCellsLoseFocus": True,
                                "enterMovesDown": False,
                                "enterMovesDownAfterEdit": False,
                            },
                            className="ag-theme-alpine",
                            style={
                                "height": "calc(100vh - 200px)",
                                "width": "100%",
                            }
                        )
                    ],
                    style={"marginTop": "1rem"}
                ),
            ],
            style={"padding": "20px"}
        )
    ]

catlote_simulation_page = html.Div([
    modal_confirm_approval,  # Modal de confirmação de aprovação
    dbc.Spinner(
        html.Div(id="catlote-simulation-content"),
        color="primary",
        size="lg",
        fullscreen=True,
    )
])

# Callback para renderizar o conteúdo da página
@callback(
    Output("catlote-simulation-content", "children"),
    Input("url", "pathname"),
    State("catlote-variables-store", "data"),
    State("store-token", "data"),
    Input("store-language", "data"),
)
def update_catlote_content(pathname, stored_data, user_data, language):

    global _
    _ = setup_translations(language)

    if pathname == "/catlote-simulation":
        return get_layout(pathname, user_data, stored_data)
    if pathname == "/approval":
        return get_layout(pathname, user_data)
    return no_update

# Callback para recalcular quando os descontos ou participações são alterados
@callback(
    Output('table-simulation-catlote', 'rowData', allow_duplicate=True),
    Output('cards-catlote-container', 'children', allow_duplicate=True),
    Output("catlote-variables-store", "data", allow_duplicate=True),
    Input({'type': 'discount-input', 'index': ALL}, 'value'),
    Input({'type': 'participation-input', 'index': ALL}, 'value'),
    State('table-simulation-catlote', 'rowData'),
    State("catlote-variables-store", "data"),
    prevent_initial_call=True,
    # background=False
)
def update_simulation_with_changes(discount_values, participation_values, table_data, stored_data):

    if not callback_context.triggered:
        raise PreventUpdate

    try:
        triggered = callback_context.triggered[0]
        triggered_id = triggered['prop_id'].split('.')[0]
        triggered_value = triggered['value']

        triggered_id = ast.literal_eval(triggered_id)
        field_value = float(triggered_value or 0)

        if isinstance(stored_data, str):
            new_stored_data = deserialize_json(stored_data)
            print("new_stored_data", new_stored_data)
        else:
            new_stored_data = stored_data

        property_name = generate_code_string(triggered_id['index'], triggered_id['type'])
        updated_stored_data = update_property(new_stored_data, property_name, field_value)
    
        calculated_data = calculate_catlote(
            catlote_inputs=updated_stored_data,
            catlote_data_products=table_data
        )

        result_data = calculated_data["table"].to_dict("records")
        result_totals = calculated_data["totals"]

        return result_data, create_cards(result_totals), new_stored_data

    except Exception as e:
        print(f"Erro ao atualizar simulação: {e}")
        import traceback
        traceback.print_exc()
        return no_update, no_update

# Atualiza os cards quando os dados são filtrados
# @callback(
#     Output('cards-catlote-container', 'children'),
#     Input('table-catlote', 'virtualRowData'),
#     prevent_initial_call=True
# )
# def update_cards_on_filter(virtual_data):
#     if not virtual_data:
#         raise PreventUpdate   
#     try:
#         # Inicializa os totais
#         total_faturamento_sc = 0
#         total_faturamento_cc = 0
#         total_faturamento_liq_sc = 0
#         total_faturamento_liq_cc = 0
#         total_margem_sc = 0
#         total_margem_cc = 0
#         total_volume_sc = 0
#         total_volume_cc = 0

#         total_margem_rel_sc = 0
#         total_margem_rel_cc = 0

#         # Calcula os totais para cada linha dos dados filtrados
#         for row in virtual_data:
#             # Faturamento Bruto
#             total_faturamento_sc += (
#                 row.get('faturamento_l1_sc', 0) + 
#                 row.get('faturamento_l2_sc', 0) + 
#                 row.get('faturamento_l3_sc', 0) + 
#                 row.get('faturamento_l4_sc', 0)
#             )
            
#             total_faturamento_cc += (
#                 row.get('faturamento_l1_cc', 0) + 
#                 row.get('faturamento_l2_cc', 0) + 
#                 row.get('faturamento_l3_cc', 0) + 
#                 row.get('faturamento_l4_cc', 0)
#             )
            
#             # Faturamento Líquido
#             total_faturamento_liq_sc += (
#                 row.get('faturamento_liq_l1_sc', 0) + 
#                 row.get('faturamento_liq_l2_sc', 0) + 
#                 row.get('faturamento_liq_l3_sc', 0) + 
#                 row.get('faturamento_liq_l4_sc', 0)
#             )
            
#             total_faturamento_liq_cc += (
#                 row.get('faturamento_liq_l1_cc', 0) + 
#                 row.get('faturamento_liq_l2_cc', 0) + 
#                 row.get('faturamento_liq_l3_cc', 0) + 
#                 row.get('faturamento_liq_l4_cc', 0)
#             )
            
#             # Volume
#             total_volume_sc += row.get('media_regular', 0)
#             total_volume_cc += row.get('media_promo', 0)
            
#             # Margem
#             total_margem_sc += (
#                 row.get('margem_l1_sc', 0) + 
#                 row.get('margem_l2_sc', 0) + 
#                 row.get('margem_l3_sc', 0) + 
#                 row.get('margem_l4_sc', 0)
#             )
            
#             total_margem_cc += (
#                 row.get('margem_l1_cc', 0) + 
#                 row.get('margem_l2_cc', 0) + 
#                 row.get('margem_l3_cc', 0) + 
#                 row.get('margem_l4_cc', 0)
#             )

#             # Margem Relativa
        
#             # calculando margem total total_margem_rel_sc - para evitar erros de divisão por zero
#             try:
#                 numerator = total_margem_sc
#                 denominator = total_faturamento_liq_sc
#                 if denominator != 0:
#                     total_margem_rel_sc = numerator / denominator 
#                 else:
#                     print(f"Aviso: Denominador zero para o índice {index} no cálculo de total_margem_rel_sc")
#             except Exception as e:
#                 print(f"Erro no cálculo de total_margem_rel_sc para o índice {index}: {str(e)}")

#             # calculando margem total total_margem_rel_cc - para evitar erros de divisão por zero
#             try:
#                 numerator = total_margem_cc
#                 denominator = total_faturamento_liq_cc
#                 if denominator != 0:
#                     total_margem_rel_cc = numerator / denominator 
#                 else:
#                     print(f"Aviso: Denominador zero para o índice {index} no cálculo de total_margem_rel_cc")
#             except Exception as e:
#                 print(f"Erro no cálculo de total_margem_rel_cc para o índice {index}: {str(e)}")

#         # Cria o dicionário de totais
#         totals = {
#             "total_faturamento_bruto_sc": total_faturamento_sc,
#             "total_faturamento_bruto_cc": total_faturamento_cc,
#             "total_faturamento_liq_sc": total_faturamento_liq_sc,
#             "total_faturamento_liq_cc": total_faturamento_liq_cc,
#             "total_margem_sc": total_margem_sc,
#             "total_margem_cc": total_margem_cc,
#             "total_volume_sc": total_volume_sc,
#             "total_volume_cc": total_volume_cc,
#             "total_margem_rel_sc": total_margem_rel_sc,
#             "total_margem_rel_cc": total_margem_rel_cc
#         }

#         return create_cards(totals)
#     except Exception as e:
#         print(f"Erro ao atualizar cards: {str(e)}")
#         raise PreventUpdate

# Callback para baixar a tabela em Excel
@callback(
    Output("download-excel-catlote", "data"),
    Input("btn-download-excel-catlote", "n_clicks"),
    State("table-simulation-catlote", "rowData"),
    prevent_initial_call=True
)
def handle_excel_download_catlote(n_clicks, row_data):
    if n_clicks is None or not row_data:
        return None

    df = pd.DataFrame(row_data)

    return dcc.send_data_frame(df.to_excel, "catlote_simulation_data.xlsx", index=False)

# Callback para recalcular a tabela
@callback(
    Output('table-simulation-catlote', 'rowData', allow_duplicate=True),
    Output('cards-catlote-container', 'children', allow_duplicate=True),
    State("catlote-variables-store", "data"),
    Input('table-simulation-catlote', 'cellValueChanged'),
    Input('table-simulation-catlote', 'rowData'),
    prevent_initial_call=True
)
def handle_recalculate(stored_data, cellValueChanged,  table_data):

    if cellValueChanged:
        # print("Cell value changed:", cellValueChanged)
        # print("Cell value changed:", cellValueChanged[0]["oldValue"])
        # print("Cell value changed:", cellValueChanged[0]["value"])
        # print("Cell value changed:", cellValueChanged[0]["colId"])

        # print("Cell value changed:", cellValueChanged[0]["rowId"])
        # print("Cell value changed:", cellValueChanged[0]["rowIndex"])

        new_values = {
            "new_value": cellValueChanged[0]["value"],
            "old_value": cellValueChanged[0]["oldValue"],
            "changed_col_name": cellValueChanged[0]["colId"],
            "row_index": cellValueChanged[0]["rowIndex"]
        }

        if isinstance(stored_data, str):
            stored_data_ajusted = deserialize_json(stored_data)
        else:
            stored_data_ajusted = stored_data

        calculated_data = calculate_catlote(
            catlote_inputs=stored_data_ajusted,
            catlote_data_products=table_data,
            new_values=new_values,
        )

        return calculated_data['table'].to_dict('records'), create_cards(calculated_data["totals"])
    return no_update

# Callback para abrir/fechar o modal de confirmação
@callback(
    Output("modal-confirm-approval-catlote", "is_open"),
    Input("button-approval-simulation-catlote", "n_clicks"),
    Input("btn-cancel-approval", "n_clicks"),
    State("modal-confirm-approval-catlote", "is_open"),
    prevent_initial_call=True,
)
def toggle_approval_modal(approval_clicks, cancel_clicks, is_open):
    triggered_id = ctx.triggered_id
    if triggered_id == "button-approval-simulation-catlote" and approval_clicks:
        return True
    if triggered_id == "btn-cancel-approval" and cancel_clicks:
        return False
    return is_open

# Callback para enviar os dados da tabela para aprovação
@callback(
    Output("modal-confirm-approval-catlote", "is_open", allow_duplicate=True),
    Output("toast-approval-catlote", "is_open", allow_duplicate=True),
    Output("toast-approval-catlote", "header", allow_duplicate=True),
    Output("toast-approval-catlote", "children", allow_duplicate=True),
    Input('btn-confirm-approval', 'n_clicks'),
    State('table-simulation-catlote', 'rowData'),
    State("store-token", "data"),
    prevent_initial_call=True,
)
def handle_approval(n_clicks, table_data, user_data):
    if not n_clicks or n_clicks == 0:
        raise PreventUpdate

    try:
        print("enviando catlote para aprovação")
        variables_to_send = {
            "user_token": user_data["access_token"],
            "table_data": table_data,
        }
        send_to_approval("catlote", variables_to_send)
        return False, True, _("Sucesso"), _("Enviado para aprovação com sucesso.")
    except Exception as e:
        print(f"Erro ao enviar para aprovação: {str(e)}")
        return False, True, _("Erro"), _("Ocorreu um erro ao enviar para aprovação.")

# allow_duplicate=True é necessário pois múltiplos callbacks escrevem no mesmo Output
@callback(
    Output("toast-approval-catlote", "is_open", allow_duplicate=True),
    Output("toast-approval-catlote", "header", allow_duplicate=True),
    Output("toast-approval-catlote", "children", allow_duplicate=True),
    Input("button-approval-accept-catlote", "n_clicks"),
    Input("button-approval-reject-catlote", "n_clicks"),
    State("table-simulation-catlote", "rowData"),
    State("store-token", "data"),
    prevent_initial_call=True
)
def handle_approval_status(accept_clicks, reject_clicks, table_data, user_data):
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
            "target_table": "catlote",
        }

        update_approval_status(variables_to_send)
        return True, status_text, _("Status alterado para {}").format(status_text)

    except Exception as e:
        print(f"Erro ao processar aprovação: {str(e)}")
        return True, _("Erro"), _("Erro ao processar aprovação: {}").format(str(e))
