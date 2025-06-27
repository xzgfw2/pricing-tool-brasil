import dash
import dash_bootstrap_components as dbc
import dash_ag_grid as dag
from dash import html, dcc, callback, Input, Output, State, no_update
from api.api_get_command_center_async import get_all_command_center_data
from styles import CONTAINER_BUTTONS_STYLE, TABLE_TITLE_STYLE, TABLE_NOTE_PARAGRAPH, CONTAINER_HELPER_BUTTON_STYLE
from static_data.helper_text import helper_text
from components.Helper_button_with_modal import create_help_button_with_modal
from datetime import datetime, timedelta
from translations import setup_translations, _

# Cache para armazenar os dados
_cache = {}
_cache_timestamp = None
CACHE_DURATION = timedelta(minutes=720)

def get_cached_data():
    """
    Obtém dados do cache se estiverem válidos, caso contrário busca novos dados
    """
    global _cache, _cache_timestamp
    current_time = datetime.now()
    
    if _cache and _cache_timestamp and current_time - _cache_timestamp < CACHE_DURATION:
        return _cache
    
    # Se não estiver no cache ou cache expirado, busca novos dados
    _cache = get_all_command_center_data()
    _cache_timestamp = current_time
    return _cache

def get_command_center_data():
    """
    Obtém todos os dados do command center com cache
    """
    return get_cached_data()

# Estilo para o container dos cards
cards_container_style = {
    "display": "grid",
    "gridTemplateColumns": "repeat(auto-fit, minmax(300px, 1fr))",
    "gap": "20px",
    "padding": "20px",
}

# Definindo cores personalizadas para os cards
card_colors = {
    "zero_cost": "#1e90ff",
    "negative_cost": "#1e90ff",
    "low_cost_high_margin": "#1e90ff",
    "low_cost_negative_margin": "#1e90ff",
    "low_cost_zero_margin": "#1e90ff",
    "low_cost_high_sales": "#1e90ff",
    "low_price_negative_margin": "#1e90ff",
    "negative_margin_and_others": "#1e90ff",
    "price_gm": "#1e90ff",
    "price_research": "#1e90ff",
    "update_cpc": "#1e90ff",
}

def columns_misc(_):
    return [
        {"headerName": "CPC1_3_6", "field": "cpc1_3_6"},
        {"headerName": _("Part Number"), "field": "part_number"},
        {"headerName": _("Descrição"), "field": "descricao"},
        {"headerName": _("Volume (12 meses)"), "field": "vol_12_meses"},
        {"headerName": _("Custo Médio (unit)"), "field": "custo_medio_unit"},
        {"headerName": _("Preço SAP (atual)"), "field": "preco_sap_atual"},
    ]

def columns_price_gm(_):
    return [
        {"headerName": _("Data Consulta"), "field": "data_consulta"},
        {"headerName": _("Published CPC"), "field": "published_cpc"},
        {"headerName": _("Part Number"), "field": "part_number"},
        {"headerName": _("Preço Concess C/ Imposto"), "field": "preco_concess_c_imposto"},
        {"headerName": _("Preço Público"), "field": "preco_publico"},
        {"headerName": _("Volume (12 meses)"), "field": "vol_12_meses"},
    ]

def columns_update_cpc(_):
    return [
        {"headerName": _("Data Consulta"), "field": "data_consulta"},
        {"headerName": _("CPC1_3_6"), "field": "cpc1_3_6"},
        {"headerName": _("Volume (12 meses)"), "field": "volume_12meses"},
        {"headerName": _("Tab Capitão"), "field": "tab_capitao"},
        {"headerName": _("Tab Estratégia"), "field": "tab_estrategia"},
        {"headerName": _("Tab Margem"), "field": "tab_margem"},
        {"headerName": _("Tab Delta Preço"), "field": "tab_delta_preco"},
    ]

