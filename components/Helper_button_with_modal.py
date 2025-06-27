from dash import html, callback, Input, Output, State
import dash_bootstrap_components as dbc
from components.Modal import create_modal
from translations import _

def create_help_button_with_modal(
    modal_title,
    modal_body,
    id="help-button",
    tooltip_text=_("Informações sobre a página"),
    modal_footer=dbc.Button(
        _("Fechar"), 
        id="close-help-modal", 
        className="ms-auto"
    ),
):
    return html.Div([
        html.Img(
            id=id,
            src="./assets/icons/help.svg",
            style={
                "cursor": "pointer",
                "width": "32px",
            }
        ),
        dbc.Tooltip(
            tooltip_text,
            target=id,
            placement="top",
        ),
        create_modal(
            modal_title=modal_title,
            modal_id=f"modal-{id}",
            # modal_id="modal-help-button",
            modal_body=modal_body,
            modal_footer=modal_footer,
        ),
    ])

# Callback para abrir e fechar o modal de ajuda
@callback(
    Output("modal-help-button", "is_open"),
    [
        Input("help-button", "n_clicks"),
        Input("close-help-modal", "n_clicks"),
    ],
    State("modal-help-button", "is_open"),
)
def toggle_help_modal(help_clicks, close_clicks, is_open):
    if help_clicks or close_clicks:
        return not is_open
    return is_open
