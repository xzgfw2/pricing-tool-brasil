from dash import html

def create_button(
        id=None,
        text=None,
        color="primary",
        disabled=False,
    ):
    """
    Create a customizable Button component using Dash Bootstrap Components.

    This component creates a styled button that can be configured with a custom text, color, and ID.

    Parameters:
    ----------
    id : str, optional
        The unique identifier for the Button component. Used for callbacks and referencing.
    text : str, optional
        The text content displayed within the button.
    color : str, optional, default="primary"
        The color of the button. It can be any valid Bootstrap color such as
        "primary", "secondary", "success", "danger", "warning", "info", "light", or "dark".
    disabled : bool, optional, default=False
        Whether the button is disabled or not.

    Returns:
    -------
    html.Button
        A Button element ready to be used in a Dash layout.
    """
    return html.Button(
        id=id,
        children=text,
        disabled=disabled,
        className=f"btn btn-{color}",
    )
