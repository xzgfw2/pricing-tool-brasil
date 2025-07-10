import dash
import dash_bootstrap_components as dbc
import pandas as pd
from datetime import datetime, timedelta
from dash import dcc, html, callback, Input, Output, State, no_update
from dash.exceptions import PreventUpdate
from dash.dash_table import DataTable
from utils.serialize_to_json import serialize_to_json
from api.api_get_catlote import get_catlote
from static_data.helper_text import helper_text
from utils.user_has_permission_to_edit import user_has_permission_to_edit
from components.Helper_button_with_modal import create_help_button_with_modal
from styles import (
    CONTAINER_BUTTONS_STYLE,
    TABLE_HEADER_STYLE,
    TABLE_CELL_STYLE,
    CONTAINER_HELPER_BUTTON_STYLE,
    MAIN_TITLE_STYLE
)
from translations import _, setup_translations

CUSTOM_HEADER_STYLE = {
    **TABLE_HEADER_STYLE,
    'height': 'auto',
    'minHeight': '50px',
    'whiteSpace': 'normal',
    'textAlign': 'center',
    'fontWeight': 'bold',
    'padding': '6px',
    'fontSize': '12px'
}

CUSTOM_CELL_STYLE = {
    **TABLE_CELL_STYLE,
    'height': 'auto',
    'minHeight': '35px',
    'whiteSpace': 'normal',
    'padding': '6px',
    'fontSize': '12px',
    'fontWeight': 'normal'
}

EDITABLE_CELL_STYLE = {
    'backgroundColor': '#e6f3ff',
    'border': '1px solid #ccc'
}

EDITABLE_COLUMNS = [
    'date_inicial', 'date_final', 
    'F1', 'F2', 'F3', 'F4',
    'P1', 'P2', 'P3', 'P4'
]

STYLE_TABLE = {
    "borderSpacing": "0px 5px"
}

TAB_BAR_STYLE = {
    "marginBottom": "20px"
}

ALERT_STYLE = {
    "marginBottom": "20px",
    "font-weight": "bold"
}

def define_columns(filter_promotion="0"):

    def allow_editable(filter_promotion):
        return True if filter_promotion == "1" else False

    return [
        {"name": ["Catlote", ""], "id": "CATLOT1", "type": "numeric", "editable": False},
        {
            "name": [_("Data Inicial"), ""],
            "id": "date_inicial",
            "type": "text",
            "editable": allow_editable(filter_promotion),
            "presentation": "input"
        },
        {
            "name": [_("Data Final"), ""], 
            "id": "date_final", 
            "type": "text",
            "editable": allow_editable(filter_promotion),
            "presentation": "input"
        },
        {"name": [_("Quantidade"), "1"], "id": "F1", "type": "numeric", "editable": allow_editable(filter_promotion)},
        {"name": [_("Quantidade"), "2"], "id": "F2", "type": "numeric", "editable": allow_editable(filter_promotion)},
        {"name": [_("Quantidade"), "3"], "id": "F3", "type": "numeric", "editable": allow_editable(filter_promotion)},
        {"name": [_("Quantidade"), "4"], "id": "F4", "type": "numeric", "editable": allow_editable(filter_promotion)},
        {"name": [_("Desconto %"), "1"], "id": "D1", "type": "text", "editable": allow_editable(filter_promotion)},
        {"name": [_("Desconto %"), "2"], "id": "D2", "type": "text", "editable": allow_editable(filter_promotion)},
        {"name": [_("Desconto %"), "3"], "id": "D3", "type": "text", "editable": allow_editable(filter_promotion)},
        {"name": [_("Desconto %"), "4"], "id": "D4", "type": "text", "editable": allow_editable(filter_promotion)},
        {"name": [_("Participação %"), _("Atual 1")], "id": "P1", "type": "text", "editable": False},
        {"name": [_("Participação %"), _("Atual 2")], "id": "P2", "type": "text", "editable": False},
        {"name": [_("Participação %"), _("Atual 3")], "id": "P3", "type": "text", "editable": False},
        {"name": [_("Participação %"), _("Atual 4")], "id": "P4", "type": "text", "editable": False},
        {"name": [_("Participação %"), _("Estim. 1")], "id": "E1", "type": "text", "editable": allow_editable(filter_promotion)},
        {"name": [_("Participação %"), _("Estim. 2")], "id": "E2", "type": "text", "editable": allow_editable(filter_promotion)},
        {"name": [_("Participação %"), _("Estim. 3")], "id": "E3", "type": "text", "editable": allow_editable(filter_promotion)},
        {"name": [_("Participação %"), _("Estim. 4")], "id": "E4", "type": "text", "editable": allow_editable(filter_promotion)}
    ]

