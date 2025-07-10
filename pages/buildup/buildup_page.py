from datetime import datetime
import dash_ag_grid as dag
import dash_bootstrap_components as dbc
import polars as pl
import pandas as pd
from dash import Dash, dcc, html, callback, dash_table, Input, Output, State, no_update, ctx, callback_context
from itertools import product
from pages.buildup.buildup_utils import handle_raw_dataframe, reverse_raw_dataframe, merge_with_original_data, get_tax_rates, get_month_from_quarter
from pages.approvals.approval_utils import container_approval_reject_buttons
from api.get_initial_data_configs import get_initial_data_configs
from api.get_requests_for_approval import get_requests_for_approval
from api.update_approval_status import update_approval_status
from api.send_to_approval import send_to_approval
from copy import deepcopy
from components.Input import create_input
from components.Modal import create_modal
from components.Helper_button_with_modal import create_help_button_with_modal
from components.Toast import Toast
from static_data.constants import VARIABLES_QUARTER
from static_data.helper_text import helper_text
from utils.modify_column_if_other_column_changed import modify_column_if_other_column_changed
from utils.user_has_permission_to_edit import user_has_permission_to_edit
from utils.handle_nothing_to_approve import handle_nothing_to_approve
from styles import BUTTON_STYLE, CONTAINER_BUTTONS_DUAL_STYLE, CONTAINER_TABLE_BUILD_UP_STYLE, DROPDOWN_STYLE, CONTAINER_HELPER_BUTTON_STYLE, MAIN_TITLE_STYLE
from translations import _, setup_translations
from .buildup_style import *  # Temporariamente usando import * para focar nos dados

df_buildup = handle_raw_dataframe(get_initial_data_configs(process_name="buildup"))
table_fx = get_initial_data_configs(process_name="buildup_fx")

INPUT_CONFIGS = [
    {"id": "input-dealer-code", "input_type": "number", "label_text": "Dealer Code", "input_value": 45.82},
    {"id": "input-icms-st", "input_type": "number", "label_text": "ICMS ST", "input_value": 18.00},
    {"id": "input-mva-price", "input_type": "number", "label_text": "MVA + Price", "input_value": 47.19},
    {"id": "input-price-zrsd026", "input_type": "number", "label_text": "Price (ZRSD026)", "input_value": 406.573837183352},
    {"id": "input-ipi", "input_type": "number", "label_text": "IPI", "input_value": 0.00},
    {"id": "input-ipi-material-cost", "input_type": "number", "label_text": "IPI (Material Cost)", "input_value": 5.00},
    {"id": "input-icms-material-cost", "input_type": "number", "label_text": "ICMS (Material Cost)", "input_value": 18.00},
    {"id": "input-product-price-pis-cofins", "input_type": "number", "label_text": "Product Price w/ PIS/COFINS", "input_value": 175.52},
]

CURRENCY_OPTIONS = [
    {'label': 'BRL', 'value': 'BRL'},
    {'label': 'USD', 'value': 'USD'},
    {'label': 'JPY', 'value': 'JPY'},
]

def buildup_simulation_columns():
    return [
        {"name": _("Parâmetro"), "id": "field", "editable": False},
        {"name": _("Valor"), "id": "value", "editable": True}
    ]

def tab_configs():
    return [
        {"id": "base_price", "label": _("Base Price")},
        {"id": "avg_cost", "label": _("Custo Médio")},
    ]

STYLE_CONTAINER_LABEL_INPUT = {
    'width': '25%',
    'marginBottom': '5px',
    'marginBottom': '5px',
    'display': 'flex',
    'flexDirection': 'column',
    'padding': '0px 5px',
}

STYLE_LABEL = {
    'fontSize': '12px',
    'fontWeight': 'bold',
    'marginBottom': '3px',
    'color': '#333',
    'whiteSpace': 'nowrap',
    'overflow': 'hidden',
    'textOverflow': 'ellipsis'
}

STYLE_INPUT = {
    'fontSize': '12px',
    'borderRadius': '4px',
    'boxSizing': 'border-box'
}

BUILD_UPS_CODES = ["ACC CLC", "ACC DSO", "ACC MANUF", "ACD AM CLC", "ACD DSO", "ACD GM CLC", "BAT DSO", "DSO OTHERS", "GEN CLC", "GEN MANUF", "LUB CLC", "LUB DSO", "PNE DSO", "TIN DSO"]