def sections(_):
    return [
        {
            "id": "zero_cost",
            "title": _("Custo Médio Zerado"),
            "description": _("Itens com custo médio zerado que podem afetar o modelo de precificação"),
            "data_key": "zero_cost",
            "columns": columns_misc(_),
        },
        {
            "id": "negative_cost",
            "title": _("Custo Negativo"),
            "description": _("Itens com custo total negativo (influência do costs factor)"),
            "data_key": "negative_cost",
            "columns": columns_misc(_),
        },
        {
            "id": "low_cost_high_margin",
            "title": _("Baixo Custo Alta Margem"),
            "description": _("Custo médio < R$ 0,50 e margem > 90%"),
            "data_key": "low_cost_high_margin",
            "columns": columns_misc(_),
        },
        {
            "id": "low_cost_negative_margin",
            "title": _("Baixo Custo Margem Negativa"),
            "description": _("Custo médio < R$ 0,50 e margem negativa"),
            "data_key": "low_cost_negative_margin",
            "columns": columns_misc(_),
        },
        {
            "id": "low_cost_zero_margin",
            "title": _("Baixo Custo Margem Zero"),
            "description": _("Custo médio < R$ 0,50 e margem zerada"),
            "data_key": "low_cost_zero_margin",
            "columns": columns_misc(_),
        },
        {
            "id": "low_cost_high_sales",
            "title": _("Baixo Custo Alta Venda"),
            "description": _("Custo médio < R$ 0,50 com volume anual acima de 1000"),
            "data_key": "low_cost_high_sales",
            "columns": columns_misc(_),
        },
        {
            "id": "low_price_negative_margin",
            "title": _("Preço Baixo Margem Negativa"),
            "description": _("Preço SAP menor que R$ 1,00 e margem negativa"),
            "data_key": "low_price_negative_margin",
            "columns": columns_misc(_),
        },
        {
            "id": "negative_margin_and_others",
            "title": _("Margem Negativa e Outros Casos"),
            "description": _("Análise de casos diversos com margem negativa"),
            "data_key": "negative_margin_and_others",
            "columns": columns_misc(_),
        },
        {
            "id": "price_gm",
            "title": _("Preços GM"),
            "description": _("Preço Público (Varejo) menor que Preço Concess (Distribuidor)"),
            "data_key": "price_gm",
            "columns": columns_price_gm(_),
        },
        {
            "id": "update_cpc",
            "title": _("Atualizar CPC"),
            "description": _("Atualizar tabelas de parâmetros para simulações"),
            "data_key": "update_cpc",
            "columns": columns_update_cpc(_),
        },
    ]

# Criação das tabelas
def create_table(table_id, data, columns):
    return dag.AgGrid(
        id=table_id,
        rowData=data.to_dict("records") if data is not None else [],
        columnDefs=columns,
        defaultColDef={
            "resizable": True, 
            "sortable": True, 
            "filter": True,
        },
        dashGridOptions={
            "pagination": True, 
            "paginationAutoPageSize": True,
            "enableCellTextSelection": True, # Permite seleção de texto
            "enableRangeSelection": True,  # Habilita seleção de intervalo
        },
    )

# Layout principal
command_center_page = html.Div(
    id="main-content",
    children=[
        dbc.Spinner(
            html.Div(id="command-center-content"),
            color="primary",
            size="lg",
            fullscreen=True,
        )
    ]
)

# Callback para lidar com a renderização da página
@callback(
    Output("command-center-content", "children"),
    Input("url", "pathname"),
    Input("store-language", "data"),
)
def update_command_center_content(pathname, language):

    global _
    _ = setup_translations(language)

    if pathname == "/command-center":
        table_data = get_command_center_data()
        return [
            html.Div(
                [
                    html.Div(className="flexible-spacer"),
                    create_help_button_with_modal(
                        modal_title=helper_text["command_center"]["title"],
                        modal_body=helper_text["command_center"]["description"],
                    ),
                ], style=CONTAINER_HELPER_BUTTON_STYLE,
            ),
            html.Div(
                [html.Div(
                    dbc.Card(
                        dbc.CardBody([
                            html.Div([
                                html.H4(section["title"], style={"color": "white", "marginBottom": "10px"}),
                                html.Div(
                                    str(len(table_data[section['data_key']])),
                                    style={
                                        "position": "absolute",
                                        "top": "-10px",
                                        "right": "-10px",
                                        "backgroundColor": "white",
                                        "color": "#0066CC",
                                        "borderRadius": "50%",
                                        "border": "2px solid #0066CC",
                                        "width": "38px",
                                        "height": "38px",
                                        "display": "flex",
                                        "alignItems": "center",
                                        "justifyContent": "center",
                                        "fontSize": "0.95rem",
                                        "fontWeight": "bold",
                                        "transform": "translate(40%, -40%)"
                                    }
                                )
                            ], style={"position": "relative"}),
                            html.P(
                                section["description"],
                                style={"color": "white", "flex": "1"}
                            ),
                        ], className="d-flex flex-column"),
                        style={"height": "100%", "cursor": "pointer"},
                        color=card_colors[section["id"]],
                        class_name="h-100",
                    ),
                    id=f"card-{section['id']}",
                    n_clicks=0
                ) for section in sections(_)],
                id="cards-container",
                style=cards_container_style
            ),
            html.Div([
                html.Div([
                    dbc.Button(
                        _("← Voltar"),
                        id="btn-back",
                        color="secondary",
                        className="me-2 mb-3",
                        n_clicks=0
                    ),
                    html.Div([
                        dbc.Button(
                            _("Copiar"),
                            id="btn-copy",
                            color="success",
                            className="me-2 mb-3",
                            n_clicks=0
                        ),
                        dbc.Button(
                            _("Baixar Excel"),
                            id="btn-download-excel",
                            color="success",
                            className="mb-3",
                            n_clicks=0
                        ),
                        dcc.Download(id="download-excel")
                    ]),
                ], 
                style={
                    "display": "flex",
                    "justifyContent": "space-between",
                    "width": "100%"
                }),
                html.Div(id="table-content")
            ], 
            id="table-container",
            className="d-none"),
        ]
    return no_update

