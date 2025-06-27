from dash import html
from translations import _

def handle_nothing_to_approve():
    """
    Cria um componente para exibir uma mensagem quando não há itens para aprovar.
    
    Este componente utiliza a classe CSS 'no-content-message' para estilização,
    que centraliza o texto e aplica o estilo adequado para mensagens de ausência
    de itens para aprovação.

    Returns:
        dash.html.Div: Um componente Dash contendo a mensagem formatada "Nada para aprovar".
    
    Example:
        >>> handle_nothing_to_approve()
        html.Div(_("Nada para aprovar"), className="no-content-message")
    """
    return html.Div(
        _("Nada para aprovar"),
        className="no-content-message",
    )
