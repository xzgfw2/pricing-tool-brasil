import dash_ag_grid as dag

def create_table(
        table_id,
        row_data,
        column_defs,
        column_size="autoSize",
        dash_grid_options=None,
        style=None,
        editable=False,
        selection_mode="multiple",
        pagination=True,
        rows_per_page=20,
        persistence=False,
        persisted_props=None,
        persistence_type=None,
    ):
    # Configurações padrão da grid
    default_col_def = {
        "sortable": True,
        "filter": True,
        "resizable": True,
        "editable": editable,
        "headerClass": "ag-header-cell-center",
        "headerStyle": {
            "text-align": "center",
            "justify-content": "center",
            "display": "flex",
            "align-items": "center"
        },
        "cellStyle": {"text-align": "right"},
        "width": 100
    }

    # Configurações da grid
    grid_options = dash_grid_options or {}
    grid_options.update({
        "pagination": pagination,
        "paginationPageSize": rows_per_page,
        "rowSelection": selection_mode,
    })

    # Estilo padrão se não for fornecido
    if style is None:
        style = {'height': '100%', 'width': '100%'}

    return dag.AgGrid(
        id=table_id,
        rowData=row_data,
        columnDefs=column_defs,
        columnSize=column_size,
        dashGridOptions=grid_options,
        defaultColDef=default_col_def,
        style=style,
        persistence=persistence,
        persisted_props=persisted_props,
        persistence_type=persistence_type,
    )