def create_buildup_simulation_table(tab_id, buildup_type):
    return dash_table.DataTable(
        id=f'table-buildup-simulation-{tab_id}-{buildup_type}',
        columns=buildup_simulation_columns(),
        data=[],
        editable=True,
        style_table=STYLE_SIMULATION_TABLE,
        style_cell=STYLE_SIMULATION_TABLE_CELL,
        style_cell_conditional=STYLE_SIMULATION_TABLE_CELL_CONDITIONAL,
        style_header=STYLE_SIMULATION_TABLE_HEADER
    )

def create_container_inputs(tab_id, buildup_type):
    container = html.Div(
        id=f'container-inputs-{tab_id}-{buildup_type}',
        children=[
            html.Div(
                children=[
                    html.Div(
                        create_input(
                            id=input_config['id'] + '-' + tab_id + '-' + buildup_type,
                            input_type=input_config.get("input_type", "number"),
                            label_text=input_config.get("label_text", ""),
                            input_value=input_config.get("input_value", None)
                        ),
                        style=CONTAINER_INPUTS_SIZE_STYLE
                    )
                    for input_config in INPUT_CONFIGS[i:i+2]
                ],
                style=CONTAINER_INPUTS_STYLE
            )
            for i in range(0, len(INPUT_CONFIGS), 2)
        ],
        style=CONTAINER_SIMULATION_STYLE,
    )
    return container

def tab_content(tab_id, buildups_type_data, _):
    return html.Div(
            children=[
                html.Div([
                    html.Div([
                        html.H4(buildup_type.upper(), style=STYLE_BUILDUP_TITLE),
                        html.Div(
                            [
                                html.Div(
                                    [
                                        html.Label('Currency', style=STYLE_LABEL),
                                        dcc.Dropdown(
                                            id=f'input-currency-{tab_id}-{buildup_type}',
                                            options=CURRENCY_OPTIONS,
                                            value='BRL',
                                            clearable=False,
                                            style=STYLE_INPUT
                                        ),
                                    ],
                                    style=STYLE_CONTAINER_LABEL_INPUT,
                                    className="input-currency-container"
                                ),
                                html.Div([
                                    html.P("FX Rate", style=STYLE_LABEL),
                                    html.P(id=f'currency-rate-{tab_id}-{buildup_type}', style=STYLE_INPUT),
                                ],
                                    className="fx-info"
                                ),
                            ],
                            className="currency-fx-container" if tab_id == 'base_price' else "d-none"

                        ),
                        create_container_inputs(tab_id, buildup_type),
                        create_buildup_simulation_table(tab_id, buildup_type),
                    ],
                    id=f"section-{tab_id}-{buildup_type}",
                    style=STYLE_BUILDUP_SECTION)
                    for buildup_type in buildups_type_data
                ],
                style=STYLE_BUILDUP_SECTIONS_CONTAINER)
            ],
            style=STYLE_TAB_CONTENT
        )

def container_input_quarter_year(pathname):
    return html.Div([
    html.Label('Quarter / Year', style=STYLE_LABEL),
    html.Div(
        style=CONTAINER_INPUT_DATE_STYLE,
        children=[
            dcc.Dropdown(
                id='input-quarter',
                options=VARIABLES_QUARTER,
                value=VARIABLES_QUARTER[0],
                clearable=False,
                style=DROPDOWN_STYLE,
            ),
            dcc.Dropdown(
                id='input-year',
                options=sorted(map(str, table_fx['RATEYEAR'].unique().tolist()), reverse=True),
                value=str(datetime.now().year),
                clearable=False,
                style=DROPDOWN_STYLE,
            ),
        ]
    ),
], className="d-none" if pathname == "/approval" else "" )

helper_button = html.Div(
    create_help_button_with_modal(
        modal_title=helper_text["buildup"]["title"],
        modal_body=helper_text["buildup"]["description"],
    ), style=CONTAINER_HELPER_BUTTON_STYLE,
)

def approval_button():
    return (
    html.Div([
        dbc.Button(
            _("Aprovar"),
            id="button-approval-buildup",
            color="success",
            n_clicks=0,
            disabled=True,
            style=BUTTON_STYLE,
        ),
        dbc.Tooltip(
            _("Enviar para aprovação"),
            target="button-approval-buildup",
            placement="top",
        ),
    ], style=CONTAINER_BUTTONS_DUAL_STYLE,
    )
)

