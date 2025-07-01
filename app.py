import os
import dash
import dash_bootstrap_components as dbc
from dotenv import load_dotenv
from dash import Input, Output, dcc, html, callback, State, no_update
from dash.exceptions import PreventUpdate
from components.Sidebar  import Sidebar
from pages.login.login_page import login_page
from pages.change_password.change_password_page import change_password_page
from pages.command_center.command_center_page import command_center_page
from pages.price_architecture.price_architecture_page import price_architecture_page
from pages.price_architecture.price_sim_architecture_page import price_sim_architecture_page
from pages.optimization.optimization_page import optimization_page
from pages.catlote.catlote_page import catlote_page
from pages.catlote.catlote_simulation_page import catlote_simulation_page
from pages.approvals.approval_page import approval_page
from pages.approvals_requests.approvals_requests_pages import approval_requests_page
from pages.captain.captain_page import captain_page
from pages.captain.captain_simulation_page import captain_simulation_page
from pages.captain_margin.captain_margin_page import captain_margin_page
from pages.strategy.strategy_page import strategy_page
from pages.marketing.marketing_page import marketing_page
from pages.delta.delta_page import delta_page
from pages.buildup.buildup_page import buildup_page
from styles import MAIN_CONTENT_STYLE, MAIN_CONTAINER_STYLE, MAIN_TITLE_STYLE
from static_data.constants import LIST_OF_ALLOWERD_ROLES_TO_ACCESS_APPROVAL
from translations import setup_translations, _, update_language

load_dotenv(override=True)

ENVIRONMENT = os.getenv('ENVIRONMENT', 'prod')

app = dash.Dash(
    __name__,
    external_stylesheets=[dbc.themes.BOOTSTRAP],
    suppress_callback_exceptions=True,
    title="GM Pricing Software",
)

server = app.server

app.config.suppress_callback_exceptions = True

content = html.Div(
    id="page-content",
    style=MAIN_CONTENT_STYLE
)

login_content = html.Div(login_page)

command_center_content = html.Div([
    html.H1(_("Command Center"), style=MAIN_TITLE_STYLE),
    html.Div(command_center_page)
])

price_content = html.Div([
    html.H1(_("Arquitetura de Preço"), style=MAIN_TITLE_STYLE),
    html.Div(price_architecture_page)
])

simulation_content = html.Div([
    html.H1(_("Simulação do Resultado"), style=MAIN_TITLE_STYLE),
    html.Div(price_sim_architecture_page)
])

optimization_content = html.Div(optimization_page)

catlote_content = html.Div([
    html.H1(_("CatLote Desconto"), style=MAIN_TITLE_STYLE),
    html.Div(catlote_page)
])

catlote_simulation_content = html.Div([
    html.H1(_("Simulação - CatLote"), style=MAIN_TITLE_STYLE),
    html.Div(catlote_simulation_page)
])

approval_content= html.Div(approval_page)

approval_requests_content = html.Div(approval_requests_page)

captain_content = html.Div([
    html.H1(_("Capitão"), style=MAIN_TITLE_STYLE),
    html.Div(captain_page)
])

captain_simulation_content = html.Div([
    html.H1(_("Simulação do Capitão"), style=MAIN_TITLE_STYLE),
    html.Div(captain_simulation_page)
])

strategy_content = html.Div([
    html.H1(_("Estratégia Comercial"), style=MAIN_TITLE_STYLE),
    html.Div(strategy_page)
])

marketing_content = html.Div([
    html.H1(_("Posicionamento de Mercado"), style=MAIN_TITLE_STYLE),
    html.Div(marketing_page)
])

captain_margin_content = html.Div([
    html.H1(_("Margem do Capitão"), style=MAIN_TITLE_STYLE),
    html.Div(captain_margin_page)
])

delta_content = html.Div([
    html.H1(_("Delta Preço"), style=MAIN_TITLE_STYLE),
    html.Div(delta_page)
])

buildup_content = html.Div([
    html.H1(_("Build Up"), style=MAIN_TITLE_STYLE),
    html.Div(buildup_page)
])

PUBLIC_ROUTES = {
    "/command-center": command_center_content,
    "/price": price_content,
    "/price-simulation": simulation_content,
    "/optimization": optimization_content,
    "/catlote": catlote_content,
    "/catlote-simulation": catlote_simulation_content,
    "/captain": captain_content,
    "/captain-simulation": captain_simulation_content,
    "/strategy": strategy_content,
    "/marketing": marketing_content,
    "/captain-margin": captain_margin_content,
    "/delta": delta_content,
    "/buildup": buildup_content,
}

def router(role):
    if role in LIST_OF_ALLOWERD_ROLES_TO_ACCESS_APPROVAL:
        return {
            **PUBLIC_ROUTES,
            "/approval": approval_content,
        }
    else:
        return {
            **PUBLIC_ROUTES,
            "/approval-requests": approval_requests_content,
        }

app.layout = html.Div([
    dcc.Location(id='url', refresh=True),
    dcc.Store(id='store-token', storage_type='session'),
    dcc.Store(id='captain-variables-store', storage_type='session'),
    dcc.Store(id='store-language', storage_type='local'),
    dcc.Store(id='catlote-variables-store', storage_type='session'),
    html.Div(id='page-content')
])

# Callback to update translations when language changes
@callback(
    Output("dummy-output", "children"),
    Input("store-language", "data"),
    prevent_initial_call=False
)
def update_translations_on_change(language):
    if language:
        update_language(language)
    return no_update

@app.callback(
    Output("page-content", "children"),
    [
        Input("url", "pathname"),
        Input("store-token", "data")
    ]
)
def render_page_content(pathname, user):

    user_role = None

    if(user):
        user_role = user.get('role_name', 'Usuário')

    if pathname == "/":
        return login_content
    if pathname == "/change-password":
        return change_password_page
    return html.Div([
        Sidebar,
        html.Div(
            children=router(user_role).get(pathname, html.Div([
                html.H1(_("404: Not found"), className="text-danger"),
                html.Hr(),
                # html.P(_("The pathname {} was not recognised...")).format(pathname),
            ])),
            style=MAIN_CONTENT_STYLE
        )
    ], style=MAIN_CONTAINER_STYLE)

if __name__ == "__main__":
    app.run(debug=ENVIRONMENT == "prod")
