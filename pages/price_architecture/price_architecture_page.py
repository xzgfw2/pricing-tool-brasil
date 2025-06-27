from dash import dash_table, Dash, dcc, html, callback, callback_context, State, Input, Output, no_update
import dash_bootstrap_components as dbc
from dash.dash_table.Format import Format, Group
import pandas as pd
import json
from api.api_get_var_arq_price import get_var_arq_price
from api.send_variables_to_price_simulation import send_variables_to_price_simulation
from components.Modal import create_modal
from utils.deserialize_json import deserialize_json
from static_data.helper_text import helper_text
from components.Helper_button_with_modal import create_help_button_with_modal
from utils.user_has_permission_to_edit import user_has_permission_to_edit
from styles import (
    CONTAINER_BUTTONS_STYLE,
    CONTAINER_TABLE_STYLE,
    TABLE_HEADER_STYLE,
    TABLE_SIZE_STYLE,
    TABLE_CELL_STYLE,
    DROPDOWN_CONTAINER_STYLE,
    DROPDOWN_STYLE,
    TABLE_TITLE_STYLE,
    CONTAINER_HELPER_BUTTON_STYLE,
)
from translations import _, setup_translations

VARIABLES_CATEGORIES = {
    "ano frota": _("Ano Frota"),
    "aplicacoes": _("Aplicações"),
    "elasticidade": _("Elasticidade"),
    "estoque": _("Estoque"),
    "frota": _("Frota"),
    "marca": _("Marca"),
    "price index": _("Price Index"),
}

def create_data_table(id_suffix=""):
    is_price_index = id_suffix == "price index"
    is_non_editable_rule = id_suffix in ["elasticidade", "marca"]
    
    return dash_table.DataTable(
        id=f'table-price-architecture-{id_suffix}',
        style_data_conditional=[
            {
                "if": {
                    "filter_query": '{data} = "marca" || {data} = "elasticidade"',
                    "column_id": "regra"
                },
                "backgroundColor": "lightgrey",
                "color": "rgb(222, 226, 230)",
                "pointerEvents": "none"
            },
            {"if": {"column_id": "tabela"}, "textAlign": "center", "textTransform": "capitalize"},
            {"if": {"column_id": "porcentagem"}, "textAlign": "right"},
            {"if": {"column_id": "regra"}, "textAlign": "right"},
        ] + ([
            {
                "if": {"column_id": col},
                "backgroundColor": "rgb(222, 226, 230)",
                "color": "black",
                "pointerEvents": "none"
            }
            for col in (["porcentagem", "regra"] if is_price_index else ["regra"] if is_non_editable_rule else [])
        ]),
        style_header=TABLE_HEADER_STYLE,
        style_cell=TABLE_CELL_STYLE,
        sort_action="native",
        sort_mode="multi",
        column_selectable="single",
        page_action="native",
        filter_action="native",
    )

def create_category_card(category_id, category_name):
    return dbc.Card([
        dbc.CardHeader(
            dbc.Button(
                category_name,
                id=f"btn-collapse-{category_id}",
                color="primary",
                style={
                    "width": "100%", 
                    "backgroundColor": "transparent", 
                    "color": "black",
                    "display": "flex",
                    "justify-content": "center"
                },
                #className="category-button",
                n_clicks=0,
            )
        ),
        dbc.Collapse(
            dbc.CardBody([
                create_data_table(category_id)
            ]),
            id=f"collapse-{category_id}",
            is_open=False,
        )
    ], className="mb-3")

modal_footer = dbc.Stack(
    [
        dbc.Button(
            _("Não"),
            id="button-cancel-simulation",
            color="secondary",
            n_clicks=0
        ),
        dbc.Button(
            _("Sim"),
            id="button-confirm-simulation",
            color="success",
            n_clicks=0
        ),
    ],
    id="modal-simulation",
    direction="horizontal",
    gap=3,
    class_name="mx-auto",
)

modal = create_modal(
    modal_id="modal-price-architecture",
    modal_title=_("Efetuar simulação ?"),
    modal_body_id="modal-price-architecture-body",
    modal_footer=modal_footer,
)