def define_columns(pathname, user_data, table_data):
    column_defs = []

    for col in table_data.columns:
        column_def = {
            "headerName": col,
            "field": col,
            "editable": col != "buildup_factors" and pathname != "/approval" and user_has_permission_to_edit(pathname, user_data) 
        }

        if col == "buildup_factors":
            column_def["pinned"] = "left"

        column_defs.append(column_def)

    return column_defs

def handle_buildup_data(df):
    if df is None:
        print("DataFrame é None!")
        return []

    data = []

    for index in range(len(df)):
        row = df.row(index, named=True)
        # Substituindo None por 0 em todas as colunas exceto 'buildup_factors'
        processed_row = {}
        for key, value in row.items():
            if key == 'buildup_factors':
                processed_row[key] = value
            else:
                processed_row[key] = 0.0 if value is None else value
        data.append(processed_row)

    print("data")
    print(data[0:5])

    return data

def create_buildup_factors_table(pathname, user_data, table_data):
    return html.Div(
        [
            dag.AgGrid(
                id='table-buildup-factors',
                columnDefs=define_columns(pathname, user_data, table_data),
                rowData=handle_buildup_data(table_data),
                style={'width': '100%', 'height': '500px'},
                defaultColDef={
                    "minWidth": 150,  # Largura mínima para cada coluna
                    "autoHeight": True,  # Altura automática
                },
            ),
        ],
        style=STYLE_BUILDUP_FACTORS_CONTAINER
    )

# Função auxiliar para pegar valores do DataFrame
def get_buildup_value(factor_name, df_buildup, buildup_code, default=0.0):
    """Função auxiliar para pegar valores do DataFrame principal"""
    try:
        factor_series = df_buildup['buildup_factors']
        if isinstance(factor_series, pl.Series):
            row_index = factor_series.to_list().index(factor_name)
        else:
            row_index = factor_series.index(factor_name)
            
        value = df_buildup[buildup_code][row_index]
        return float(value if value is not None else default)
    except (ValueError, KeyError, IndexError, TypeError) as e:
        print(f"Erro ao buscar {factor_name} para {buildup_code}: {str(e)}")
        return default

# def generate_parameter_rows(buildup_code):
#     """Gera as linhas da tabela de parâmetros para um buildup específico"""
#     if df_buildup is None:
#         return []
        
#     rows = []
#     try:
#         factor_list = df_buildup['buildup_factors'].to_list()
#         for i, factor in enumerate(factor_list):
#             value = df_buildup[buildup_code][i]
#             formatted_value = f"{value:.4f}" if value is not None else "0.00"
            
#             rows.append({
#                 'Parâmetro': factor,
#                 'Valor': formatted_value
#             })
#     except Exception as e:
#         print(f"Erro ao gerar linhas para {buildup_code}: {str(e)}")
        
#     return rows

def get_layout(pathname, user_data):
    
    if pathname == "/approval":
        table_data = handle_raw_dataframe(get_requests_for_approval(table="buildup"))
    else:
        table_data = handle_raw_dataframe(get_initial_data_configs(process_name="buildup"))

    if table_data is None:
        return handle_nothing_to_approve()

    buildups_type_data = table_data.columns[1:]
    header = None
    if pathname != "/approval":
        header = html.Div([
            html.H1(_('Build Up'), style=MAIN_TITLE_STYLE),
            helper_button
        ], className="container-title")

    input_container = html.Div([
        container_input_quarter_year(pathname),
        None if pathname == "/approval" else approval_button(),
    ], className="input-header")

    date_section = html.Div(
        [header, input_container],
        style=STYLE_DATE_CONTAINER
    )

    approval_controls = (
        container_approval_reject_buttons(table="buildup")
        if pathname == "/approval"
        else None
    )

    toast_approval = Toast(
        id="toast-approval-buildup",
        header=_("Aprovação"),
        toast_message=_("Enviado para aprovação"),
    )

    toast_reject = Toast(id="toast-approval-reject-buildup")

    table_or_tabs = (
        create_buildup_factors_table(pathname, user_data, table_data)
        if pathname == "/approval"
        else html.Div(
            dbc.Tabs(
                [dbc.Tab(
                    create_buildup_factors_table(pathname, user_data, table_data),
                    label=_("Fatores")
                )] +
                [
                    dbc.Tab(
                        tab_content(tab_config["id"], buildups_type_data, _),
                        label=tab_config["label"]
                    )
                    for tab_config in tab_configs()
                ],
                style=STYLE_TABS
            ),
            style=STYLE_TABS_CONTAINER
        )
    )

    return html.Div(
        children=[
            date_section,
            approval_controls,
            toast_approval,
            toast_reject,
            table_or_tabs,
        ],
        style=STYLE_PAGE_CONTAINER
    )


