from dash import Input, Output, callback, html, dcc, State
import dash
import dash_bootstrap_components as dbc
import dash_ag_grid as dag
from components.Card import Card
from api.get_initial_data_configs import get_initial_data_configs
from api.api_post_captain_variables import post_captain_variables
from utils.serialize_to_json import serialize_to_json
from utils.handle_data import handle_data
from static_data.helper_text import helper_text
from components.Helper_button_with_modal import create_help_button_with_modal
from utils.user_has_permission_to_edit import user_has_permission_to_edit
from styles import CONTAINER_CARD_STYLE, CONTAINER_BUTTONS_STYLE, CAPTAIN_CARD_INSIDE_STYLE, HELPER_MESSAGE, TABLE_TITLE_STYLE, CONTAINER_HELPER_BUTTON_STYLE
from translations import _, setup_translations

def columns():
    return [
    {"headerName": _("CPC1_3_6"), "field": "cpc1_3_6"},
    {"headerName": _("Rank"), "field": "rank"},
    {"headerName": _("Part Number"), "field": "part_number"},
    {"headerName": _("Descrição"), "field": "descricao"},
    {"headerName": _("Critério"), "field": "criterio"},
    {"headerName": _("Repres. Volume"), "field": "vol"},
    {"headerName": _("Repres. Faturamento"), "field": "gross_sales"},
    {"headerName": _("Data Inclusão"), "field": "data_inclusao"},
    {"headerName": _("Penetração"), "field": "penetracao"},
    {"headerName": _("Capitão (atual)"), "field": "capitao"},
]

def get_captain_data(cpc):
    table_data = get_initial_data_configs("captain", cpc=cpc)
    
    if table_data is None or table_data.empty:
        row_data = []
    else:
        row_data = table_data
    
    table_variables = get_initial_data_configs("captain_variables").to_dict("records")[0]
    return row_data, table_variables

def get_layout(pathname, user_data):
    
    cpc = user_data.get('cpc1_3_6_list')
    row_data, table_variables = get_captain_data(cpc)
    formated_data = handle_data(row_data, decimal_places=2, date_format='%m-%d-%y')

    table = dag.AgGrid(
        id='table-captain',
        rowData=formated_data.to_dict("records"),
        columnDefs=columns(),
        defaultColDef={
            "sortable": True,
            "filter": True,
            "resizable": True,
            "singleClickEdit": True,
        },
        columnSize="autoSize",
        dashGridOptions={
            "pagination": True,
            "paginationPageSize": 20,
        },
        style={'height': '500px'},
    )

    return [
        html.Div(
            [
                html.Div(className="flexible-spacer"),  # Espaçador flexível
                create_help_button_with_modal(
                    modal_title=helper_text["captain"]["title"],
                    modal_body=helper_text["captain"]["description"],
                ),
            ], style=CONTAINER_HELPER_BUTTON_STYLE,
        ),
        html.Div(
            children=[
                dbc.Button(
                    [
                        _("Simulação"),  
                        dbc.Spinner(
                            size="sm",
                            color="light",
                            id="button-simulate-captain-spinner",
                            spinner_style={"display": "none"},
                        ),
                    ],
                    id="button-simulate-captain",
                    color="success",
                    disabled=False if user_has_permission_to_edit(pathname, user_data) else True,
                    n_clicks=0
                ),
                dbc.Tooltip(
                    _("Simular Capitão"),
                    target="button-simulate-captain",
                    placement="top",
                ),
            ],
            style=CONTAINER_BUTTONS_STYLE,
        ),
        html.Div(
            [
                Card(
                    title=_("Repres. Faturamento"),
                    children=dcc.Input(
                        id="input-revenue",
                        type='number',
                        value=str(table_variables['fator_gsales'] * 100),
                        min=0,
                        max=100,
                        step=1,
                        style=CAPTAIN_CARD_INSIDE_STYLE
                    )
                ),
                Card(
                    title=_("Repres. Volume"),
                    children=dcc.Input(
                        id="input-volume",
                        type='number',
                        value=str(table_variables['fator_qtd_faturada'] * 100),
                        min=0,
                        max=100,
                        step=1,
                        style=CAPTAIN_CARD_INSIDE_STYLE
                    )
                ),
                Card(
                    title=_("Repres. Penetração"),
                    children=dcc.Input(
                        id="input-market-share",
                        type='number',
                        value=str(table_variables['fator_penetracao'] * 100),
                        min=0,
                        max=100,
                        step=1,
                        style=CAPTAIN_CARD_INSIDE_STYLE
                    )
                ),
            ],
            style=CONTAINER_CARD_STYLE,
        ),
        html.Div(
            id="variable-helper-message",
            style=HELPER_MESSAGE,
        ),
        html.Div(
            [
                html.H2(
                    _("Situação atual dos capitão"),
                    style=TABLE_TITLE_STYLE
                ),
                table,
            ]
        ),
    ]

captain_page = html.Div([
    dbc.Spinner(
        html.Div(id="captain-content"),
        color="primary",
        size="lg",
        fullscreen=True,
    )
])

@callback(
    Output("captain-content", "children"),
    Input("url", "pathname"),
    Input("store-token", "data"),
    Input("store-language", "data"),
)
def update_captain_content(pathname, user_data, language):

    global _
    _ = setup_translations(language)

    if pathname == "/captain":
        return get_layout(pathname, user_data)
    return dash.no_update

# Callback para validação das variaveis
@callback(
    Output("variable-helper-message", "children"),
    [Input("input-revenue", "value"),
    Input("input-volume", "value"),
    Input("input-market-share", "value")],
)
def validate_inputs(input1, input2, input3):

    total = float(input1) + float(input2) + float(input3)

    if total > 100:
        return f"A soma dos valores é {total}, que ultrapassa o limite de 100."
    elif total < 100:
        return f"A soma dos valores é {total}, faltam {100 - total} para 100."
    else:
        # return "A soma das variáveis deve ser de 100%"
        return

# Callback para controlar a visibilidade do spinner do botão
@callback(
    Output("button-simulate-captain-spinner", "spinner_style"),
    Input("button-simulate-captain", "n_clicks"),
    prevent_initial_call=True,
)
def toggle_button_spinner(n_clicks):
    if n_clicks:
        return {"display": "inline-block", "marginLeft": "5px"}
    return {"display": "none"}

# Callback para ao clicar no botão enviar as variáveis para o back-end e redirecionamento para a página de simulação
@callback(
    Output("url", "pathname", allow_duplicate=True),
    Output("captain-variables-store", "data"),
    Input("button-simulate-captain", "n_clicks"),
    Input("input-revenue", "value"),
    Input("input-volume", "value"),
    Input("input-market-share", "value"),
    prevent_initial_call=True,
)
def redirect_to_simulation(n_clicks, revenue, volume, market_share):

    if n_clicks:

        variables = [{
            'id': 1,
            'fator_gsales': int(float(revenue)) / 100,
            'fator_qtd_faturada': int(float(volume))  / 100,
            'fator_penetracao': int(float(market_share))  / 100,
        }]

        variables_to_store = serialize_to_json({
            'fator_gsales': int(float(revenue)) / 100,
            'fator_qtd_faturada': int(float(volume))  / 100,
            'fator_penetracao': int(float(market_share))  / 100,
        })

        print("variables_to_store", variables_to_store)

        success = post_captain_variables(data_variables=variables)

        if success:
            print("success", success)
            return "/captain-simulation", variables_to_store
        else:
            print("error")
            return dash.no_update, dash.no_update
    
    return dash.no_update, dash.no_update
