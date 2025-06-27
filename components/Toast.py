from dash import html
import dash_bootstrap_components as dbc
from styles import TOAST_STYLE

def Toast(
        id=None,
        toast_message=None,
        header=None,
        icon="primary",
    ):
    """
    Create a customizable Toast component using Dash Bootstrap Components.

    This component displays a dismissable toast notification that is initially closed.
    It can be configured with a custom message, header, icon, and duration.

    Parameters:
    ----------
    id : str, optional
        The unique identifier for the Toast component. Used for callbacks and referencing.
    toast_message : str, optional
        The message content displayed within the body of the Toast.
    header : str, optional
        The header text displayed at the top of the Toast.
    icon : str, optional, default="primary"
        The icon color used for the Toast. It can be any valid Bootstrap color such as
        "primary", "secondary", "success", "danger", "warning", "info", "light", or "dark".

    Returns:
    -------
    html.Div
        A Div element wrapping the Toast component, ready to be used in a Dash layout.
    """
    return html.Div(
        dbc.Toast(
            id=id,
            key=id,
            header=header,
            children=toast_message,
            icon=icon,
            is_open=False,
            dismissable=True,
            duration=4000,
            style=TOAST_STYLE,
        ),
    )