error_modal = dbc.Modal(
    [
        dbc.ModalHeader("Erro"),
        dbc.ModalBody(id="error-modal-body"),
        dbc.ModalFooter(
            dbc.Button("Fechar", id="close-error-modal", className="ml-auto")
        ),
    ],
    id="error-modal",
    centered=True,
)

modal_confirm_approval = create_modal(
    modal_id="modal-confirm-approval-buildup",
    modal_title="Solicitar Aprovação",
    modal_body=html.P("Tem certeza que deseja enviar para aprovação?"),
    modal_footer=html.Div([
        dbc.Button("Não", id="btn-cancel-approval", color="secondary", className="me-2"),
        dbc.Button("Sim", id="btn-confirm-approval", color="success")
        ]),
    is_open=False
)

buildup_page = html.Div([
    dbc.Spinner(
        html.Div(id="buildup-content"),
        color="primary",
    ),
    dcc.Store(id="previous-quarter", data=None),
    dcc.Store(id="previous-year", data=None),
    error_modal,
    modal_confirm_approval,
])

# Callback para lidar com a renderizaçao da pagina
@callback(
    Output("buildup-content", "children"),
    Input("url", "pathname"),
    State("store-token", "data"),
    Input("store-language", "data"),
)
def update_buildup_content(pathname, user_data, language):

    global _
    _ = setup_translations(language)

    if pathname in ["/buildup", "/approval"]:
        return get_layout(pathname, user_data)
    return no_update

