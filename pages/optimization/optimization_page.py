import dash
import dash_ag_grid as dag
import dash_bootstrap_components as dbc
import polars as pl
import pandas as pd
import time
import base64
import io
from dash import html, dcc, Input, Output, State, callback, no_update, callback_context, ctx
from components.Card import Card
from components.Helper_button_with_modal import create_help_button_with_modal
from components.Toast import Toast
from components.Modal import create_modal
from components.Upload_file import create_upload_file
from pages.approvals.approval_utils import container_approval_reject_buttons
from api.api_get_optimization import get_optimization
from api.update_optimization import update_optimization
from api.get_requests_for_approval import get_requests_for_approval
from api.send_to_approval import send_to_approval
from api.update_approval_status import update_approval_status
from utils.calculation_division import calculation_division
from utils.sum_df_col import sum_df_col
from utils.user_has_permission_to_edit import user_has_permission_to_edit
from utils.handle_nothing_to_approve import handle_nothing_to_approve
from static_data.helper_text import helper_text
from styles import MAIN_TITLE_STYLE, CONTAINER_BUTTONS_STYLE, CONTAINER_HELPER_BUTTON_STYLE
from translations import _, setup_translations

def create_columns(pathname, user_data):
    return [
        {"headerName": _("Peça"), "field": "peca", "width": 80, "pinned": "left"},
        {"headerName": _("Descrição"), "field": "descricao", "width": 250, "pinned": "left"},
        {"headerName": _("Status"), "field": "status", "width": 180, "pinned": "left"},
        {"headerName": _("Catlote"), "field": "catlote", "width": 180, "pinned": "left"},
        {"headerName": _("CPC 1 3 6"), "field": "cpc1_3_6", "width": 220, "pinned": "left"},
        {"headerName": _("Marca"), "field": "var_marca", "width": 80, "pinned": "left"},
        {"headerName": _("Preço Tabela"), "children": [
            {"headerName": _("Mercado"), "field": "preco_concorrente_distribuidor", "width": 120, "type": "numericColumn"},
            {"headerName": _("Baseline"), "field": "preco_sap_atual", "width": 120, "type": "numericColumn"},
            {"headerName": _("Estimado"), "field": "preco_sap_novo", "width": 120, "type": "numericColumn", "editable": user_has_permission_to_edit(pathname, user_data)},
            {"headerName": _("Delta %"), "field": "dp_final", "width": 60, "type": "numericColumn"},
        ]},
        {"headerName": _("Volume"), "children": [
            {"headerName": _("Baseline"), "field": "qtd_volume", "width": 120, "hide": True},
            {"headerName": _("Estimado"), "field": "vol_novo2_final", "width": 120, "hide": True},
            {"headerName": _("Delta %"), "field": "delta_volume_final", "width": 60, "type": "numericColumn"},
        ]},
        {"headerName": _("Fat Bruto"), "children": [
            {"headerName": _("Baseline"), "field": "preco_venda_baseline", "width": 120, "hide": True},
            {"headerName": _("Estimado"), "field": "gross_final", "width": 120, "hide": True},
            {"headerName": _("Delta %"), "field": "delta_gross_final", "width": 60, "type": "numericColumn"},
        ]},
        {"headerName": _("Fat Liq"), "children": [
            {"headerName": _("Baseline"), "field": "preco_net_baseline", "width": 120, "hide": True},
            {"headerName": _("Estimado"), "field": "net_final", "width": 120, "hide": True},
            {"headerName": _("Delta %"), "field": "delta_net_final", "width": 60, "type": "numericColumn"},
        ]},
        {"headerName": _("Margem ABS"), "children": [
            {"headerName": _("Baseline"), "field": "margem_contribuicao_baseline", "width": 120, "hide": True},
            {"headerName": _("Estimado"), "field": "mc_final", "width": 120, "hide": True},
            {"headerName": _("Delta %"), "field": "delta_mc_final", "width": 60, "type": "numericColumn"},
        ]},
    ]

def columns_approval():
    return [
        {"headerName": _("Peça"), "field": "peca"},
        {"headerName": _("Descrição"), "field": "descricao"},
        {"headerName": _("Status"), "field": "status"},
        {"headerName": _("CPC 1 3 6"), "field": "cpc1_3_6"},
        {"headerName": _("Marca"), "field": "var_marca"},
        {"headerName": _("Preço Tabela"), "children": [
            {"headerName": _("Mercado"), "field": "preco_concorrente_distribuidor"},
            {"headerName": _("Baseline"), "field": "preco_sap_atual"},
            {"headerName": _("Estimado"), "field": "preco_sap_novo", "editable": False, "valueFormatter": "value ? `R$ ${value.toFixed(2)}` : ''"},
            {"headerName": _("Delta %"), "field": "dp_final", "type": "numericColumn"},
        ]},
        {"headerName": _("Volume"), "children": [
            {"headerName": _("Baseline"), "field": "qtd_volume", "hide": True},
            {"headerName": _("Estimado"), "field": "vol_novo2_final", "hide": True},
            {"headerName": _("Delta %"), "field": "delta_volume_final", "type": "numericColumn"},
        ]},
        {"headerName": _("Fat Bruto"), "children": [
            {"headerName": _("Baseline"), "field": "preco_venda_baseline", "hide": True},
            {"headerName": _("Estimado"), "field": "gross_final", "hide": True},
            {"headerName": _("Delta %"), "field": "delta_gross_final", "type": "numericColumn"},
        ]},
        {"headerName": _("Fat Liq"), "children": [
            {"headerName": _("Baseline"), "field": "preco_net_baseline", "hide": True},
            {"headerName": _("Estimado"), "field": "net_final", "hide": True},
            {"headerName": _("Delta %"), "field": "delta_net_final", "type": "numericColumn"},
        ]},
        {"headerName": _("Margem ABS"), "children": [
            {"headerName": _("Baseline"), "field": "margem_contribuicao_baseline", "hide": True},
            {"headerName": _("Estimado"), "field": "mc_final", "hide": True},
            {"headerName": _("Delta %"), "field": "delta_mc_final", "type": "numericColumn"},
        ]},
        {"headerName": _("Status"), "field": "status"}, # temporário para testes
        {"headerName": _("UUID Alteração"), "field": "uuid_alteracoes"}, # temporário para testes
    ]

