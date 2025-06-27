from dash import html, dcc, callback, Input, Output, State, no_update
import dash_bootstrap_components as dbc

def create_avatar(name, role="User", image_url=None, user_data=None):
    """
    Create an avatar component with user information
    
    Args:
        name (str): User's name
        role (str): User's role/position
        image_url (str, optional): URL to user's profile image
        user_data (dict, optional): User data
    """
    default_image = "./assets/icons/avatar.svg"
    
    if name:
        return html.Div([
            html.Div([
                html.Img(
                    src=image_url or default_image,
                    style={
                        "width": "30px",
                        "height": "30px",
                        "borderRadius": "50%",
                        "marginRight": "10px"
                    }
                ),
                html.Div([
                    html.Div(
                        html.Span(name),
                        className="nav-link span",
                        style={"fontWeight": "bold"}
                    ),
                    html.Div(
                        html.Span(role),
                        className="nav-link span",
                        style={"color": "var(--text-secondary)"}
                    )
                ], style={"flex": 1}),
                html.Div(
                    html.Img(
                        src="./assets/icons/logout.svg",
                        id="logout-button",
                        style={
                            "width": "20px",
                            "height": "20px",
                            "cursor": "pointer",
                            "marginLeft": "10px",
                        }
                    ),
                    title="Sair",
                    className="logout-icon nav-link",
                )
            ], style={
                "display": "flex",
                "alignItems": "center",
                "padding": "10px",
                "borderTop": "1px solid var(--border-color)",
                "backgroundColor": "var(--background-secondary)",
                "marginTop": "auto"
            })
        ], className="mt-auto")