# Callback to update the buildup simulation tables
for tab_config, buildup in product(tab_configs(), BUILD_UPS_CODES):
    @callback(
        Output(f'table-buildup-simulation-{tab_config["id"]}-{buildup}', 'data'),
        Output(f'currency-rate-{tab_config["id"]}-{buildup}', 'children'),
        [
            Input("input-quarter", "value"),
            Input("input-year", "value"),
            Input("table-buildup-factors", "data"),
            Input(f'table-buildup-simulation-{tab_config["id"]}-{buildup}', 'data'),
            Input(f'input-currency-{tab_config["id"]}-{buildup}', 'value'),
            Input(f'input-dealer-code-{tab_config["id"]}-{buildup}', 'value'),
            Input(f'input-icms-st-{tab_config["id"]}-{buildup}', 'value'),
            Input(f'input-mva-price-{tab_config["id"]}-{buildup}', 'value'),
            Input(f'input-price-zrsd026-{tab_config["id"]}-{buildup}', 'value'),
            Input(f'input-ipi-{tab_config["id"]}-{buildup}', 'value'),
            Input(f'input-ipi-material-cost-{tab_config["id"]}-{buildup}', 'value'),
            Input(f'input-icms-material-cost-{tab_config["id"]}-{buildup}', 'value'),
            Input(f'input-product-price-pis-cofins-{tab_config["id"]}-{buildup}', 'value'),
        ],
    )
    def handle_change_buildup(
        input_value_quarter,
        input_value_year,
        table_build_up_factors,
        table_build_up_simulation_data,
        input_value_currency,
        input_value_dealer_code,
        input_value_icms_st,
        input_value_mva_price,
        input_value_price_zrsd026,
        input_value_ipi,
        input_value_ipi_material_cost,
        input_value_icms_material_cost,
        input_value_product_price_pis_cofins,
        buildup_code=buildup,
        tab_name=tab_config["id"],
    ):

        month = get_month_from_quarter(input_value_quarter)
        currency_rate = get_tax_rates(
            table_fx,
            currency_selected=input_value_currency,
            month=month,
            year=input_value_year
        ) if tab_name == "base_price" else 1

        if df_buildup is None:
            print("DataFrame principal não está carregado")
            return []

        if buildup_code is None:
            print("buildup_code é None, retornando lista vazia")
            return []

        # Todos os inputs de simulação
        input_price_zrsd026 = float(input_value_price_zrsd026 or 0)
        input_price_zrsd026_with_fx = input_price_zrsd026 * currency_rate
        input_product_price_pis_cofins = float(input_value_product_price_pis_cofins or 0)
        input_dealer_code_percentage = float(input_value_dealer_code or 0) / 100
        input_icms_st_percentage = float(input_value_icms_st or 0) / 100
        input_mva_price_percentage = float(input_value_mva_price or 0) / 100
        input_ipi_percentage = float(input_value_ipi or 0) / 100
        input_ipi_material_cost_percentage = float(input_value_ipi_material_cost or 0) / 100
        input_icms_material_cost_percentage = float(input_value_icms_material_cost or 0) / 100

        # Todos os inputs de fatores usando a nova função
        input_icms_avg_percentage = get_buildup_value('icms_avg', df_buildup, buildup_code)
        input_pis_exceto_dso_percentage = get_buildup_value('pis', df_buildup, buildup_code)
        input_cofins_exceto_dso_percentage = get_buildup_value('cofins', df_buildup, buildup_code)
        input_warranty_parts_percentage = get_buildup_value('warranty_parts', df_buildup, buildup_code)
        input_warranty_cars_percentage = get_buildup_value('warranty_cars', df_buildup, buildup_code)
        input_bonus_percentage = get_buildup_value('bonus', df_buildup, buildup_code)
        input_regional_marketing_percentage = get_buildup_value('regional_marketing', df_buildup, buildup_code)
        input_floor_plan_percentage = get_buildup_value('floor_plan', df_buildup, buildup_code)
        input_part_return_autogiro_anom_percentage = get_buildup_value('part_return', df_buildup, buildup_code)
        input_other_expenses_percentage = get_buildup_value('other_expenses', df_buildup, buildup_code)
        input_freight_in_percentage = get_buildup_value('freight_in', df_buildup, buildup_code)
        input_freight_out_percentage = get_buildup_value('freight_out', df_buildup, buildup_code)
        input_warranty_1_parts_percentage = get_buildup_value('warranty_1_parts', df_buildup, buildup_code)
        input_warranty_2_cars_percentage = get_buildup_value('warranty_2_cars', df_buildup, buildup_code)
        input_product_service_warranty_percentage = get_buildup_value('product_service_warranty', df_buildup, buildup_code)
        input_cost_adjustment_percentage = get_buildup_value('cost_adjustment', df_buildup, buildup_code)
        input_other_costs_percentage = get_buildup_value('other_costs', df_buildup, buildup_code)
        input_structural_expenses_percentage = get_buildup_value('structural_expenses', df_buildup, buildup_code)
        input_other_percentage = get_buildup_value('other', df_buildup, buildup_code)

        # Cálculos iniciais
        price_ipi = input_price_zrsd026_with_fx * (1 + input_ipi_percentage)
        public_price = input_price_zrsd026_with_fx / (1 - input_dealer_code_percentage)
        icms_st_gm_manufacturer = input_price_zrsd026_with_fx * input_icms_st_percentage
        mva_price = price_ipi * (1 + input_mva_price_percentage)
        icms_st = mva_price * input_icms_st_percentage
        icms_st_charge_dealer = icms_st - icms_st_gm_manufacturer
        total_ticket_manufacturer = price_ipi + icms_st_charge_dealer
        dealer_code = public_price - total_ticket_manufacturer
        ipi = input_price_zrsd026_with_fx * input_ipi_percentage

        # Cálculo dos componentes do Net Sales
        icms_avg = input_price_zrsd026_with_fx * input_icms_avg_percentage
        pis_exceto_dso = input_price_zrsd026_with_fx * input_pis_exceto_dso_percentage
        cofins_exceto_dso = input_price_zrsd026_with_fx * input_cofins_exceto_dso_percentage
        warranty_parts = input_price_zrsd026_with_fx * input_warranty_parts_percentage
        warranty_cars = input_price_zrsd026_with_fx * input_warranty_cars_percentage
        bonus = input_price_zrsd026_with_fx * input_bonus_percentage
        regional_marketing = input_price_zrsd026_with_fx * input_regional_marketing_percentage
        floor_plan = input_price_zrsd026_with_fx * input_floor_plan_percentage
        part_return_autogiro_anom = input_price_zrsd026_with_fx * input_part_return_autogiro_anom_percentage
        other_expenses = input_price_zrsd026_with_fx * input_other_expenses_percentage

        # Cálculo do Net Sales Factor e Net Sales
        net_sales = input_price_zrsd026_with_fx + icms_avg + pis_exceto_dso + cofins_exceto_dso + warranty_parts + warranty_cars + bonus + regional_marketing + floor_plan + part_return_autogiro_anom + other_expenses

        # % GS
        percentage_of_gs = net_sales / input_price_zrsd026_with_fx

        # Cálculo do Material Cost
        product_price_w_pis_cofins = input_product_price_pis_cofins * currency_rate
        pis = product_price_w_pis_cofins * input_pis_exceto_dso_percentage
        cofins = product_price_w_pis_cofins * input_cofins_exceto_dso_percentage
        base_price_net_cost = product_price_w_pis_cofins - pis - cofins
        price_without_ipi = base_price_net_cost / (1 - input_icms_material_cost_percentage)
        material_cost_ipi = price_without_ipi * input_ipi_material_cost_percentage
        # material_cost = price_without_ipi + material_cost_ipi

        material_cost = base_price_net_cost + material_cost_ipi
        material_cost_avg_mt_cost = -material_cost  # Negativo pois é um custo

        # Cálculo dos custos
        freight_in = input_price_zrsd026_with_fx * input_freight_in_percentage
        freight_out = input_price_zrsd026_with_fx * input_freight_out_percentage
        warranty_1_parts = input_price_zrsd026_with_fx * input_warranty_1_parts_percentage
        warranty_2_cars = input_price_zrsd026_with_fx * input_warranty_2_cars_percentage
        product_service_warranty = input_price_zrsd026_with_fx * input_product_service_warranty_percentage
        cost_adjustment = input_price_zrsd026_with_fx * input_cost_adjustment_percentage
        other_costs = input_price_zrsd026_with_fx * input_other_costs_percentage

        # Total de custos e fator de custos
        costs_factor = (
            input_freight_in_percentage + input_freight_out_percentage + 
            input_warranty_1_parts_percentage + input_warranty_2_cars_percentage + 
            input_product_service_warranty_percentage + input_cost_adjustment_percentage + 
            input_other_costs_percentage
        )

        # total_costs = material_cost_avg_mt_cost + (input_price_zrsd026_with_fx * costs_factor)
        total_costs = material_cost_avg_mt_cost + freight_in + freight_out + warranty_1_parts + warranty_2_cars + product_service_warranty + cost_adjustment + other_costs

        # Cálculo da margem de contribuição e despesas
        contribution_margin = net_sales + total_costs
        percentage_of_ns = contribution_margin / net_sales if net_sales != 0 else 0

        structural_expenses = input_price_zrsd026_with_fx * input_structural_expenses_percentage
        other = input_price_zrsd026_with_fx * input_other_percentage
        total_expenses = structural_expenses + other

        # Cálculo do EBIT
        ebit = contribution_margin - total_expenses
        percentage_of_ns_ebit = ebit / net_sales if net_sales != 0 else 0

        # Funcao para atualizar a tabela de simulacao
        simulation_data = [
            {
                "field": "Public Price",
                "value": round(public_price, 2)
            },
            {
                "field": "Dealer Code",
                "value": round(dealer_code, 2)
            },
            {
                "field": "Total Ticket Manufacturer",
                "value": round(total_ticket_manufacturer, 2)
            },
            {
                "field": "ICMS ST",
                "value": round(icms_st, 2)
            },
            {
                "field": "ICMS (GM+Manufacturer)",
                "value": round(icms_st_gm_manufacturer, 2)
            },
            {
                "field": "ICMS ST (Charge Dealer)",
                "value": round(icms_st_charge_dealer, 2)
            },
            {
                "field": "MVA + Price",
                "value": round(mva_price, 2)
            },
            {
                "field": "Price + IPI",
                "value": round(price_ipi, 2)
            },
            {
                "field": "IPI",
                "value": round(ipi, 2)
            },
            {
                "field": "Price (ZRSD026)",
                "value": round(input_price_zrsd026_with_fx, 2)
            },
            {
                "field": "ICMS",
                "value": round(icms_avg, 2)
            },
            {
                "field": "PIS (AVG)",
                "value": round(pis_exceto_dso, 2)
            },
            {
                "field": "Cofins (AVG)",
                "value": round(cofins_exceto_dso, 2)
            },
            {
                "field": "Warranty (Parts)",
                "value": round(warranty_parts, 2)
            },
            {
                "field": "Warranty (Cars)",
                "value": round(warranty_cars, 2)
            },
            {
                "field": "Bonus",
                "value": round(bonus, 2)
            },
            {
                "field": "Regional Marketing",
                "value": round(regional_marketing, 2)
            },
            {
                "field": "Floor Plan",
                "value": round(floor_plan, 2)
            },
            {
                "field": "Part Return/Autogiro/Anom",
                "value": round(part_return_autogiro_anom, 2)
            },
            {
                "field": "Other Expenses",
                "value": round(other_expenses, 2)
            },
            {
                "field": "Net Sales",
                "value": round(net_sales, 2)
            },
            {
                "field": "% of GS",
                "value": round(percentage_of_gs, 2)
            },
            {
                "field": "Material Cost/ Avg Mt Cost",
                "value": round(material_cost_avg_mt_cost, 2)
            },
            {
                "field": "Freight In",
                "value": round(freight_in, 2)
            },
            {
                "field": "Freight Out",
                "value": round(freight_out, 2)
            },
            {
                "field": "Warranty 1 (Parts)",
                "value": round(warranty_1_parts, 2)
            },
            {
                "field": "Warranty 2 (Cars)",
                "value": round(warranty_2_cars, 2)
            },
            {
                "field": "Product Service Warranty",
                "value": round(product_service_warranty, 2)
            },
            {
                "field": "Package",
                "value": round(0, 2)  # Placeholder for actual value
            },
            {
                "field": "Cost Adjustment",
                "value": round(cost_adjustment, 2)
            },
            {
                "field": "Other Costs",
                "value": round(other_costs, 2)
            },
            {
                "field": "Total Costs",
                "value": round(total_costs, 2)
            },
            {
                "field": "Contribution Margin",
                "value": round(contribution_margin, 2)
            },
            {
                "field": "% of NS",
                "value": round(percentage_of_ns, 2)
            },
            {
                "field": "Structural Expenses",
                "value": round(structural_expenses, 2)
            },
            {
                "field": "Other",
                "value": round(other, 2)
            },
            {
                "field": "Total Expenses",
                "value": round(total_expenses, 2)
            },
            {
                "field": "EBIT",
                "value": round(ebit, 2)
            },
            {
                "field": "% of NS EBIT",
                "value": round(percentage_of_ns_ebit, 2)
            }
        ]

        return simulation_data, round(currency_rate, 2)

