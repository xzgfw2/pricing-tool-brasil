MAIN_CONTENT_STYLE = {
    "width": "90%",
    "marginRight": "2rem",
    "padding": "2rem 1rem",
}

MAIN_CONTAINER_STYLE = {
    "display": "flex",
    "flexDirection": "row",
    "height": "100%",
}

MAIN_TITLE_STYLE = {
    "textAlign": "center",
    "fontSize": "24px",
    "fontWeight": "bold",
    "flex": "1",
}

CONTAINER_CARD_STYLE = {
    "display": "flex",
    "justifyContent": "space-evenly",
    "margin": "20px 0px",
}

CAPTAIN_CARD_INSIDE_STYLE = {
    "border": "none",
    "textAlign": "center",
    "width": "100%",
    "height": "100%",
}

CONTAINER_BUTTONS_STYLE = {
    "display": "flex",
    "justifyContent": "flex-end",
    "gap": "15px",
    "marginBottom": "20px",
    "marginTop": "20px",
}

CONTAINER_BUTTONS_DUAL_STYLE = {
    **CONTAINER_BUTTONS_STYLE,
    "justifyContent": "space-between",
}

BUTTON_STYLE = {
    "height": "40px",
    "width": "80px",
}

CONTAINER_TABLE_STYLE = {
    "width": "100%",
}

CONTAINER_TABLE_BUILD_UP_STYLE = {
    "display": "flex",
    "gap": "50px",
    "marginTop": "40px",
    "width": "100%",
}

# Estilos modernos para tabelas
TABLE_HEADER_STYLE = {
    "backgroundColor": "#f8f9fa",
    "color": "#495057",
    "fontWeight": "600",
    "fontSize": "0.875rem",
    "textAlign": "left",
    "padding": "12px 16px",
    "borderBottom": "2px solid #dee2e6",
    "whiteSpace": "nowrap",
    "fontFamily": "'Segoe UI', system-ui, -apple-system, sans-serif",
}

TABLE_CELL_STYLE = {
    "padding": "12px 16px",
    "fontSize": "0.875rem",
    "color": "#212529",
    "borderBottom": "1px solid #dee2e6",
    "fontFamily": "'Segoe UI', system-ui, -apple-system, sans-serif",
    "whiteSpace": "nowrap",
    "overflow": "hidden",
    "textOverflow": "ellipsis",
}

TABLE_STYLE = {
    "border": "1px solid #dee2e6",
    "borderRadius": "8px",
    "overflow": "hidden",
    "backgroundColor": "white",
    "boxShadow": "0 1px 3px rgba(0,0,0,0.1)",
}

TABLE_CONTAINER_STYLE = {
    "padding": "1rem",
    "backgroundColor": "#f8f9fa",
    "borderRadius": "8px",
    "marginTop": "1rem",
}

# Estilo para linhas alternadas
TABLE_STRIPE_STYLE = {
    "backgroundColor": "#f8f9fa",
}

# Estilo para hover nas linhas
TABLE_ROW_HOVER_STYLE = {
    "backgroundColor": "#f2f4f6",
}

# Estilo para células selecionadas
TABLE_SELECTED_CELL_STYLE = {
    "backgroundColor": "#e9ecef",
    "borderColor": "#dee2e6",
}

TABLE_TITLE_STYLE = {
    "fontWeight": "700",
    "backgroundColor": "dodgerblue",
    "color": "white",
    "fontSize": "14px",
    "padding": "10px",
    "marginBottom": "0px",
}

TABLE_NOTE_PARAGRAPH = {
    "color": "black",
    "fontSize": "14px",
    "padding": "5px",
    "marginBottom": "0px",
}

TABLE_SIZE_STYLE = {
    'margin': 'auto',
    'width': '80%',
}

# Sidebar

SVG_STYLE = {
    "width": "16px",
}

NAV_ITEM_STYLE = { 
    "color": "black", 
    "cursor": "pointer",
}

CONTAINER_LANGUAGE_SELECTOR_STYLE = {
    "display": "flex",
    "padding": "0.5rem 1rem",
    "width": "40%",
}

LANGUAGE_SELECTOR_STYLE = {
    'border': 'none',
    'borderRadius': '5px',
    'width': '100%'
}

# Card component

CARD_TITLE_STYLE = {
    "fontWeight": "700",
    "backgroundColor": "dodgerblue",
    "color": "white",
    "padding": "5px",
}

CARD_STYLE = {
    "width": "20%",
    "textAlign": "center",
    "borderRadius": "5px",
    "padding": "10px",
    "display": "flex",
    "flexDirection": "column",
}

CARD_INSIDE_STYLE = {
    "border": "2px solid dodgerblue",
    "textAlign": "center",
    "flex": "1",
    "display": "flex",
    "flexDirection": "column",
    "justifyContent": "center",
}

CARD_INSIDE_STYLE_OPTION_LEFT = CARD_INSIDE_STYLE.copy()
CARD_INSIDE_STYLE_OPTION_LEFT.update({
    "padding": "10px 10px 10px 30px",
    "alignItems": "flex-start",
})

CARD_INSIDE_STYLE_OPTION_CENTER = CARD_INSIDE_STYLE.copy()
CARD_INSIDE_STYLE_OPTION_CENTER.update({
    "padding": "10px 10px 10px 10px",
    "alignItems": "center",
})

DROPDOWN_STYLE = {
    "width": "150px",
}

DROPDOWN_CONTAINER_STYLE = {
    "display": "flex",
    "justifyContent": "space-between",
    "padding": "0px 20px",
}

CONTAINER_HELPER_BUTTON_STYLE = {
    "display": "flex",
    "alignItems": "center",
}

HELPER_MESSAGE = {
    "color": "red",
    "marginBottom": "20px",
}

TOAST_STYLE = {
    "position": "fixed", 
    "top": 40,
    "right": 40,
    "width": 350,
    "backgroundColor": "white",
}