original_footer = html.Div([
    dbc.Button(
        "Cancelar", 
        id="btn-cancel-import",
        color="secondary",
        className="me-2"
    ),
    dbc.Button(
        "Importar", 
        id="btn-confirm-import",
        color="success",
        disabled=True,
    )
], className="w-100 d-flex justify-content-center")

original_body = html.Div([
    html.P("Selecione o arquivo Excel para importar:"),
    html.Div(
        id="upload-container",
        children=create_upload_file(id="upload-excel-optimization")
    ),
    html.Div(id="validation-message", className="validation-message", style={"display": "none"}),
    dcc.Store(id="excel-data-store", storage_type="memory")
])

def button_download_excel():
    return html.Div([
            dbc.Button(
                _("Baixar"),
                id="btn-download-excel-optimization",
                color="success",
                n_clicks=0
            ),
            dbc.Tooltip(
                _("Baixar arquivo em Excel"),
                target="btn-download-excel-optimization",
                placement="top",
            ),
            dcc.Download(id="download-excel-optimization"),
    ])

def calculate_totals(df):
    try:
        # Cálculo do preço médio
        price_as_is = calculation_division(df=df, column1="preco_venda_baseline", column2="qtd_volume")
        price_to_be = calculation_division(df=df, column1="gross_final", column2="vol_novo2_final")

        # Cálculo do volume total
        volume_as_is = sum_df_col(df=df, column="qtd_volume")
        volume_to_be = sum_df_col(df=df, column="vol_novo2_final")

        # Cálculo do faturamento bruto total
        gross_as_is = sum_df_col(df=df, column="preco_venda_baseline")
        gross_to_be = sum_df_col(df=df, column="gross_final")

        # Cálculo da margem total
        margin_as_is = sum_df_col(df=df, column="margem_contribuicao_baseline")
        margin_to_be = sum_df_col(df=df, column="mc_final")

        return {
            'price': (price_as_is, price_to_be),
            'volume': (volume_as_is, volume_to_be),
            'gross': (gross_as_is, gross_to_be),
            'margin': (margin_as_is, margin_to_be)
        }
    except Exception as e:
        print(f"Erro no cálculo dos totalizadores: {e}")
        return None

def create_cards(df, _):
    """
    Cria cards com os totais calculados.

    Args:
        df (polars.DataFrame): DataFrame contendo os dados para calcular os totais.
        _ (gettext.GNUTranslations): Objeto de tradução para o idioma atual.

    Returns:
        dash.html.Div: Componente Dash contendo os cards com os totais calculados.
    """
    if isinstance(df, list):
        df = pl.DataFrame(df)

    print("df['preco_sap_novo'].sum()", df["preco_sap_novo"].sum())

    totals = calculate_totals(df)
    print("totals", totals)

    if not totals:
        return html.Div("Erro ao calcular totalizadores")

    cards = html.Div([
        dbc.Row([
            dbc.Col(
                Card(
                    title=_("Preço"),
                    value_as_is=totals['price'][0],
                    value_to_be=totals['price'][1],
                    show_decimal=True,
                    icon="💵"
                ),
                width=3,
                className="px-2"
            ),
            dbc.Col(
                Card(
                    title=_("Volume"),
                    value_as_is=totals['volume'][0],
                    value_to_be=totals['volume'][1],
                    show_decimal=False,
                    icon="📦"
                ),
                width=3,
                className="px-2"
            ),
            dbc.Col(
                Card(
                    title=_("Faturamento Bruto"),
                    value_as_is=totals['gross'][0],
                    value_to_be=totals['gross'][1],
                    show_decimal=False,
                    icon="💰"
                ),
                width=3,
                className="px-2"
            ),
            dbc.Col(
                Card(
                    title=_("Margem"),
                    value_as_is=totals['margin'][0],
                    value_to_be=totals['margin'][1],
                    show_decimal=False,
                    icon="📈"
                ),
                width=3,
                className="px-2"
            ),
        ], className="g-0 mb-3"),
    ])

    return cards

