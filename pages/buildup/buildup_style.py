STYLE_TABLE_PARAMETERS = {
    'height': '600px',
    'marginBottom': '20px',
    'width': '100%',
}

STYLE_LABEL = {
    'fontSize': '14px',
    'marginBottom': '5px',
    'color': '#333',
    'fontWeight': 'bold',
}

STYLE_INPUT = {
    'width': '100%',
    'padding': '8px 12px',
    'fontSize': '14px',
    'border': '1px solid #ccc',
    'borderRadius': '5px',
    'outline': 'none',
    'boxSizing': 'border-box',
    'transition': 'border-color 0.3s ease',
}

STYLE_CONTAINER_LABEL_INPUT = {
    'flex': '1 1 calc(33.33% - 20px)',
    'minWidth': '250px',
    'marginBottom': '20px',
    'display': 'flex',
    'flexDirection': 'column',
}

STYLE_CONTAINER_INPUTS = {
    'display': 'flex',
    'flexWrap': 'wrap',
    'gap': '20px',
    'justifyContent': 'flex-start',
}

STYLE_BUILDUP_FACTORS_CONTAINER = {
    'width': '100%',
    'padding': '20px',
}

STYLE_TAB_CONTENT = {
    'width': '100%',
    'height': '100%',
    'overflow': 'hidden'
}

STYLE_BUILDUP_SECTIONS_CONTAINER = {
    'display': 'flex',
    'flexWrap': 'nowrap',
    'gap': '20px',
    'overflowX': 'auto',
    'overflowY': 'auto',  
    'paddingBottom': '15px',
    'width': '100%',
    'marginTop': '20px',
    'maxHeight': 'calc(100vh - 250px)',
}

STYLE_BUILDUP_SECTION = {
    'flex': '0 0 350px',  
    'margin': '10px',
    'padding': '15px',
    'border': '1px solid #ddd',
    'borderRadius': '5px',
    'backgroundColor': '#fff',
    'height': 'fit-content',
    'minWidth': '350px'
}

STYLE_BUILDUP_TITLE = {
    'marginBottom': '20px',
    'color': '#333',
    'fontWeight': 'bold'
}

STYLE_BUILDUP_TABLE = {
    'overflowX': 'auto',
    'width': '300px',  
    'minWidth': '300px'
}

CONTAINER_INPUT_DATE_STYLE = {
    'display': 'flex',
    'gap': '10px'
}

STYLE_TABLE_CELL = {
    'textAlign': 'left',
    'padding': '8px',
    'whiteSpace': 'normal',
    'height': 'auto',
}

STYLE_TABLE_CELL_FIELD = {
    'width': '180px',
}

STYLE_TABLE_CELL_VALUE = {
    'width': '120px',
}

STYLE_TABLE_HEADER = {
    'backgroundColor': '#f8f9fa',
    'fontWeight': 'bold',
    'textAlign': 'center'
}

STYLE_DEVELOPMENT_BANNER = {
    "padding": "20px",
    "color": "white",
    "background": "dodgerblue",
    "fontWeight": "600",
    "marginBottom": "20px",
    "width": "300px",
}

STYLE_DATE_CONTAINER = {
    "marginBottom": "20px",
}

STYLE_TABS_CONTAINER = {
    "width": "100%"
}

STYLE_TABS = {
    "marginBottom": "20px"
}

STYLE_PAGE_CONTAINER = {
    'padding': '20px',
    'height': '100%',
}

STYLE_INPUT_GROUP = {
    'display': 'flex',
    'justifyContent': 'space-between',
    'width': '290px',
    'marginBottom': '5px'
}

STYLE_SINGLE_INPUT = {
    'width': '135px'
}

STYLE_INPUTS_CONTAINER = {
    'display': 'flex',
    'flexDirection': 'column',
    'marginBottom': '15px',
    'width': '300px',
    'padding': '0 5px'
}

STYLE_TABLE_HEADER_BUILDUP = {
    'textAlign': 'center',
    'fontWeight': 'bold',
    'backgroundColor': '#f8f9fa',
    'padding': '10px'
}

STYLE_TABLE_CELL_BUILDUP = {
    'textAlign': 'center',
    'padding': '10px',
    'whiteSpace': 'normal',
    'height': 'auto',
}

# Table Styles
STYLE_BUILDUP_FACTORS_TABLE_HEADER = {
    'textAlign': 'center',
    'fontWeight': 'bold',
    'backgroundColor': '#f8f9fa',
    'padding': '10px'
}

STYLE_BUILDUP_FACTORS_TABLE_CELL = {
    'textAlign': 'center',
    'padding': '10px',
    'whiteSpace': 'normal',
    'height': 'auto',
}

STYLE_BUILDUP_FACTORS_TABLE_CELL_CONDITIONAL = [
    {
        'if': {'column_id': 'buildup_factors'},
        'textAlign': 'left',
    }
]

STYLE_SIMULATION_TABLE_CELL = {
    'textAlign': 'left',
    'padding': '8px',
    'whiteSpace': 'normal',
    'height': 'auto',
}

STYLE_SIMULATION_TABLE_CELL_CONDITIONAL = [
    {
        'if': {'column_id': 'field'},
        'width': '180px',
    },
    {
        'if': {'column_id': 'value'},
        'width': '120px',
    }
]

STYLE_SIMULATION_TABLE = {
    'overflowX': 'auto',
    'width': '300px',
    'minWidth': '300px'
}

STYLE_SIMULATION_TABLE_HEADER = {
    'backgroundColor': '#f8f9fa',
    'fontWeight': 'bold',
    'textAlign': 'center'
}

CONTAINER_INPUTS_STYLE = {
    'display': 'flex',
    'justifyContent': 'space-between',
    'width': '290px',  # Total width accounting for gap
    'marginBottom': '5px'
}

CONTAINER_INPUTS_SIZE_STYLE = {
    'width': '135px', # Fixed width for each input container
}

CONTAINER_SIMULATION_STYLE = {
    'display': 'flex',
    'flexDirection': 'column',
    'marginBottom': '15px',
    'width': '300px',
    'padding': '0 5px'
}

def get_style_data_conditional(non_editable_fields):
    return [
        {
            'if': {
                'column_id': 'value',
                'filter_query': f'{{field}} = "{field}"'
            },
            'backgroundColor': 'rgb(250, 250, 250)',
            'color': 'darkgrey',
        } for field in non_editable_fields
    ]
