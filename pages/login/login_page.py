import dash_bootstrap_components as dbc
from dash import html, dcc, callback, Input, Output, State, no_update
import os
import shutil
from api.user_login import user_login
from styles import SVG_STYLE, CONTAINER_LANGUAGE_SELECTOR_STYLE, LANGUAGE_SELECTOR_STYLE
from translations import setup_translations, update_language

CONTAINER_STYLE = {
    'display': 'flex',
    'flexDirection': 'column',
    'alignItems': 'center',
    'justifyContent': 'center',
    'height': '100vh',
    'backgroundColor': '#f8f9fa',
}

FORM_STYLE = {
    'width': '100%',
    'maxWidth': '400px',
    'padding': '2rem',
    'backgroundColor': 'white',
    'borderRadius': '10px',
    'boxShadow': '0 4px 6px rgba(0, 0, 0, 0.1)',
    'display': 'flex',
    'flexDirection': 'column',
    'alignItems': 'center',
}

INPUT_STYLE = {
    'marginBottom': '1rem',
}

BUTTON_STYLE = {
    'width': '100%',
    'backgroundColor': '#0d6efd',
    'borderColor': '#0d6efd',
}

LOGO_STYLE = {
    'width': '200px',
    'marginBottom': '2rem',
}

ERROR_MESSAGE_STYLE = {'color': 'red', 'marginTop': '1rem'}
SUCESS_MESSAGE_STYLE = {'color': 'green', 'marginTop': '1rem'}

validation_message = html.Div("Por favor, insira usuário e senha", style=ERROR_MESSAGE_STYLE)
error_message = html.Div("Usuário ou senha inválidos", style=ERROR_MESSAGE_STYLE)
success_message = html.Div("Login realizado com sucesso!", style=SUCESS_MESSAGE_STYLE)

AVAILABLE_LANGUAGES = [
    {'label': 'PT-BR', 'value': 'pt_BR'},
    {'label': 'EN', 'value': 'en'},
    {'label': 'ES', 'value': 'es'}
]

login_page = html.Div([
    dcc.Location(id='url-login', refresh=True),
    html.Div([
        html.Img(
            src='/assets/logo/logo_gradient.jpg',
            style=LOGO_STYLE
        ),
        dbc.Form([
            html.Div(
                [
                    html.Img(src="./assets/icons/language.svg", style=SVG_STYLE),
                    dcc.Dropdown(
                        id='language-selector',
                        options=AVAILABLE_LANGUAGES,
                        value='pt_BR',
                        clearable=False,
                        className='multi-language',
                        style=LANGUAGE_SELECTOR_STYLE
                    ),
                ],
                style=CONTAINER_LANGUAGE_SELECTOR_STYLE,
            ),
            dbc.Input(
                type="text",
                id="email-input",
                placeholder="E-mail",
                style=INPUT_STYLE
            ),
            dbc.Input(
                type="password",
                id="password-input",
                placeholder="Password",
                style=INPUT_STYLE
            ),
            dbc.Button(
                [
                    dbc.Spinner(
                        size="sm",
                        color="light",
                        id="login-spinner",
                        spinnerClassName="d-none"
                    ),
                    html.Span("Login", id="login-text")
                ],
                id="login-button",
                n_clicks=0,
                color="primary",
                style=BUTTON_STYLE
            ),
            html.Div(id="login-output")
        ], style=FORM_STYLE)
    ], style=CONTAINER_STYLE),
])

@callback(
    Output("url", "pathname", allow_duplicate=True),
    Output("login-output", "children"),
    Output("store-token", "data", allow_duplicate=True),
    Output("login-spinner", "spinnerClassName"),
    Output("login-text", "className"),
    Output("store-language", "data", allow_duplicate=True),
    Input("login-button", "n_clicks"),
    State("email-input", "value"),
    State("password-input", "value"),
    State("language-selector", "value"),
    prevent_initial_call=True,
)
def login(n_clicks, email, password, language):
    if n_clicks > 0:
        if not email or not password:
            return no_update, validation_message, no_update, "d-none", "", no_update

        update_language(language)

        try:
            user = user_login({
                "user_email": email,
                "user_password": password
            })

            if user and user.get("access_token") is not None:
                return "/command-center", success_message, user, "d-none", "", language
            else:
                return no_update, error_message, no_update, "d-none", "", no_update
                
        except Exception as e:
            print(f"Erro durante o login: {str(e)}")
            error_msg = html.Div([
                html.I(className="fas fa-exclamation-circle me-2"),
                f"Erro ao conectar: {str(e)}"
            ], className="text-danger")
            return no_update, error_msg, no_update, "d-none", "", no_update

    return no_update, no_update, no_update, "d-none", "", no_update

@callback(
    [Output("login-spinner", "spinnerClassName", allow_duplicate=True),
    Output("login-text", "className", allow_duplicate=True)],
    Input("login-button", "n_clicks"),
    prevent_initial_call=True
)
def toggle_loading_state(n_clicks):
    if n_clicks > 0:
        return "", "d-none"
    return "d-none", ""