def calculate_dependent_fields(df, changed_field):
    """Recalcula campos dependentes quando um valor é alterado"""

    print("calculate_dependent_fields")

    if changed_field == "preco_sap_novo":
        # Recalcula delta de preço
        df = df.with_columns([
            ((pl.col("preco_sap_novo") / pl.col("preco_sap_atual") - 1) * 100).alias("dp_final")
        ])
        
        # Recalcula volume estimado
        df = df.with_columns([
            (pl.col("qtd_volume") * (1 + pl.col("dp_final") / 100)).alias("vol_novo2_final"),
            ((pl.col("vol_novo2_final") / pl.col("qtd_volume") - 1) * 100).alias("delta_volume_final")
        ])
        
        # Recalcula faturamento
        df = df.with_columns([
            (pl.col("preco_sap_novo") * pl.col("vol_novo2_final")).alias("gross_final"),
            ((pl.col("gross_final") / pl.col("preco_venda_baseline") - 1) * 100).alias("delta_gross_final")
        ])

        # Recalcula margens
        df = df.with_columns([
            (pl.col("gross_final") * (pl.col("margem_contribuicao_baseline") / pl.col("preco_venda_baseline"))).alias("mc_final"),
            ((pl.col("mc_final") / pl.col("margem_contribuicao_baseline") - 1) * 100).alias("delta_mc_final")
        ])

    return df

def handle_percentage_fields(df):
    """Ajusta os campos de percentual para exibição correta"""

    return df.with_columns([
        (pl.col("dp_final") * 100).round(1).alias("dp_final"),
        (pl.col("delta_volume_final") * 100).round(1).alias("delta_volume_final"),
        (pl.col("delta_gross_final") * 100).round(1).alias("delta_gross_final"),
        (pl.col("delta_net_final") * 100).round(1).alias("delta_net_final"),
        (pl.col("delta_mc_final") * 100).round(1).alias("delta_mc_final")
    ])

def handle_new_alteration(table_data):
    """Prepara os dados iniciais da tabela"""

    table_data = table_data.with_columns(
        pl.lit(None).alias("new_alteration")
    )
    return handle_percentage_fields(table_data)

helper_button = html.Div(
    create_help_button_with_modal(
        modal_title=helper_text["optimization"]["title"],
        modal_body=helper_text["optimization"]["description"],
    ), style=CONTAINER_HELPER_BUTTON_STYLE,
)

def action_buttons(_, pathname, user_data):
    return html.Div([
        dbc.Button(
            _("Atualizar"),
            id="button-update-optimization",
            color="success",
            disabled=False if user_has_permission_to_edit(pathname, user_data) else True,
            n_clicks=0
        ),
        dbc.Tooltip(
            _("Solicitar atualização dos dados"),
            target="button-update-optimization",
            placement="top",
        ),
        dbc.Button(
            _("Importar"),
            id="button-import-excel-optimization",
            color="success",
            disabled=False if user_has_permission_to_edit(pathname, user_data) else True,
            n_clicks=0
        ),
        dbc.Tooltip(
            _("Importar Excel"),
            target="button-import-excel-optimization",
            placement="top",
        ),
        button_download_excel(),
        dbc.Button(
            _("Aprovar"),
            id="button-approval-optimization",
            color="success",
            disabled=False if user_has_permission_to_edit(pathname, user_data) else True,
            n_clicks=0
        ),
        dbc.Tooltip(
            _("Enviar para aprovação"),
            target="button-approval-optimization",
            placement="top",
        ),
    ], style=CONTAINER_BUTTONS_STYLE)

