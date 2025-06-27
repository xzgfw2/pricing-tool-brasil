import os
import shutil
import dash_bootstrap_components as dbc
from dash import Dash, dcc, html, callback, State, dash_table, Input, Output, no_update
from static_data.constants import LIST_OF_ALLOWERD_ROLES_TO_ACCESS_APPROVAL
from styles import SVG_STYLE, NAV_ITEM_STYLE, CONTAINER_LANGUAGE_SELECTOR_STYLE, LANGUAGE_SELECTOR_STYLE
from components.Avatar import create_avatar
from translations import _

AVAILABLE_LANGUAGES = [
    {'label': 'PT-BR', 'value': 'pt_BR'},
    {'label': 'EN', 'value': 'en'},
    {'label': 'ES', 'value': 'es'}
]

def create_nav_item(label, icon_path, href, user):

    user_role = user.get('role_name', 'Usuário')

    if href == "/approval" and user_role not in LIST_OF_ALLOWERD_ROLES_TO_ACCESS_APPROVAL:
        return None
    elif href == "/approval-requests" and user_role in LIST_OF_ALLOWERD_ROLES_TO_ACCESS_APPROVAL:
        return None
    else:
        return dbc.NavLink(
            html.Div(
                [
                    html.Img(src=icon_path, style=SVG_STYLE),
                    html.Span(f" {label}")
                ],
                style=NAV_ITEM_STYLE
            ),
        href=href,
        active="exact",
    )

logo = html.Div(
    html.Img(src="./assets/logo/logo_gradient.jpg"),
    style={"textAlign": "center"},
)

command_center_item = (_("Command Center"), "./assets/icons/command_center.svg", "/command-center")
catlote_item = (_("CatLote Desc"), "./assets/icons/catlote.svg", "/catlote")
optimization_item = (_("Otimização de Preços"), "./assets/icons/optimization.svg", "/optimization")
price_architecture_item = (_("Arquitetura de Preço"), "./assets/icons/price.svg", "/price")
approval_item = (_("Aprovações"), "./assets/icons/approval.svg", "/approval")
approval_requests_item = (_("Requisições de Aprovação"), "./assets/icons/approval.svg", "/approval-requests")

submenu = [
    html.Li(
        html.Div(
            [
                html.Img(src="./assets/icons/settings.svg", style=SVG_STYLE),
                html.Span(_("Configurações"), style={"marginLeft": "5px"}),
            ],
            style=NAV_ITEM_STYLE,
            className="my-1",
        ),
        id="submenu-1",
    ),
    dbc.Collapse(
        [
            dbc.NavLink(_("Capitão"), href="/captain", active="exact"),
            dbc.NavLink(_("Estratégia Comercial"), href="/strategy", active="exact"),
            dbc.NavLink(_("Mercado"), href="/marketing", active="exact"),
            dbc.NavLink(_("Margem do Capitão"), href="/captain-margin", active="exact"),
            dbc.NavLink(_("Delta Preço"), href="/delta", active="exact"),
            dbc.NavLink(_("Build Up"), href="/buildup", active="exact"),
        ],
        id="submenu-1-collapse",
    ),
]

def create_sidebar():
    return html.Div(
        [
            logo,
            html.Hr(),
            dbc.Nav(
                id="sidebar-nav",
                vertical=True,
                pills=True,
            ),
            html.Div(
                html.Hr(),
                style={'marginTop': 'auto'}
            ),
            html.Div(id="avatar-container"),
        ],
        className="sidebar",
        style={
            "display": "flex",
            "flexDirection": "column",
            "minHeight": "100vh",
        },
    )

@callback(
    Output("sidebar-nav", "children"),
    Input("store-token", "data"),
    prevent_initial_call=False,
)
def update_navbar(user_data):
    return [
        create_nav_item(*command_center_item, user=user_data),
        create_nav_item(*catlote_item, user=user_data),
        create_nav_item(*optimization_item, user=user_data),
        create_nav_item(*price_architecture_item, user=user_data),
        dbc.NavLink(submenu),
        create_nav_item(*approval_item, user=user_data),
        create_nav_item(*approval_requests_item, user=user_data),
    ]

@callback(
    Output("avatar-container", "children"),
    Input("store-token", "data"),
)
def update_avatar(user_data):
    if not user_data:
        return no_update

    user_name = f"{user_data.get('first_name', '')} {user_data.get('last_name', '')}".strip()
    user_role = user_data.get('role_name', 'Usuário')

    return create_avatar(
        name=user_name,
        role=user_role,
    )

# Callback para lidar com o logout
@callback(
    Output("url", "pathname", allow_duplicate=True),
    Output("store-token", "data", allow_duplicate=True),
    Input("logout-button", "n_clicks"),
    prevent_initial_call=True,
)
def handle_logout(n_clicks):
    if n_clicks and n_clicks > 0:

        # Limpa o cache
        cache_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "api", "cache")
        if os.path.exists(cache_dir):
            try:
                # Verifica e remove o arquivo optimization_cache.parquet primeiro
                optimization_cache = os.path.join(cache_dir, "optimization_cache.parquet")
                if os.path.exists(optimization_cache):
                    os.remove(optimization_cache)
                    print(f"Optimization cache file removed: {optimization_cache}")
                
                # Remove o diretório cache
                shutil.rmtree(cache_dir)
                print(f"Cache directory removed: {cache_dir}")
            except Exception as e:
                print(f"Error removing cache directory or optimization file: {str(e)}")

        # Limpa a session
        session_file = os.path.join(os.path.dirname(os.path.dirname(__file__)), "api", "session")
        if os.path.exists(session_file):
            try:
                os.remove(session_file)
                print(f"Session file removed: {session_file}")
            except Exception as e:
                print(f"Error removing session file: {str(e)}")

        return "/", None
    return no_update, no_update

# Callback para atualizar o idioma
# @callback(
#     Output("store-language", "data"),
#     Input("language-selector", "value"),
#     prevent_initial_call=True
# )
# def update_language_callback(selected_language):
#     if selected_language:
#         print("selected_language", selected_language)
#         update_language(selected_language)
#         return selected_language
#     return no_update

Sidebar = create_sidebar()

def toggle_collapse(n, is_open):
    if n:
        return not is_open
    return is_open

def set_navitem_class(is_open):
    if is_open:
        return "open"
    return ""

for i in [1, 2]:
    callback(
        Output(f"submenu-{i}-collapse", "is_open"),
        [Input(f"submenu-{i}", "n_clicks")],
        [State(f"submenu-{i}-collapse", "is_open")],
    )(toggle_collapse)

    callback(
        Output(f"submenu-{i}", "className"),
        [Input(f"submenu-{i}-collapse", "is_open")],
    )(set_navitem_class)
