import re
import dash_bootstrap_components as dbc
from dash import html, dcc, callback, Input, Output, State, no_update
from api.post_change_password import post_change_password
from translations import _

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
SUCCESS_MESSAGE_STYLE = {'color': 'green', 'marginTop': '1rem'}

password_regex = re.compile(
    r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@#$%^&/*-_+=()! ?"]).{8,128}$'
)

def get_layout():
    return html.Div([
        dcc.Location(id='url-change-password', refresh=True),
        dcc.Interval(id='redirect-interval', interval=4000, max_intervals=1, disabled=True),
        html.Div([
            html.Img(
                src='/assets/logo/logo_gradient.jpg',
                style=LOGO_STYLE
            ),
            dbc.Form([
                dbc.Input(
                    type="email",
                    id="email-input",
                    placeholder=_("Email"),
                    style=INPUT_STYLE
                ),
                dbc.Input(
                    type="password",
                    id="current-password-input",
                    placeholder=_("Senha atual"),
                    style=INPUT_STYLE
                ),
                dbc.Input(
                    type="password",
                    id="new-password-input",
                    placeholder=_("Nova senha"),
                    style=INPUT_STYLE
                ),
                dbc.Input(
                    type="password",
                    id="confirm-password-input",
                    placeholder=_("Confirmar nova senha"),
                    style=INPUT_STYLE
                ),
                html.Div(
                    dbc.Button(
                        [
                            dbc.Spinner(size="sm", id="change-password-spinner", spinnerClassName="d-none"),
                            html.Span(_("Mudar senha"), id="change-password-text")
                        ],
                        id="change-password-button",
                        n_clicks=0,
                        color="primary",
                        style=BUTTON_STYLE
                    ),
                    className="text-center"
                ),
                html.Div(id="change-password-output"),
                dbc.Toast(
                    id="success-toast",
                    header=_("Sucesso!"),
                    is_open=False,
                    dismissable=True,
                    duration=4000,
                    icon="success",
                    style={"position": "fixed", "top": 66, "right": 10, "width": 350},
                )
            ], style=FORM_STYLE)
        ], style=CONTAINER_STYLE)
    ])

change_password_page = html.Div([
    dbc.Spinner(
        html.Div(id="change-password-content"),
        color="primary",
    )
])

@callback(
    Output("change-password-content", "children"),
    Input("url", "pathname"),
)
def update_change_password_content(pathname):
    if pathname == "/change-password":
        return get_layout()
    return no_update

@callback(
    [
        Output("change-password-output", "children"),
        Output("change-password-spinner", "spinnerClassName"),
        Output("change-password-text", "className"),
        Output("success-toast", "is_open"),
        Output("success-toast", "children"),
        Output("redirect-interval", "disabled")
    ],
    Input("change-password-button", "n_clicks"),
    [
        State("email-input", "value"),
        State("current-password-input", "value"),
        State("new-password-input", "value"),
        State("confirm-password-input", "value")
    ],
    prevent_initial_call=True
)
def change_password(n_clicks, email, current_password, new_password, confirm_password):
    if not n_clicks:
        return no_update, "d-none", "", False, "", True

    spinner_class = "d-none"
    button_class = ""

    if not all([email, current_password, new_password, confirm_password]):
        return html.Div(_("Por favor, preencha todos os campos"), style=ERROR_MESSAGE_STYLE), spinner_class, button_class, False, "", True

    if new_password != confirm_password:
        return html.Div(_("As senhas não coincidem"), style=ERROR_MESSAGE_STYLE), spinner_class, button_class, False, "", True

    if not password_regex.match(new_password):
        error_msg = _("A senha deve conter pelo menos 8 caracteres, incluindo maiúsculas, minúsculas, números e caracteres especiais (@#$%^&/*-_+=()!?\")")
        return html.Div(error_msg, style=ERROR_MESSAGE_STYLE), spinner_class, button_class, False, "", True

    variables_to_send = {
        "user_email": email,
        "current_password": current_password,
        "new_password": new_password
    }

    try:
        spinner_class = ""
        button_class = "d-none"
        response = post_change_password(variables_to_send)

        if response is None:
            return html.Div(_("Erro verifique as informações enviadas"), style=ERROR_MESSAGE_STYLE), "d-none", "", False, "", True

        if response[0]["status"] == 'error':
            return html.Div(_("Erro verifique as informações enviadas"), style=ERROR_MESSAGE_STYLE), "d-none", "", False, "", True

        if response[0]["status"] == 'success':
            success_message = html.Div(_("Senha alterada com sucesso! Redirecionado para login"))
            return None, "d-none", "", True, success_message, False  # Enable the interval for redirect

    except Exception as e:
        return html.Div(str(e), style=ERROR_MESSAGE_STYLE), "d-none", "", False, "", True

    return no_update, "d-none", "", False, "", True

@callback(
    Output("url-change-password", "pathname"),
    Input("redirect-interval", "n_intervals"),
    prevent_initial_call=True
)
def redirect_after_success(n_intervals):
    if n_intervals is not None and n_intervals > 0:
        return "/"
    return no_update