def recalculate_row(
    df,
    current_data=None,
    peca=None,
    novo_valor=None
):
    """
    Recalcula a linha
    """

    print("recalculate_row")

    if current_data is not None:
        coluna = current_data.get('colId')
        print("coluna", coluna)

        if coluna != 'preco_sap_novo':
            raise dash.exceptions.PreventUpdate

        peca = current_data['data']['peca']
        novo_valor = float(current_data['value'] or 0)

    print("peca", peca)
    print("novo_valor", novo_valor)

    print("df['peca'] == peca", df['peca'] == peca)

    row_idx = df['peca'] == peca
    print("row_idx", row_idx)

    if not row_idx.any():
        raise dash.exceptions.PreventUpdate

    row = df.filter(row_idx)

    print("row", row)

    # Extrai valores com vetorização

    print("Extrai valores com vetorização")

    calcs = {
        'imp_icms': float(row['imp_icms'][0]),
        'desconto': float(row['desconto'][0]),
        'imp': float(row['imp'][0]),
        'preco_sap_atual': float(row['preco_sap_atual'][0] or 1.0),
        'qtd_volume': float(row['qtd_volume'][0]),
        'e': float(row['e'][0]),
        'costs_factor_medio': float(row['costs_factor_medio'][0]),
        'custo_medio_unit': float(row['custo_medio_unit'][0]),
        'preco_venda_baseline': float(row['preco_venda_baseline'][0] or 1.0),
        'preco_net_baseline': float(row['preco_net_baseline'][0] or 1.0),
        'margem_contribuicao_baseline': float(row['margem_contribuicao_baseline'][0] or 1.0)
    }

    print("calcs", calcs)

    # Cálculos vetorizados
    updates = {
        'preco_sap_novo': novo_valor,
        'preco_imp_final': round(novo_valor * calcs['imp_icms'], 2),
        'preco_venda_final': round(novo_valor * calcs['imp_icms'] * (1 - calcs['desconto']), 2)
    }

    updates['preco_net_final'] = round(updates['preco_venda_final'] * calcs['imp'], 2)
    updates['dp_final'] = round((novo_valor / calcs['preco_sap_atual'] - 1) * 100, 1)
    updates['vol_novo_final'] = round(calcs['qtd_volume'] * (1 + updates['dp_final'] / 100) ** calcs['e'], 2)
    updates['vol_novo2_final'] = min(updates['vol_novo_final'], round(calcs['qtd_volume'] * 1.5, 2)) if updates['dp_final'] > 50 else updates['vol_novo_final']

    updates['gross_final'] = round(updates['vol_novo2_final'] * updates['preco_venda_final'], 2)
    updates['net_final'] = round(updates['vol_novo2_final'] * updates['preco_net_final'], 2)
    updates['mc_final'] = round((updates['preco_net_final'] + (updates['preco_venda_final'] * calcs['costs_factor_medio'] - calcs['custo_medio_unit'])) * updates['vol_novo2_final'], 2)

    updates['delta_volume_final'] = round((updates['vol_novo2_final'] / calcs['qtd_volume'] - 1) * 100, 1)
    updates['delta_gross_final'] = round((updates['gross_final'] / calcs['preco_venda_baseline'] - 1) * 100, 1)
    updates['delta_net_final'] = round((updates['net_final'] / calcs['preco_net_baseline'] - 1) * 100, 1)
    updates['delta_mc_final'] = round((updates['mc_final'] / calcs['margem_contribuicao_baseline'] - 1) * 100, 1)
    updates['status'] = 'manual'
    updates['new_alteration'] = 'sim'

    print("updates", updates)
    print("updates['dp_final']", updates['dp_final'])

    for col, value in updates.items():
        df = df.with_columns(
            pl.when(row_idx)
            .then(pl.lit(value))
            .otherwise(pl.col(col))
            .alias(col)
        )

    return df.to_dicts()

def get_layout(pathname, user_data):
    """Gera o layout da página de otimização de preços"""

    cpc = user_data.get('cpc1_3_6_list')
    table_data = get_requests_for_approval(table="optimization") if pathname == "/approval" else get_optimization(cpc)
    table_data = table_data if pathname == "/approval" else handle_new_alteration(table_data)

    if table_data is None:
        return handle_nothing_to_approve()

    header = None
    if pathname != "/approval":
        header = html.Div([
            html.H1(_("Otimização de Preços"), style=MAIN_TITLE_STYLE),
            helper_button
        ], className="container-title")

    toast_approve = Toast(
        id="toast-approval-optimization",
        header=_("Aprovação"),
        toast_message=_("Enviado para aprovação"),
    )

    toast_reject = Toast(id="toast-approval-reject-optimization")

    buttons = (
        container_approval_reject_buttons(table="optimization")
        if pathname == "/approval"
        else action_buttons(_, pathname, user_data)
    )

    cards = html.Div(
        id="optimization-cards",
        children=create_cards(table_data, _),
        className="configs-space-cards"
    )

    table_container = html.Div([
        html.P(
            _("Volume dos últimos 12 meses com preços e custos vigentes"),
            className="description-message"
        ),
        dag.AgGrid(
            id='optimization-table',
            rowData=table_data.to_dict("records") if pathname == "/approval" else table_data.to_dicts(),
            columnDefs=columns_approval() if pathname == "/approval" else create_columns(pathname, user_data),
            defaultColDef={
                "sortable": True,
                "filter": 'agTextColumnFilter',
                "filterParams": {
                    "buttons": ["apply", "reset"],
                    "closeOnApply": True,
                },
                "resizable": True,
                "minWidth": 120,
            },
            dashGridOptions={
                "pagination": True,
                "paginationPageSize": 20,
                "enableRangeSelection": True,
                "enableFilter": True,
                "domLayout": 'autoHeight',
                "stopEditingWhenCellsLoseFocus": True,
                "enterMovesDown": False,
                "enterMovesDownAfterEdit": False,
            },
            className="ag-theme-alpine",
            style={
                "height": "calc(100vh - 200px)",
                "width": "100%",
            }
        )
    ], className="table-container")

    page_content = html.Div(
        [cards, table_container],
        className="page-content"
    )

    return html.Div([
        header,
        toast_approve,
        toast_reject,
        buttons,
        page_content
    ])


modal_import_excel = create_modal(
    modal_id="modal-import-excel",
    modal_title="Importar Excel",
    modal_body_id="modal-import-excel-body",
    modal_body=original_body,
    modal_footer_id="modal-import-excel-footer",
    modal_footer=html.Div([
        dbc.Button(
            "Cancelar", 
            id="btn-cancel-import",
            color="secondary",
            className="me-2"
        ),
        dbc.Button(
            "Importar", 
            id="btn-confirm-import",
            color="success",
            disabled=True,
        )
    ], className="w-100 d-flex justify-content-center"),
    is_open=False,
)