# Estilo condicional para células
def change_style_data_conditional(filter_promotion):
    return [
        {
            'if': {'column_id': col},
            'textAlign': 'right'
        } for col in ['F1', 'F2', 'F3', 'F4', 'D1', 'D2', 'D3', 'D4', 'P1', 'P2', 'P3', 'P4', 'E1', 'E2', 'E3', 'E4']
    ] + [
        {
            "if": {"column_id": col["id"]},
            "backgroundColor": "rgb(250, 250, 250)",
            "color": "darkgrey",
            "pointerEvents": "none"  # Desabilita edição
        } for col in define_columns(filter_promotion) if not col["editable"]
    ] + [
        {
            "if": {"column_id": col["id"]},
            **EDITABLE_CELL_STYLE
        } for col in define_columns(filter_promotion) if col["editable"]
    ]

def create_buttons():
    return html.Div(
        [
            dbc.Button(
                _("Simulação"),
                id="button-simulation-catlote",
                disabled=True,
                color="success",
                n_clicks=0,
            ),
            dbc.Tooltip(
                _("Simular impactos"),
                target="button-simulation-catlote",
                placement="top",
            )
        ],
        style=CONTAINER_BUTTONS_STYLE,
    )

helper_button = html.Div(
    create_help_button_with_modal(
        modal_title=helper_text["catlote"]["title"],
        modal_body=helper_text["catlote"]["description"],
    ), style=CONTAINER_HELPER_BUTTON_STYLE,
)

def get_layout(pathname, user_data):

    def create_table(filter_promotion, user_data):
        catlote_data = get_catlote(filter_promotion)
        data_dict = catlote_data.to_dict('records')

        def format_values(data_dict):
            for row in data_dict:
                # Formatar colunas de Quantidade com separador de milhar
                for i in range(1, 5):
                    col_f = f'F{i}'
                    if col_f in row and row[col_f] is not None:
                        row[col_f] = "{:,.0f}".format(float(row[col_f])).replace(",", ".")

                # Formatar colunas de Desconto
                for i in range(1, 5):
                    col_d = f'D{i}'
                    if col_d in row and row[col_d] is not None:
                        row[col_d] = f"{int(float(row[col_d]) * 100)}%"

                # Formatar colunas de Participação Atual
                for i in range(1, 5):
                    col_p = f'P{i}'
                    if col_p in row and row[col_p] is not None:
                        row[col_p] = f"{int(float(row[col_p]) * 100)}%"

                # Formatar colunas de Participação Estimada
                for i in range(1, 5):
                    col_e = f'E{i}'
                    if col_e in row and row[col_e] is not None:
                        row[col_e] = f"{int(float(row[col_e]) * 100)}%"

            return data_dict

        formated_data = format_values(data_dict)


        validation_alert = dbc.Alert(
            _("Erro na validação"), 
            id="validation-message",
            color="danger",
            style=ALERT_STYLE,
            is_open=False,
        )

        data_table = DataTable(
            id="catlote-simulation-table",
            columns=define_columns(filter_promotion),
            data=formated_data,
            merge_duplicate_headers=True,
            row_selectable=False if filter_promotion == "0" or not user_has_permission_to_edit(pathname, user_data) else "multi",
            style_header=CUSTOM_HEADER_STYLE,
            style_cell=CUSTOM_CELL_STYLE,
            style_data_conditional=change_style_data_conditional(filter_promotion),
            style_table=STYLE_TABLE,
        )

        return html.Div([validation_alert, data_table])

    def create_tabs():
        return dbc.Tabs(
        [
            dbc.Tab(create_table(filter_promotion="0", user_data=user_data), label=_("Sem Promoção"), tab_id="tab-0"),
            dbc.Tab(create_table(filter_promotion="1", user_data=user_data), label=_("Com Promoção"), tab_id="tab-1"),
        ],
        style=TAB_BAR_STYLE,
        active_tab="tab-0"
    )

    return [
        dcc.Location(id="url-catlote", refresh=True),
        html.Div([
            html.H1(_('CatLote Desconto'), style=MAIN_TITLE_STYLE),
            helper_button
        ], className="container-title"),
        html.Div(
            [
                create_buttons(),
                create_tabs(),
            ]
        ),
    ]