# Callback para filtrar a tabela de fatores de acordo com o quarter e year selecionados
@callback(
    Output("table-buildup-factors", "rowData"),
    Input("input-quarter", "value"),
    Input("input-year", "value"),
    Input("table-buildup-factors", "rowData"),
)
def filter_factors_table(quarter, year, table_data):
    if not quarter or not year:
        return table_data

    df = pl.DataFrame(table_data)

    # Converter quarter e year para string para garantir comparação correta
    quarter = str(quarter)
    year = str(year)

    filtered_df = df.filter(
        (pl.col("quarter").cast(pl.Utf8).eq(quarter)) & 
        (pl.col("formatted_year").cast(pl.Utf8).eq(year))
    )

    return handle_buildup_data(filtered_df)

# Callback para validar combinações de quarter/year e mostrar mensagem de erro
@callback(
    [
        Output("error-modal", "is_open"),
        Output("error-modal-body", "children"),
        Output("input-quarter", "value"),
        Output("input-year", "value"),
        Output("previous-quarter", "data"),
        Output("previous-year", "data"),
    ],
    [
        Input("input-quarter", "value"),
        Input("input-year", "value"),
        Input("close-error-modal", "n_clicks"),
        State("previous-quarter", "data"),
        State("previous-year", "data"),
    ],
    prevent_initial_call=True
)
def validate_quarter_year(quarter, year, close_clicks, prev_quarter, prev_year):
    trigger = callback_context.triggered[0]
    
    # Se o botão de fechar foi clicado, fecha o modal
    if trigger["prop_id"] == "close-error-modal.n_clicks":
        return False, "", no_update, no_update, no_update, no_update
    
    if not quarter or not year:
        return False, "", quarter, year, quarter, year
        
    df = pl.DataFrame(df_buildup)
    
    # Converter quarter e year para string para garantir comparação correta
    quarter_str = str(quarter)
    year_str = str(year)
    
    # Verifica se a combinação existe na base de dados
    filtered_df = df.filter(
        (pl.col("quarter").cast(pl.Utf8).eq(quarter_str)) & 
        (pl.col("formatted_year").cast(pl.Utf8).eq(year_str))
    )
    
    if filtered_df.height == 0:
        error_msg = f"A combinação do trimestre {quarter} com o ano {year} não existe na base de dados."
        # Retorna aos valores anteriores válidos
        return True, error_msg, prev_quarter or quarter, prev_year or year, prev_quarter or quarter, prev_year or year
    
    # Atualiza os valores anteriores válidos
    return False, "", quarter, year, quarter, year

