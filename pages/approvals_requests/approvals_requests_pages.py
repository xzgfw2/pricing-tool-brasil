"""Approval Requests Page Module

This module provides the UI components and callbacks for the approval requests page.
It displays a table of approval requests for a user and allows viewing detailed information
about each request in a modal dialog.
"""

from typing import Dict, List, Any, Optional, Tuple
import logging
import dash_bootstrap_components as dbc
from dash import html, Input, Output, State, callback, ALL
from dash.development.base_component import Component
from components.Modal import create_modal
from components.Table import create_table
from components.Tabs import create_tabs
from components.Helper_button_with_modal import create_help_button_with_modal
from api.get_requests_for_approval_by_user import get_requests_for_approval_by_user
from api.get_requests_for_approval_by_id import get_requests_for_approval_by_id
from static_data.helper_text import helper_text
from styles import MAIN_TITLE_STYLE, CONTAINER_HELPER_BUTTON_STYLE
from translations import _, setup_translations
from utils.handle_no_data_to_show import handle_no_data_to_show
from pages.approvals_requests.approvals_requests_utils import (
    handle_process_name,
    handle_status_name,
    handle_date_format,
)

logger = logging.getLogger(__name__)

def transform_columns_format(col: List[str]) -> List[Dict[str, str]]:
    """
    Transform DataFrame column names into the format required by ag-grid.
    
    Args:
        col: List of column names from a pandas DataFrame
        
    Returns:
        List of dictionaries with 'headerName' and 'field' keys for ag-grid
        
    Example:
        >>> transform_columns_format(['col1', 'col2', 'uuid_alteracoes'])
        [{'headerName': 'col1', 'field': 'col1'}, {'headerName': 'col2', 'field': 'col2'}]
    """
    formated_columns = []
    ignored_columns = ["uuid_alteracoes", "source_table", "manual"]

    for col_id in col:
        if col_id not in ignored_columns:
            formated_columns.append({"headerName": col_id, "field": col_id})

    return formated_columns

helper_button = html.Div(
    create_help_button_with_modal(
        modal_title=helper_text["approvals_requests"]["title"],
        modal_body=helper_text["approvals_requests"]["description"],
    ), style=CONTAINER_HELPER_BUTTON_STYLE,
)