modal_update_optimization = create_modal(
    modal_id="modal-update-optimization",
    modal_title="Atualização de Dados",
    modal_body_id="modal-update-optimization-body",
    modal_body=html.P("Atualizando dados..."),
    is_open=False
)

# Modal de confirmação para atualização de dados
modal_confirm_update = create_modal(
    modal_id="modal-confirm-update",
    modal_title="Confirmar Atualização",
    modal_body=html.Div([
        html.P("Tem certeza que deseja solicitar a atualização dos dados?"),
        html.P("Esta operação pode levar várias horas para ser concluída, mas você pode continuar usando o sistema normalmente.")
    ]),
    modal_footer=html.Div([
        dbc.Button("Não", id="btn-cancel-update", color="secondary", className="me-2"),
        dbc.Button("Sim", id="btn-confirm-update", color="success")
    ]),
    is_open=False
)

modal_confirm_approval = create_modal(
    modal_id="modal-confirm-approval",
    modal_title="Solicitar Aprovação",
    modal_body=html.P("Tem certeza que deseja enviar para aprovação?"),
    modal_footer=html.Div([
        dbc.Button("Não", id="btn-cancel-approval", color="secondary", className="me-2"),
        dbc.Button("Sim", id="btn-confirm-approval", color="success")
    ]),
    is_open=False
)

optimization_page = html.Div([
    dbc.Spinner(
        html.Div(id="optimization-content", className="optimization-content"),
        color="primary",
    ),
    modal_update_optimization,
    modal_import_excel,
    modal_confirm_approval,
    modal_confirm_update,
])

# Callback para atualizar o layout inicial com os dados da tabela
@callback(
    Output("optimization-content", "children"),
    Input("url", "pathname"),
    State("store-token", "data"),
    Input("store-language", "data"),
)
def update_optimization_content(pathname, user_data, language):

    global _
    _ = setup_translations(language)

    if pathname in ["/optimization", "/approval"]:
        return get_layout(pathname, user_data)
    return no_update

# Callback unificado para atualizar dados e cards
@callback(
    Output('optimization-table', 'rowData', allow_duplicate=True),
    Output('optimization-cards', 'children'),
    Input("url", "pathname"),
    State('optimization-table', 'rowData'),
    Input('optimization-table', 'virtualRowData'),
    Input('optimization-table', 'filterModel'),
    Input('optimization-table', 'cellValueChanged'),
    prevent_initial_call=True
)
def update_table_and_cards(pathname, row_data, virtual_data, filter_model, current_data):
    """Atualiza tabela e cards quando houver alterações ou filtros"""

    print("---update_table_and_cards---")

    # print("pathname", pathname)
    # print("row_data", row_data)
    print("virtual_data", virtual_data is not None)
    print("filter_model", filter_model)
    print("current_data", current_data)

    teste_df = pl.DataFrame(row_data)
    # print("colunas", teste_df.columns)
    print("qtd_volume", teste_df['qtd_volume'].sum())
    print("vol_novo", teste_df['vol_novo'].sum())
    print("vol_novo2", teste_df['vol_novo2'].sum())
    
    print("gross", teste_df['gross'].sum())
    print("gross_cap", teste_df['gross_cap'].sum())
    print("gross_mc", teste_df['gross_mc'].sum())
    print("gross_cap_mc", teste_df['gross_cap_mc'].sum())
    print("gross_final", teste_df['gross_final'].sum())

    print("preco_sap_atual", teste_df['preco_sap_atual'].sum())
    print("preco_sap_atual_baseline", teste_df['preco_sap_atual_baseline'].sum())
    print("preco_sap_novo", teste_df['preco_sap_novo'].sum())
    print("preco_sap_novo_fat", teste_df['preco_sap_novo_fat'].sum())

    if not virtual_data:
        return no_update, None

    ctx = callback_context

    print("---ctx---")
    print(ctx)

    if not ctx.triggered:
        raise dash.exceptions.PreventUpdate

    trigger_id = ctx.triggered[0]['prop_id']

    print("---trigger_id---")
    print(trigger_id)
    print('cellValueChanged' in trigger_id)

    # Se for alteração de célula
    if 'cellValueChanged' in trigger_id and row_data:
        try:
            if isinstance(current_data, list):
                if not current_data:
                    raise dash.exceptions.PreventUpdate
                current_data = current_data[0]

            df = pl.DataFrame(row_data)
            print("df", df)

            updated_data = recalculate_row(
                current_data=current_data,
                df=df
            )

            print("updated_data[0]", updated_data[0])

            updated_cards = no_update if pathname == "/approval" else create_cards(updated_data, _)

            return updated_data, updated_cards

        except Exception as e:
            print(f"Erro ao processar alteração de célula: {str(e)}")
            raise dash.exceptions.PreventUpdate

    # Se for filtro ou atualização virtual
    else:

        print("---else---")

        try:
            filtered_df = pl.DataFrame(virtual_data)
            cards = create_cards(filtered_df, _)
            return no_update, no_update if pathname == "/approval" else cards
        except Exception as e:
            print(f"Erro ao atualizar cards: {e}")
            return no_update, html.Div("Erro ao atualizar totalizadores")

    raise dash.exceptions.PreventUpdate