# Callback para atualizar a tabela e habilitar botão de aprovação
@callback(
    Output('button-approval-buildup', 'disabled'),        # Habilita/desabilita o botão
    Output('table-buildup-factors', 'rowData', allow_duplicate=True),           # Atualiza os dados da tabela
    Input('table-buildup-factors', 'cellValueChanged'),
    Input("input-quarter", "value"),
    Input("input-year", "value"),
    Input('table-buildup-factors', 'rowData'),
    prevent_initial_call=True,
)
def update_cell_value(cellValueChanged, quarter, year, table_data):
    if cellValueChanged:
        # Atualiza a coluna 'manual' para todas as linhas onde houve alteração

        updated_row_data = modify_column_if_other_column_changed(
            cellValueChanged,
            table_data,
            column_to_change="manual",
            value_to_input="1"
        )

        return False, updated_row_data 
    return True, no_update

# Callback para abrir o modal de confirmação de aprovação
@callback(
    Output("modal-confirm-approval-buildup", "is_open"),
    Input("button-approval-buildup", "n_clicks"),
    prevent_initial_call=True,
)
def open_confirm_approval_modal(n_clicks):
    if n_clicks:
        return True
    return False

# Callback para processar a confirmação de aprovação
@callback(
    Output("modal-confirm-approval-buildup", "is_open", allow_duplicate=True),
    Output("toast-approval-buildup", "is_open", allow_duplicate=True),
    Input("btn-confirm-approval","n_clicks"),
    Input("btn-cancel-approval","n_clicks"),
    State("table-buildup-factors", "rowData"),
    State("store-token", "data"),
    prevent_initial_call=True,
)
def handle_send_approval(confirm_clicks, cancel_clicks, table_data, user_data):
    triggered_id = ctx.triggered_id
    
    if triggered_id == "btn-cancel-approval" and cancel_clicks:
        return False, False

    if triggered_id == "btn-confirm-approval" and confirm_clicks:
            
        df = pl.DataFrame(table_data)

        new_table = merge_with_original_data(reverse_raw_dataframe(df))
        new_table = new_table.select([col for col in new_table.columns if col != "manual"])

        # Garantir que year seja string antes de adicionar à tabela
        new_table = new_table.with_columns([
            pl.col("year").cast(pl.Utf8),
            pl.col("quarter").cast(pl.Utf8)
        ])

        variables_to_send = {
            'user_token': user_data["access_token"],
            'table_data': new_table.to_pandas().to_dict('records'),
        }

        send_to_approval(notebook_name="buildup", data_variables=variables_to_send)

        return False, True
    return False, False