def get_layout(pathname, user_data):
    return [
        dcc.Location(id="url-simulation", refresh=True),
        dcc.Store(id='stored-variables', storage_type="session"),
        dcc.Store(id='stored-category-states', storage_type="session"),
        html.Div(
            [
                html.Div(className="flexible-spacer"),
                create_help_button_with_modal(
                    modal_title=helper_text["price"]["title"],
                    modal_body=helper_text["price"]["description"],
                ),
            ], style=CONTAINER_HELPER_BUTTON_STYLE,
        ),
        # Botões de ação
        dbc.Row([
            dbc.Col([
                dbc.ButtonGroup([
                    dbc.Button(_("Expandir Todos"), id="btn-expand-all", color="primary", outline=True),
                    dbc.Button(_("Colapsar Todos"), id="btn-collapse-all", color="primary", outline=True),
                    dbc.Button(
                        _("Simulação"), 
                        id="button-simulation",
                        color="success",
                        disabled=False if user_has_permission_to_edit(pathname, user_data) else True,
                    ),
                ], className="mb-3")
            ])
        ]),
        dbc.Row([
            dbc.Col([
                html.Div([
                    create_category_card(cat_id, cat_name)
                    for cat_id, cat_name in VARIABLES_CATEGORIES.items()
                ])
            ])
        ]),
        modal
    ]

price_architecture_page = html.Div([
    dbc.Spinner(
        html.Div(id="price-content"),
        color="primary",
        size="lg",
        fullscreen=True,
    )
])

# Callback para renderizar o conteúdo da página
@callback(
    Output("price-content", "children"),
    Input("url", "pathname"),
    Input("store-token", "data"),
    Input("store-language", "data"),
)
def update_price_content(pathname, user_data, language):

    global _
    _ = setup_translations(language)

    if pathname == "/price":
        return get_layout(pathname, user_data)
    return no_update

# Callbacks para lidar com o estado dos cards
@callback(
    [Output(f"collapse-{cat_id}", "is_open") for cat_id in VARIABLES_CATEGORIES.keys()],
    [
        Input("btn-expand-all", "n_clicks"),
        Input("btn-collapse-all", "n_clicks"),
    ] + [Input(f"btn-collapse-{cat_id}", "n_clicks") for cat_id in VARIABLES_CATEGORIES.keys()],
    [State(f"collapse-{cat_id}", "is_open") for cat_id in VARIABLES_CATEGORIES.keys()]
)
def toggle_cards(*args):
    ctx = callback_context
    if not ctx.triggered:
        return [False] * len(VARIABLES_CATEGORIES)
    
    button_id = ctx.triggered[0]["prop_id"].split(".")[0]
    states = args[-len(VARIABLES_CATEGORIES):]
    
    if button_id == "btn-expand-all":
        return [True] * len(VARIABLES_CATEGORIES)
    elif button_id == "btn-collapse-all":
        return [False] * len(VARIABLES_CATEGORIES)
    else:
        for i, cat_id in enumerate(VARIABLES_CATEGORIES.keys()):
            if button_id == f"btn-collapse-{cat_id}":
                new_states = list(states)
                new_states[i] = not states[i]
                return new_states
    return states

# Callback para lidar com os dados das tabelas
@callback(
    [Output(f"table-price-architecture-{cat_id}", "data") for cat_id in VARIABLES_CATEGORIES.keys()],
    [Output(f"table-price-architecture-{cat_id}", "columns") for cat_id in VARIABLES_CATEGORIES.keys()],
    [
        Input(f"collapse-{cat_id}", "is_open") for cat_id in VARIABLES_CATEGORIES.keys()
    ] + [Input("stored-variables", "data")]
)
def update_tables(*args):
    ctx = callback_context
    if not ctx.triggered:
        return [None] * len(VARIABLES_CATEGORIES) * 2

    triggered_id = ctx.triggered[0]["prop_id"].split(".")[0]
    collapse_states = args[:-1]  # Estados dos collapses
    stored_data = args[-1]  # Último argumento é stored_variables
    
    if triggered_id == "stored-variables" or any(collapse_states):
        # Inicializa dicionário para armazenar dados por categoria
        categorized_data = {cat_id: [] for cat_id in VARIABLES_CATEGORIES.keys()}
        
        # Se não houver dados armazenados, carrega dados para cada categoria expandida
        if not stored_data:
            for cat_id, is_open in zip(VARIABLES_CATEGORIES.keys(), collapse_states):
                if is_open:
                    try:
                        df = get_var_arq_price(cat_id.lower())
                        if not df.empty:
                            categorized_data[cat_id] = df.to_dict("records")
                    except Exception as e:
                        print(f"Erro ao carregar dados para {cat_id}: {e}")
        else:
            # Se houver dados armazenados, usa eles
            stored_dict = deserialize_json(stored_data)
            if isinstance(stored_dict, list):
                # Se for uma lista, processa cada item
                for row in stored_dict:
                    category = row.get("tabela", "").lower()
                    if category in categorized_data:
                        categorized_data[category].append(row)
            elif isinstance(stored_dict, dict):
                # Se for um dicionário, usa diretamente
                categorized_data = stored_dict

        # Prepara as colunas para cada tabela
        all_columns = []
        for cat_id in VARIABLES_CATEGORIES.keys():
            columns = [
                {"name": _("ID"), "id": "id", "editable": False},
                {"name": _("Grupo"), "id": "nome"},
                {"name": _("%"), "id": "porcentagem", "editable": True, "type": "numeric"},
                {"name": _("Regra"), "id": "regra", "editable": True},
                {"name": _("Produtos"), "id": "produtos"},
                {"name": _("Margem"), "id": "total_margem", "type": "numeric", "format": Format().group(True)},
                {"name": _("Margem %"), "id": "margem_porcentagem"},
            ]
            all_columns.append(columns)

        # Retorna os dados e colunas
        table_data = []
        for cat_id in VARIABLES_CATEGORIES.keys():
            table_data.append(categorized_data[cat_id])

        return table_data + all_columns

    # Se nenhuma tabela estiver expandida, retorna None para todas
    return [None] * len(VARIABLES_CATEGORIES) * 2