# Callback para abrir o modal de confirmação de atualização
@callback(
    Output("modal-confirm-update", "is_open"),
    Input("button-update-optimization", "n_clicks"),
    prevent_initial_call=True,
)
def open_confirm_update_modal(n_clicks):
    if n_clicks:
        return True
    return False

# Callback para processar a confirmação de atualização
@callback(
    Output("modal-confirm-update", "is_open", allow_duplicate=True),
    Output("toast-approval-optimization", "is_open", allow_duplicate=True),
    Output("toast-approval-optimization", "header", allow_duplicate=True),
    Output("toast-approval-optimization", "children", allow_duplicate=True),
    Input("btn-confirm-update", "n_clicks"),
    Input("btn-cancel-update", "n_clicks"),
    prevent_initial_call=True
)
def update_optimization_table(confirm_clicks, cancel_clicks):
    triggered_id = ctx.triggered_id

    if triggered_id == "btn-cancel-update":
        return False, False, "", ""

    if triggered_id == "btn-confirm-update" and confirm_clicks:
        try:
            update_optimization()
            return False, True, "Sucesso", "Solicitação enviada com sucesso!"
        except Exception as e:
            return False, True, "Erro", f"Erro ao enviar solicitação: {str(e)}"

    return False, False, "", ""

# Callback para abrir o modal de importação de Excel
@callback(
    Output("modal-import-excel", "is_open"),
    Input("button-import-excel-optimization", "n_clicks"),
    Input("btn-cancel-import", "n_clicks"),
    prevent_initial_call=True
)
def open_import_excel_modal(import_clicks, cancel_clicks):
    trigger_id = ctx.triggered_id
    if trigger_id == "button-import-excel-optimization" and import_clicks:
        return True
    elif trigger_id == "btn-cancel-import" and cancel_clicks:
        return False
    return no_update

# Callback para validar o arquivo Excel e habilitar o botão de importação
@callback(
    Output("validation-message", "children", allow_duplicate=True),
    Output("btn-confirm-import", "disabled", allow_duplicate=True),
    Output("excel-data-store", "data", allow_duplicate=True),
    Output("validation-message", "style", allow_duplicate=True),
    Input("upload-excel-optimization", "contents"),
    State("upload-excel-optimization", "filename"),
    prevent_initial_call=True
)
def validate_excel_file(contents, filename):
    print("validate_excel_file")
    print(f"Filename: {filename}")

    if contents is None:
        return no_update, True, no_update, {"display": "none"}

    if not filename.endswith(('.xlsx', '.xls')):
        return html.Div("O arquivo deve ser um Excel (.xlsx ou .xls)",className="error-message"), True, None
    
    try:
        # Decodificar o conteúdo do arquivo
        content_type, content_string = contents.split(',', 1)
        decoded = base64.b64decode(content_string)
        
        # Tentar ler o arquivo Excel
        try:
            df = pd.read_excel(io.BytesIO(decoded))
            print(f"Colunas encontradas: {list(df.columns)}")
            print(f"Primeiras linhas: {df.head(2)}")
        except Exception as excel_error:
            print(f"Erro ao ler Excel: {str(excel_error)}")
            return html.Div(f"Erro ao ler o arquivo Excel: {str(excel_error)}", className="error-message"), True, None, {"display": "block"}
        
        # Verificar colunas obrigatórias
        required_columns = ["Peça", "Preço SAP novo"]
        missing_columns = [col for col in required_columns if col not in df.columns]
        
        if missing_columns:
            missing_cols_str = ", ".join(missing_columns)
            return html.Div(f"Colunas obrigatórias ausentes: {missing_cols_str}",className="error-message"), True, None
        
        # Converter coluna de peça para string
        df["Peça"] = df["Peça"].astype(str)
        
        # Converter coluna de preço para float
        try:
            df["Preço SAP novo"] = pd.to_numeric(df["Preço SAP novo"], errors='coerce')
            # Verificar se há valores NaN após a conversão
            if df["Preço SAP novo"].isna().any():
                return html.Div("Atenção: Alguns valores na coluna 'Preço SAP novo' não puderam ser convertidos para números e serão ignorados.", className="error-message"), False, df.dropna(subset=["Preço SAP novo"]).to_json(date_format='iso', orient='split'), {"display": "block"}
        except Exception as conv_error:
            print(f"Erro na conversão de preços: {str(conv_error)}")
            return html.Div(f"Erro ao converter preços: {str(conv_error)}", className="error-message"), True, None, {"display": "block"}
        
        # Verificar se há dados
        if len(df) == 0:
            return html.Div("O arquivo não contém dados.", className="error-message"), True, None, {"display": "block"}
        
        # Sucesso - armazenar dados e habilitar botão de importação
        json_data = df.to_json(date_format='iso', orient='split')
        print(f"Dados validados com sucesso: {len(df)} linhas")
        
        return html.Div([
            html.Span("Arquivo validado com sucesso. ", className="success-message"),
            html.Br(),
            html.Span(f"Encontradas {len(df)} linhas com dados válidos. Clique em 'Importar' para continuar.")
        ]), False, json_data, {"display": "block"}
        
    except Exception as e:
        import traceback
        error_details = traceback.format_exc()
        print(f"Erro ao validar arquivo: {str(e)}")
        print(error_details)
        return html.Div(f"Erro ao processar o arquivo: {str(e)}", className="error-message"), True, None, {"display": "block"}