def get_table_data(user_data: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    Fetch and process approval requests data for the specified user.
    
    Args:
        user_data: Dictionary containing user information, including 'id'
        
    Returns:
        List of dictionaries representing approval requests data ready for display
    """
    user_id = user_data.get('id')
    
    if not user_id:
        logger.warning("No user ID provided in user_data")
        return []

    try:
        df = get_requests_for_approval_by_user(user_id)
    except Exception as e:
        logger.error(f"Error fetching requests for approval: {e}")
        return []

    if df is None:
        return []

    df = handle_date_format(df)
    df = handle_status_name(df)
    df = handle_process_name(df)
    df["details"] = "Ver detalhes 🔍"

    return df

columns = [
    {"name": "Data", "id": "data_alteracoes_data"},
    {"name": "Processo", "id": "source_table"},
    {"name": "ID Requisição", "id": "uuid_alteracoes"},
    {"name": "Status", "id": "status"},
    {"name": "Detalhes", "id": "details"},
]

modal = create_modal(
    modal_id="approval-requests-modal",
    modal_title="Detalhes da Solicitação",
    modal_body_id="approval-requests-modal-body",
    modal_footer_id="approval-requests-modal-footer",
)

def get_layout(user_data: Dict[str, Any]) -> Component:
    """
    Generate the layout for the approval requests page.
    
    Args:
        user_data: Dictionary containing user information
        
    Returns:
        Dash component representing the page layout
        
    The layout includes:
    - A title with helper button
    - A table of approval requests or a "no data" message
    - A modal for displaying request details
    """
    df = get_table_data(user_data)

    all_status_data = df.to_dict("records")
    pending_data = df[df["status"] == "Pendente"].to_dict("records")
    approved_data = df[df["status"] == "Aprovado"].to_dict("records")
    rejected_data = df[df["status"] == "Rejeitado"].to_dict("records")

    no_data_message = handle_no_data_to_show(message="Nenhuma requisição encontrada para este usuário")
    no_historic_data_message = handle_no_data_to_show(message="Você não tem histórico de requisição de aprovação.")

    columns_test = [
        {'headerName': 'Data', 'field': 'data_alteracoes_data'},
        {'headerName': 'Processo', 'field': 'source_table'},
        {'headerName': 'ID Requisição', 'field': 'uuid_alteracoes'},
        {'headerName': 'Status', 'field': 'status'},
        {'headerName': 'Detalhes', 'field': 'details'},
    ]

    tabs_config = [
        {
            "id": "approval-requests-tab-all",
            "label": "Todos",
            "content": html.Div([
                create_table(
                    table_id={"type": "approval-table", "index": "all"},
                    data=all_status_data if all_status_data else [],
                    columns=columns_test,
                    column_size="responsiveSizeToFit",
                    pagination=False,
                    style={'display': 'block' if all_status_data else 'none'}
                ),
                html.Div(no_data_message, style={'display': 'block' if not all_status_data else 'none'})
            ]),
        },
        {
            "id": "approval-requests-tab-pending",
            "label": "Pendentes",
            "content": html.Div([
                create_table(
                    table_id={"type": "approval-table", "index": "pending"},
                    data=pending_data if pending_data else [],
                    columns=columns_test,
                    column_size="responsiveSizeToFit",
                    pagination=False,
                    style={'display': 'block' if pending_data else 'none'}
                ),
                html.Div(no_data_message, style={'display': 'block' if not pending_data else 'none'})
            ]),
        },
        {
            "id": "approval-requests-tab-approved",
            "label": "Aprovados",
            "content": html.Div([
                create_table(
                    table_id={"type": "approval-table", "index": "approved"},
                    data=approved_data if approved_data else [],
                    columns=columns_test,
                    column_size="responsiveSizeToFit",
                    pagination=False,
                    style={'display': 'block' if approved_data else 'none'}
                ),
                html.Div(no_data_message, style={'display': 'block' if not approved_data else 'none'})
            ]),
        },
        {
            "id": "approval-requests-tab-rejected",
            "label": "Rejeitados",
            "content": html.Div([
                create_table(
                    table_id={"type": "approval-table", "index": "rejected"},
                    data=rejected_data if rejected_data else [],
                    columns=columns_test,
                    column_size="responsiveSizeToFit",
                    pagination=False,
                    style={'display': 'block' if rejected_data else 'none'}
                ),
                html.Div(no_data_message, style={'display': 'block' if not rejected_data else 'none'})
            ]),
        },
    ]

    header = html.Div([
        html.H1(_("Requisições de Aprovação"), style=MAIN_TITLE_STYLE),
        helper_button
    ], className="container-title")

    tabs = create_tabs(
        active_tab="approval-requests-tab-pending",
        tabs_config=tabs_config,
        class_name="tabs-content"
    )

    content = html.Div([
        tabs
    ], className="space-content-margin")

    return html.Div([
        header,
        no_historic_data_message if df is None else content,
        modal,
    ])

approval_requests_page = html.Div([
    dbc.Spinner(
        html.Div(id="approval-requests-content"),
        color="primary",
        size="lg",
        fullscreen=True,
    )
])

@callback(
    Output("approval-requests-content", "children"),
    [
        Input("store-token", "data"),
        Input("store-language", "data"),
    ],
)
def update_approval_requests_content(user_data: Dict[str, Any], language: str) -> Component:
    """
    Callback to update the approval requests content when user data or language changes.
    
    Args:
        user_data: Dictionary containing user information from store-token
        language: Selected language code from store-language
        
    Returns:
        Updated page layout component
    """
    global _
    _ = setup_translations(language)

    return get_layout(user_data)

@callback(
    Output("approval-requests-modal", "is_open"),
    Output("approval-requests-modal-body", "children"),
    Input({"type": "approval-table", "index": ALL}, "cellClicked"),
    State({"type": "approval-table", "index": ALL}, "rowData"),
    prevent_initial_call=True,
)
def open_modal_on_click(
    cell_clicked_list: List[Optional[Dict[str, Any]]],
    table_data_list: List[List[Dict[str, Any]]],
) -> Tuple[bool, Optional[Component]]:
    """
    Callback to open a modal with detailed information when a table row is clicked.
    
    Args:
        cell_clicked_list: List of cell click information from all tables
        table_data_list: List of data from all tables
        
    Returns:
        Tuple containing:
        - Boolean indicating whether the modal should be open
        - Component to display in the modal body, or None if modal should be closed
    """
    triggered_idx = None
    cell_clicked = None

    for i, cell_click_data in enumerate(cell_clicked_list):
        if cell_click_data is not None:
            triggered_idx = i
            cell_clicked = cell_click_data
            break

    if triggered_idx is None or cell_clicked is None:
        return False, None

    table_data = table_data_list[triggered_idx] if table_data_list else None

    if not table_data:
        logger.warning("No table data available")
        return False, None

    try:
        cell_info = _extract_cell_info(cell_clicked)

        if not cell_info:
            return False, None

        if not _is_details_column_clicked(cell_info):
            return False, None

        request_id = _get_request_id_from_table(cell_info, table_data)

        if not request_id:
            return False, None

        modal_content = _create_modal_content(request_id)
        return True, modal_content

    except Exception as e:
        logger.error(f"Error displaying request details: {e}")
        return True, _create_error_content(str(e))

def _extract_cell_info(active_cell: Optional[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
    """Extract and validate cell information from the active cell."""
    return active_cell if active_cell else None


def _is_details_column_clicked(cell_info: Dict[str, Any]) -> bool:
    """Check if the clicked column is the details column."""

    print("_is_details_column_clicked")
    
    return cell_info.get("colId") == "details"


def _get_request_id_from_table(
    cell_info: Dict[str, Any], 
    table_data: List[Dict[str, Any]]
) -> Optional[str]:
    """Extract request ID from table data based on clicked cell."""
    
    row_id = int(cell_info.get("rowId"))

    if not _is_valid_row_index(row_id, table_data):
        return None

    table_row = table_data[row_id]
    request_id = table_row.get("uuid_alteracoes")

    if not request_id:
        logger.warning("No uuid_alteracoes found in table row")

    return request_id

def _is_valid_row_index(row_id: Optional[int], table_data: List[Dict[str, Any]]) -> bool:
    """Validate if the row index is within table bounds."""
    
    if row_id is None or row_id >= len(table_data):
        logger.warning(f"Invalid row index: {row_id}, table data length: {len(table_data)}")
        return False
    return True


def _create_modal_content(request_id: str) -> Component:
    """Create the modal content with request details."""

    logger.info(f"Fetching details for request ID: {request_id}")
    df = get_requests_for_approval_by_id(request_id)

    if df is None or df.empty:
        logger.warning(f"No details found for request ID: {request_id}")
        return _create_no_data_content()

    return _create_details_table(df)


def _create_details_table(df) -> Component:
    """Create the details table component."""

    return html.Div([
        create_table(
            table_id="approval-details-table",
            data=df.to_dict("records"),
            columns=transform_columns_format(df.columns),
            column_size="responsiveSizeToFit",
            style={'height': '500px', 'width': '100%'}
        ),
    ])


def _create_no_data_content() -> Component:
    """Create content for when no data is found."""
    return html.Div("Nenhum detalhe encontrado para esta solicitação")


def _create_error_content(error_message: str) -> Component:
    """Create content for error scenarios."""
    return html.Div(f"Erro ao carregar detalhes: {error_message}")