catlote_page = html.Div([
    dbc.Spinner(
        html.Div(id="catlote-content"),
        color="primary",
        size="lg",
        fullscreen=True,
    )
])

# Callback para renderizar o conteúdo da página
@callback(
    Output("catlote-content", "children"),
    Input("url", "pathname"),
    State("store-token", "data"),
    Input("store-language", "data"),
)
def update_marketing_content(pathname, user_data, language):

    global _
    _ = setup_translations(language)

    if pathname == "/catlote":
        return get_layout(pathname, user_data)
    return no_update

# Callback para validação da soma dos valores Estim_1 a Estim_4
@callback(
    [
        Output("validation-message", "children"),
        Output("validation-message", "is_open"),
        Output("validation-message", "color"),
        Output("button-simulation-catlote", "disabled", allow_duplicate=True),
    ],
    [
        Input('catlote-simulation-table', 'data'),
        Input('catlote-simulation-table', 'selected_rows'),
    ],
    prevent_initial_call=True
)
def validate_estim_columns(data, selected_rows):
    if not selected_rows or not data:
        return "", False, "danger", True

    ctx = dash.callback_context
    if not ctx.triggered:
        return "", False, "danger", True

    try:
        for idx in selected_rows:
            row = data[idx]
            estim_values = [
                float(str(row.get(f'E{i}', '0')).replace('%', '').strip() or 0)
                for i in range(1, 5)
            ]

            total = sum(estim_values)

            if abs(total - 100) > 0.01:  # Usando 0.01 para lidar com arredondamentos
                diff = 100 - total
                message = [
                    html.Div([
                        html.Strong(_("Soma atual: "), className="me-1"),
                        f"{total:.1f}%"
                    ], className="mb-1"),
                    html.Div([
                        html.Strong(
                            f"{_('Faltam') if diff > 0 else _('Excedem')} ",
                            className="me-1"
                        ),
                        f"{abs(diff):.1f}% " + _('para atingir 100%')
                    ])
                ]
                return message, True, "warning", True

    except Exception as e:
        print(f"Erro na validação: {e}")
        return _("Erro ao validar os valores"), True, "danger", True

    return html.Div([
        html.I(className="fas fa-check me-2"),
        _("Valores corretos! Soma = 100%")
    ]), True, "success", False

# Callback para atualizar a data final automaticamente
@callback(
    Output('catlote-simulation-table', 'data'),
    [Input('catlote-simulation-table', 'data'),
    Input('catlote-simulation-table', 'selected_rows')]
)
def update_end_date(data, selected_rows):
    if not selected_rows or not data:
        return data
    
    ctx = dash.callback_context
    if not ctx.triggered:
        return data

    try:
        for idx in selected_rows:
            row = data[idx]
            if isinstance(row, dict) and 'date_inicial' in row and row['date_inicial']:
                try:
                    # Tenta primeiro o formato brasileiro
                    try:
                        start_date = datetime.strptime(str(row['date_inicial']), '%d/%m/%Y')
                    except ValueError:
                        # Se falhar, tenta o formato ISO
                        start_date = datetime.strptime(str(row['date_inicial']), '%Y-%m-%d')
                    
                    end_date = start_date + timedelta(days=30)
                    data[idx]['date_final'] = end_date.strftime('%d/%m/%Y')
                except Exception as e:
                    print(f"Erro ao processar data: {e}")
                    continue
    except Exception as e:
        print(f"Erro no callback update_end_date: {e}")
        return data

    return data