# Callback para processar a importação do Excel quando o botão importar for clicado
@callback(
    Output("modal-import-excel-body", "children"),
    Output("modal-import-excel-footer", "children"),
    Input("btn-confirm-import", "n_clicks"),
    prevent_initial_call=True
)
def show_loading_on_import(n_clicks):
    if n_clicks:
        # Criar um spinner centralizado com o mesmo tamanho aproximado do modal original
        loading_container = html.Div(
            dbc.Spinner(color="primary", size="lg"),
            style={
                "display": "flex",
                "justifyContent": "center",
                "alignItems": "center",
                "height": "200px",  # Altura aproximada do modal original
                "width": "100%"
            }
        )
        # Retornar o spinner para o body e nada para o footer
        return loading_container, None
    return no_update, no_update

@callback(
    Output("optimization-table", "rowData", allow_duplicate=True),
    Output("modal-import-excel", "is_open", allow_duplicate=True),
    Output("toast-approval-optimization", "is_open", allow_duplicate=True),
    Output("toast-approval-optimization", "header", allow_duplicate=True),
    Output("toast-approval-optimization", "children", allow_duplicate=True),
    Output("modal-import-excel-body", "children", allow_duplicate=True),
    Output("modal-import-excel-footer", "children", allow_duplicate=True),
    Input("btn-confirm-import", "n_clicks"),
    State("excel-data-store", "data"),
    State("optimization-table", "rowData"),
    prevent_initial_call=True
)
def process_excel_import(n_clicks, excel_data, current_table_data):
    print("process_excel_import")

    if n_clicks is None or excel_data is None:
        print("Nenhum clique ou dados do Excel")
        return no_update, no_update, no_update, no_update, no_update, no_update, no_update

    try:
        # Converter os dados do JSON para DataFrame
        print("Tentando converter dados JSON para DataFrame")
        imported_df = pd.read_json(excel_data, orient='split')
        print(f"DataFrame importado: {len(imported_df)} linhas")

        # Para debug - verificar os tipos de dados e valores
        debug_info = f"Colunas do Excel: {list(imported_df.columns)}\n"
        debug_info += f"Tipos de dados: {imported_df.dtypes.to_dict()}\n"
        debug_info += f"Primeiras linhas: {imported_df.head(3).to_dict()}\n"
        print(debug_info)

        # Mapear os nomes das colunas do Excel para os nomes das colunas da tabela
        column_mapping = {
            "Peça": "peca",
            "Preço SAP novo": "preco_sap_novo"
        }

        # Renomear as colunas do DataFrame importado
        imported_df = imported_df.rename(columns=column_mapping)
        print(f"Colunas após renomeação: {list(imported_df.columns)}")

        # Verificar se as colunas necessárias existem no DataFrame importado
        if "peca" not in imported_df.columns or "preco_sap_novo" not in imported_df.columns:
            print(f"Colunas obrigatórias não encontradas: {list(imported_df.columns)}")

            return no_update, False, True, "Erro", f"Colunas obrigatórias não encontradas após mapeamento. {debug_info}", original_body, original_footer

        # Verificar se há dados na tabela atual
        if not current_table_data or len(current_table_data) == 0:
            print("Tabela atual está vazia")            
            return no_update, False, True, "Erro", "Não há dados na tabela para atualizar.", original_body, original_footer

        # Criar uma cópia dos dados da tabela para modificação
        updated_data = current_table_data.copy()
        print(f"Dados atuais copiados: {len(updated_data)} linhas")

        # Criar um dicionário para facilitar a busca
        import_dict = {}
        for _, row in imported_df.iterrows():
            try:
                peca = str(row["peca"]).strip()
                if pd.notna(row["preco_sap_novo"]):
                    preco = float(row["preco_sap_novo"])
                    import_dict[peca] = preco
                    print(f"Adicionado ao dicionário: peça {peca}, preço {preco}")
            except Exception as e:
                print(f"Erro ao processar linha do Excel: {str(e)}")
                continue

        print(f"Dicionário de importação criado com {len(import_dict)} itens")
        if len(import_dict) > 0:
            print(f"Exemplo de item: {list(import_dict.items())[0]}")

        # Atualizar os valores na tabela atual
        updated_rows = 0
        for i, row in enumerate(updated_data):
            try:
                peca = str(row.get("peca", "")).strip()
                if peca and peca in import_dict:
                    print(f"Atualizando peça {peca} com preço {import_dict[peca]}")
                    # updated_data[i]["preco_sap_novo"] = import_dict[peca]

                    updated_data = recalculate_row(
                        df=pl.DataFrame(updated_data),
                        peca=peca,
                        novo_valor=import_dict[peca]
                    )

                    # updated_data[i]["new_alteration"] = "sim"
                    # updated_data[i]["status"] = "manual"

                    updated_rows += 1
            except Exception as e:
                print(f"Erro ao atualizar linha {i}: {str(e)}")
                continue

        if updated_rows == 0:
            print("Nenhuma peça correspondente encontrada")
            return no_update, False, True, "Aviso", f"Nenhuma peça correspondente encontrada no arquivo Excel.", original_body, original_footer

        print(f"Atualização concluída: {updated_rows} peças atualizadas")

        return updated_data, False, True, "Importação Concluída", f"{updated_rows} peças foram atualizadas com sucesso!", original_body, original_footer
    
    except Exception as e:
        import traceback
        error_details = traceback.format_exc()
        print(f"Erro na importação: {str(e)}")
        print(error_details)
        
        return no_update, False, True, "Erro na Importação", f"Ocorreu um erro ao importar os dados: {str(e)}", original_body, original_footer

