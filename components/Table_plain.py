from dash import dash_table
from styles import TABLE_CELL_STYLE, TABLE_HEADER_STYLE, TABLE_STYLE
from typing import List, Dict, Any

def create_table_plain(
        data: List[Dict[str, Any]],
        columns: List[Dict[str,Any]],
        table_id: str,
        page_size: int = 15
    ):
    """
    Create a plain table with the specified data and columns.
    
    Args:
        data: List of dictionaries representing the table data
        columns: List of dictionaries representing the table columns
        table_id: ID of the table
        page_size: Number of rows to display per page
        
    Returns:
        Dash DataTable component
    """
    return dash_table.DataTable(
        id=table_id,
        columns=columns,
        data=data,
        style_table=TABLE_STYLE,
        # style_table={"width": "1500px", "margin": "0 auto", "overflowX": "auto"},
        # style_cell=dict(TABLE_CELL_STYLE, **{
        #     'width': '130px',
        # }),
        style_cell=TABLE_CELL_STYLE,
        style_cell_conditional=[
            {
                'if': {'column_id': 'details'},
                'cursor': 'pointer',
            },
        ],
        style_header=dict(TABLE_HEADER_STYLE, **{
            'textAlign': 'center'
        }),
        style_data_conditional=[
            {
                'if': {'row_index': 'odd'},
                'backgroundColor': '#f9f9f9'
            }
        ],
        page_action='native',
        page_size=page_size,
    )
