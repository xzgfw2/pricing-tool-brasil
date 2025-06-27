from dash import dcc, html

STYLE_CONTAINER_LABEL_INPUT = {
    'width': '100%',
    'marginBottom': '5px',
    'display': 'flex',
    'flexDirection': 'column',
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
    'width': '100%',
    'padding': '4px 8px',
    'fontSize': '12px',
    'border': '1px solid #ccc',
    'borderRadius': '4px',
    'outline': 'none',
    'boxSizing': 'border-box'
}

def create_input(id, input_type='number', label_text=None, input_value=None, style=None, **kwargs):
    children = []

    if label_text:
        label_for = str(id) if isinstance(id, dict) else id
        children.append(html.Label(label_text, htmlFor=label_for, style=STYLE_LABEL))

    input_style = STYLE_INPUT.copy()
    if style:
        input_style.update(style)

    if input_value is not None:
        children.append(dcc.Input(id=id, type=input_type, value=input_value, style=input_style, **kwargs))
    else:
        children.append(dcc.Input(id=id, type=input_type, style=input_style, **kwargs))

    return html.Div(children=children, style=STYLE_CONTAINER_LABEL_INPUT)