@callback(
    [Output("cards-container", "style"),
    Output("table-container", "style"),
    Output("table-content", "children")],
    [Input(f"card-{section['id']}", "n_clicks") for section in sections(_)] + 
    [Input("btn-back", "n_clicks")],
    [State("cards-container", "style")],
    prevent_initial_call=True
)
def toggle_content(*args):
    ctx = dash.callback_context
    if not ctx.triggered:
        return cards_container_style, {"display": "none"}, None
    
    button_id = ctx.triggered[0]["prop_id"].split(".")[0]
    
    if button_id == "btn-back":
        return cards_container_style, {"display": "none"}, None
    
    # Encontra a seção correspondente ao card clicado
    section_id = button_id.replace("card-", "")
    section = next((s for s in sections(_) if s["id"] == section_id), None)
    
    if section:
        table_id = f"table-{section['id']}"
        table_data = get_command_center_data()
        return (
            {"display": "none"},
            {"display": "block"},
            html.Div([
                html.Div([
                    html.H4(
                        section["title"],
                        style={
                            **TABLE_TITLE_STYLE,
                            "width": "100%", 
                            "marginBottom": "10px"
                        }
                    ),
                    html.P(
                        section["description"],
                        style={
                            **TABLE_NOTE_PARAGRAPH,
                            "width": "100%", 
                            "marginBottom": "20px"
                        }
                    ),
                    create_table(table_id, table_data[section["data_key"]], section["columns"])
                ], style={"width": "100%"})
            ])
        )
    
    return cards_container_style, {"display": "none"}, None

# Callback para copiar dados para o clipboard
@callback(
    Output("btn-copy", "children"),
    Input("btn-copy", "n_clicks"),
    State("table-content", "children"),
    prevent_initial_call=True
)
def handle_copy_to_clipboard(n_clicks, table_content):
    if n_clicks is None or table_content is None:
        return "Copiar"

    table_id = table_content["props"]["children"][0]["props"]["children"][2]["props"]["id"]
    section_id = table_id.replace("table-", "")
    
    # Find the corresponding section
    section = next((s for s in sections(_) if s["id"] == section_id), None)
    
    if section:
        table_data = get_command_center_data()
        df = table_data[section["data_key"]]
        # Corrige colunas datetime com timezone
        for col in df.select_dtypes(include=["datetime64[ns, UTC]"]).columns:
            df[col] = df[col].dt.tz_localize(None)
        df.to_clipboard(index=False)
        return "✓ Copiado!"
    
    return "Copiar"

# Callback para download em Excel
@callback(
    Output("download-excel", "data"),
    Input("btn-download-excel", "n_clicks"),
    State("table-content", "children"),
    prevent_initial_call=True,
)
def handle_excel_download(n_clicks, table_content):
    if n_clicks is None or table_content is None:
        return None
    
    # Extract table ID from the table content to identify which section it belongs to
    table_id = table_content["props"]["children"][0]["props"]["children"][2]["props"]["id"]
    section_id = table_id.replace("table-", "")
    
    # Find the corresponding section
    section = next((s for s in sections(_) if s["id"] == section_id), None)
    
    if section:
        table_data = get_command_center_data()
        df = table_data[section["data_key"]]
        # Corrige colunas datetime com timezone
        for col in df.select_dtypes(include=["datetime64[ns, UTC]"]).columns:
            df[col] = df[col].dt.tz_localize(None)
        return dcc.send_data_frame(df.to_excel, f"{section['id']}_data.xlsx", index=False)