# Callback para aprovação/rejeição
@callback(
    Output("toast-approval-reject-buildup", "is_open"),
    Output("toast-approval-reject-buildup", "header"),
    Output("toast-approval-reject-buildup", "children"),
    Input("button-approval-accept-buildup", "n_clicks"),
    Input("button-approval-reject-buildup", "n_clicks"),
    State("table-buildup-factors", "rowData"),
    State("store-token", "data"),
    prevent_initial_call=True
)
def handle_approval(accept_clicks, reject_clicks, table_data, user_data):
    if not ctx.triggered_id:
        return no_update

    button_id = ctx.triggered_id
    status = "1" if "accept" in button_id else "2"
    status_text = "aprovado" if status == "1" else "recusado"

    if not table_data:
        return html.P("Erro: Não há dados para aprovar/recusar",className="message-danger")

    try:
        uuid_alteracoes = table_data[0]["uuid_alteracoes"]

        variables_to_send = {
            "uuid_alteracoes": uuid_alteracoes,
            "status": status,
            "user_token": user_data["access_token"],
            "target_table": "buildup",
        }

        update_approval_status(variables_to_send)

        return True, f"{status_text}", f"Status alterado para {status_text}"

    except Exception as e:
        print(f"Erro ao processar aprovação: {str(e)}")
        return True, "Erro", f"Erro ao processar aprovação: {str(e)}"