# Callback para o download da tabela em Excel
@callback(
    Output("download-excel-optimization", "data"),
    Input("btn-download-excel-optimization", "n_clicks"),
    State("optimization-table", "rowData"),
    prevent_initial_call=True
)
def handle_excel_download_optimization(n_clicks, row_data):
    if n_clicks is None or not row_data:
        return None

    col_to_export = {
        'peca': _('Peça'),
        'estrategia_utilizada': _('Estratégia'),
        'var_marca': _('Marca'),
        'var_elasticidade': _('Elasticidade'),
        'var_aplicacoes': _('Qtd de aplicações'),
        'var_frota': _('Frota disponível'),
        'var_estoquegm': _('Estoque GM'),
        'var_anofrota': _('Ano frota'),
        'custo_medio_unit': _('Custo medio'),
        'preco_sap_atual': _('Preço SAP atual'),
        'preco_sap_novo': _('Preço SAP novo'),
        # 'gross': _('Gross'), # temporário para testar a importação
        # 'gross_cap': _('Gross Cap'), # temporário para testar a importação
        # 'gross_mc': _('Gross MC'), # temporário para testar a importação
        # 'gross_cap_mc': _('Gross Cap MC'), # temporário para testar a importação
        # 'gross_final': _('Gross Final') # temporário para testar a importação
    }

    df = pd.DataFrame(row_data)

    print("preco_sap_atual", df["preco_sap_atual"].sum())
    print("preco_sap_novo", df["preco_sap_novo"].sum())

    df_export = df[col_to_export.keys()].rename(columns=col_to_export)

    return dcc.send_data_frame(df_export.to_excel, "optimization_data.xlsx", index=False)

# Callback para abrir o modal de confirmação de aprovação
@callback(
    Output("modal-confirm-approval", "is_open"),
    Input("button-approval-optimization", "n_clicks"),
    prevent_initial_call=True,
)
def open_confirm_approval_modal(n_clicks):
    if n_clicks:
        return True
    return False

# Callback para processar a confirmação de aprovação
@callback(
    Output("modal-confirm-approval", "is_open", allow_duplicate=True),
    Output("toast-approval-optimization", "is_open", allow_duplicate=True),
    Output("toast-approval-optimization", "header", allow_duplicate=True),
    Output("toast-approval-optimization", "children", allow_duplicate=True),
    Input("btn-confirm-approval", "n_clicks"),
    Input("btn-cancel-approval", "n_clicks"),
    State('optimization-table', 'rowData'),
    State("store-token", "data"),
    prevent_initial_call=True,
)
def handle_to_approval(confirm_clicks, cancel_clicks, table_data, user_data):
    triggered_id = ctx.triggered_id
    
    # Fechar o modal em ambos os casos
    if triggered_id == "btn-cancel-approval" and cancel_clicks:
        return no_update, False, False, ""
    
    if triggered_id == "btn-confirm-approval" and confirm_clicks:
        try:
            df = pd.DataFrame(table_data)
            filtered_df = df.loc[df["new_alteration"] == "sim"]
            
            if filtered_df.empty:
                return no_update, False, True, "Aviso", "Não há alterações para enviar para aprovação."

            variables_to_send = {
                "user_token": user_data["access_token"],
                "table_data": filtered_df,
            }

            send_to_approval("optimization", variables_to_send)

            return False, True, "Sucesso", "Dados enviados para aprovação com sucesso!"
        except Exception as e:
            return False, True, "Erro", f"Erro ao enviar para aprovação: {str(e)}"
    
    return no_update, False, False, "", ""

# Callback para aprovação/rejeição
@callback(
    Output("toast-approval-reject-optimization", "is_open"),
    Output("toast-approval-reject-optimization", "header"),
    Output("toast-approval-reject-optimization", "children"),
    Input("button-approval-accept-optimization", "n_clicks"),
    Input("button-approval-reject-optimization", "n_clicks"),
    State("optimization-table", "rowData"),
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
        return html.P("Erro: Não há dados para aprovar/recusar", className="error-message")

    try:
        uuid_alteracoes = table_data[0]["uuid_alteracoes"]

        variables_to_send = {
            "uuid_alteracoes": uuid_alteracoes,
            "status": status,
            "user_token": user_data["access_token"],
            "target_table": "optimization",
        }

        update_approval_status(variables_to_send)
        return True, f"{status_text}", f"Status alterado para {status_text}"

    except Exception as e:
        print(f"Erro ao processar aprovação: {str(e)}")
        return True, "Erro", f"Erro ao processar aprovação: {str(e)}"