# Callback para lidar com o modal de simulação
@callback(
    Output("modal-price-architecture", "is_open"),
    Output("modal-price-architecture-body", "children"),
    Output("modal-simulation", "children"),
    [
        Input("button-simulation", "n_clicks"),
        Input("button-confirm-simulation", "n_clicks"),
        Input("button-cancel-simulation", "n_clicks")
    ],
    [
        State("modal-price-architecture", "is_open"),
    ]
)
def handle_modal_simulation(click_simulation, click_confirm, click_cancel, is_open):
    ctx = callback_context
    if not ctx.triggered:
        return False, None, dbc.Stack(
            [
                dbc.Button(_("Não"), id="button-cancel-simulation", color="secondary", n_clicks=0),
                dbc.Button(_("Sim"), id="button-confirm-simulation", color="success", n_clicks=0),
            ],
            direction="horizontal",
            gap=3,
            class_name="mx-auto",
        )
    
    button_id = ctx.triggered[0]["prop_id"].split(".")[0]
    
    default_buttons = dbc.Stack(
        [
            dbc.Button(_("Não"), id="button-cancel-simulation", color="secondary", n_clicks=0),
            dbc.Button(_("Sim"), id="button-confirm-simulation", color="success", n_clicks=0),
        ],
        direction="horizontal",
        gap=3,
        class_name="mx-auto",
    )
    
    if button_id == "button-simulation":
        return True, html.Div(_("A simulação pode levar vários minutos para ser efetuada")), default_buttons
    
    if button_id == "button-cancel-simulation":
        return False, None, default_buttons
    
    if button_id == "button-confirm-simulation":
        spinner = dbc.Spinner(
            color="primary",
            size="lg",
            type="border",
        )
        return True, html.Div(_("A simulação pode levar vários minutos para ser efetuada")), spinner
    
    return False, None, default_buttons

# Callback para lidar com os dados de simulação
@callback(
    Output("url-simulation", "pathname"),
    Input("button-confirm-simulation", "n_clicks"),
    [State(f"table-price-architecture-{cat_id}", "data") for cat_id in VARIABLES_CATEGORIES.keys()],
    State("store-token", "data"),
    prevent_initial_call=True
)
def handle_simulation_data(n_clicks, *args):
    if not n_clicks:
        return no_update
        
    # Extract data from args
    table_data = args[:-1]  # All but the last argument
    user_data = args[-1]    # Last argument is user_data
    
    # Create a dictionary to store the table data
    table_values = {}
    
    # Get data from each table
    for table_data, category_id in zip(table_data, VARIABLES_CATEGORIES.keys()):
        if table_data:
            # Extract values from table data
            values = []
            for row in table_data:
                if row.get('porcentagem') is not None:  # Only include rows with percentage values
                    values.append({
                        'id': row.get('id', ''),
                        'nome': row.get('nome', ''),
                        'porcentagem': row.get('porcentagem', ''),
                        'regra': row.get('regra', '')
                    })
            if values:
                table_values[category_id] = values

    variables_to_send = {
        "user_token": user_data["access_token"],
        "table_data": table_values
    }

    response = send_variables_to_price_simulation(variables_to_send)

    if response is True:
        return "/price-simulation"
    
    return no_update
