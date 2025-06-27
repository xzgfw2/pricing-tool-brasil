import dash_bootstrap_components as dbc
from dash import html
from pages.catlote.catlote_simulation_page import catlote_simulation_page
from pages.optimization.optimization_page import optimization_page
from pages.price_architecture.price_sim_architecture_page import price_sim_architecture_page
from pages.captain.captain_simulation_page import captain_simulation_page
from pages.strategy.strategy_page import strategy_page
from pages.marketing.marketing_page import marketing_page
from pages.captain_margin.captain_margin_page import captain_margin_page
from pages.delta.delta_page import delta_page
from pages.buildup.buildup_page import buildup_page
from components.Helper_button_with_modal import create_help_button_with_modal
from static_data.helper_text import helper_text
from styles import MAIN_TITLE_STYLE, CONTAINER_HELPER_BUTTON_STYLE
from translations import _

helper_button = html.Div(
    create_help_button_with_modal(
        modal_title=helper_text["approval"]["title"],
        modal_body=helper_text["approval"]["description"],
    ),
    style=CONTAINER_HELPER_BUTTON_STYLE,
)

container_title = html.Div([
    html.H1(_("Aprovações"), style=MAIN_TITLE_STYLE),
    helper_button
], className="container-title")

approval_page = html.Div([
    container_title,
    dbc.Tabs([
        dbc.Tab(catlote_simulation_page, label=_("CatLote")),
        dbc.Tab(optimization_page, label=_("Otimização de Preços")),
        dbc.Tab(price_sim_architecture_page, label=_("Arquitetura de Preço")),
        dbc.Tab(captain_simulation_page, label=_("Capitão")),
        dbc.Tab(strategy_page, label=_("Estratégia")),
        dbc.Tab(marketing_page, label=_("Mercado")),
        dbc.Tab(captain_margin_page, label=_("Margem do Capitão")),
        dbc.Tab(delta_page, label=_("Delta Preço")),
        dbc.Tab(buildup_page, label=_("Build Up")),
    ])
])
