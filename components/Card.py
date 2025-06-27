from dash import html
import dash_bootstrap_components as dbc
from utils.calculate_diff import calculate_diff
from utils.calculate_diff_pp import calculate_diff_pp
from utils.format_number import format_number
from utils.format_number_decimal import format_number_decimal
from utils.format_number_color import format_number_color

def formatted_diff(value_as_is, value_to_be, option):
    return calculate_diff_pp(value_as_is, value_to_be) if option == "pp" else calculate_diff(value_as_is, value_to_be)

def Card(
        title,
        value_as_is=None,
        value_to_be=None,
        option="perc",
        position="left",
        children=None,
        show_decimal=True,
        icon=None
    ):
    """
    Componente de Card para exibir métricas com layout consistente
    """
    def format_value(value):
        if show_decimal:
            return format_number(value)
        return format_number(value).split('.')[0]

    # Calcula a variação
    diff = formatted_diff(value_as_is, value_to_be, option) if value_as_is is not None and value_to_be is not None else None
    diff_color = "#dc3545" if diff and float(diff) < 0 else "#198754"
    
    card_content = [
        # Título
        html.Div(
            [
                html.Span(icon) if icon else None,
                html.Span(title, style={"fontWeight": "500", "color": "#495057"}),
            ],
            style={"marginBottom": "8px"}
        ),
        # Valor principal
        html.Div(
            format_value(value_to_be) if value_to_be is not None else None,
            style={
                "fontSize": "1.25rem",
                "fontWeight": "600",
                "color": "#212529",
                "marginBottom": "4px"
            }
        ),
        # Baseline e variação
        html.Div([
            html.Span(
                f"Baseline: {format_value(value_as_is)}" if value_as_is is not None else "",
                style={"color": "#6c757d", "fontSize": "0.875rem"}
            ),
            html.Span(
                f" ({format_number_decimal(diff, option)})" if diff else "",
                style={
                    "color": diff_color,
                    "fontSize": "0.875rem",
                    "marginLeft": "8px",
                    "fontWeight": "500"
                }
            ) if diff is not None else None
        ])
    ]

    if children is not None:
        card_content.append(children)

    return dbc.Card(
        dbc.CardBody(card_content, className="p-3"),
        style={
            "height": "100%",
            "border": "1px solid #dee2e6",
            "borderRadius": "6px",
            "backgroundColor": "white",
        }
    )
