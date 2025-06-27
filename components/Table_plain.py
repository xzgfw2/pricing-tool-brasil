from dash import dash_table
from styles import TABLE_CELL_STYLE, TABLE_HEADER_STYLE, TABLE_STYLE

def create_table_plain(data, columns, table_id, page_size=15):
    # new_columns = columns + [{"name": "Detalhes", "id": "detalhes"}]
    # new_data = [{**row, "detalhes": "Ver detalhes 🔍"} for row in data]

    return dash_table.DataTable(
        id=table_id,
        columns=columns,
        data=data,
        style_table=TABLE_STYLE,
        # style_table={"width": "1500px", "margin": "0 auto", "overflowX": "auto"},
        style_cell=dict(TABLE_CELL_STYLE, **{
            'width': '130px',
        }),
        style_cell_conditional=[
            {
                'if': {'column_id': 'id'},
                'minWidth': '130px',
                'width': '130px',
                'maxWidth': '130px',
            },
            {
                'if': {'column_id': 'detalhes'},
                'textDecoration': 'none',
                'color': 'blue',
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
