import dash_bootstrap_components as dbc
from dash import html
from styles import CONTAINER_BUTTONS_STYLE

def container_approval_reject_buttons(table):

    return html.Div(
        children=[
            html.Div(
                children=[
                    dbc.Button(
                        "Recusar", 
                        id=f"button-approval-reject-{table}",
                        color="danger",
                        disabled=False,
                        n_clicks=0
                    ),
                    dbc.Tooltip(
                        "Clique para Recusar",
                        target=f"button-approval-reject-{table}",
                        placement="top",
                    ),
                ],
            ),
            html.Div(
                children=[
                    dbc.Button(
                        "Aprovar", 
                        id=f"button-approval-accept-{table}",
                        color="success",
                        disabled=False,
                        n_clicks=0
                    ),
                    dbc.Tooltip(
                        "Clique para Aprovar",
                        target=f"button-approval-accept-{table}",
                        placement="top",
                    ),
                ],
            ),
        ],
        style=CONTAINER_BUTTONS_STYLE,
    )