# Callback para habilitar ou desabilitar o botão de simulação
@callback(
    Output('button-simulation-catlote', 'disabled'),
    Input('catlote-simulation-table', 'selected_rows')
)
def toggle_simular_button(selected_rows):
    return not bool(selected_rows)  # Disable button if no rows are selected

def convert_columns_to_numeric(df):
    cols_to_convert = ['E1', 'E2', 'E3', 'E4', 'D1', 'D2', 'D3', 'D4', 'P1', 'P2', 'P3', 'P4']

    for col in cols_to_convert:
        df[col] = df[col].astype(str)
        df[col] = df[col].str.replace("%", "")
        df[col] = df[col].astype(str).replace("nan", "0").fillna(0)
        df[col] = df[col].astype(float)
        df[col] = df[col] / 100
    return df

# Callback para salvar os dados dos Catlotes selecionados na Store.
@callback(
    Output('catlote-variables-store', 'data'),
    Input('catlote-simulation-table', 'selected_rows'),
    Input('catlote-simulation-table', 'data'),
    Input('button-simulation-catlote', 'n_clicks')
)
def store_catlote_values(selected_rows, table_data, n_clicks):
    if n_clicks > 0 and selected_rows:

        df = pd.DataFrame(table_data)
        table_with_converted_data = convert_columns_to_numeric(df)
        selected_catlotes = [table_with_converted_data.loc[row].to_dict() for row in selected_rows]

        return serialize_to_json(selected_catlotes)
    return no_update

# Callback para redirecionar para a pagina de simulacao
@callback(
    Output("url", "pathname"),
    Input("button-simulation-catlote", "n_clicks"),
    prevent_initial_call=True
)
def redirect_simulation(n_clicks):
    if n_clicks:
        return "/catlote-simulation"
    return dash.no_update

# Callback para preencher datas automaticamente quando selecionar catlote
@callback(
    Output('catlote-simulation-table', 'data', allow_duplicate=True),
    [Input('catlote-simulation-table', 'selected_rows')],
    [State('catlote-simulation-table', 'data')],
    prevent_initial_call=True
)
def auto_fill_dates(selected_rows, data):
    if not selected_rows or not data:
        raise PreventUpdate

    ctx = dash.callback_context
    if not ctx.triggered:
        raise PreventUpdate

    try:
        for idx in selected_rows:
            if not data[idx].get('date_inicial') and not data[idx].get('date_final'):
                today = datetime.now()
                end_date = today + timedelta(days=30)

                data[idx]['date_inicial'] = today.strftime('%d/%m/%Y')
                data[idx]['date_final'] = end_date.strftime('%d/%m/%Y')
    except Exception as e:
        print(f"_('Erro ao preencher datas automaticamente: '){e}")
        return data

    return data

# Callback para formatar valores de participação automaticamente
@callback(
    Output('catlote-simulation-table', 'data', allow_duplicate=True),
    Input('catlote-simulation-table', 'data_timestamp'),
    State('catlote-simulation-table', 'data'),
    State('catlote-simulation-table', 'active_cell'),
    prevent_initial_call=True
)
def format_participation_values(timestamp, data, active_cell):
    if not active_cell:
        return no_update

    column_id = active_cell['column_id']
    row = active_cell['row']

    try:
        if column_id.startswith('P'):
            value = data[row][column_id]
            if value:
                clean_value = value.replace('%', '').strip()
                try:
                    float(clean_value)
                    data[row][column_id] = f"{clean_value}%"
                except ValueError:
                    pass

        elif column_id.startswith('E'):
            value = data[row][column_id]
            if value:
                clean_value = value.replace('%', '').strip()
                try:
                    float(clean_value)
                    data[row][column_id] = f"{clean_value}%"
                except ValueError:
                    pass

    except Exception as e:
        print(f"Erro ao formatar valor: {e}")

    return data
