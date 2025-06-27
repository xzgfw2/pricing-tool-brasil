from dash import html

def handle_no_data_to_show(message="Nenhum dado retornado pela API, por favor verificar com o suporte técnico"):
    """
    Cria um componente para exibir uma mensagem quando não há dados para mostrar.

    Args:
        message (str): Mensagem a ser exibida quando não há dados. O valor padrão é
                      "Nenhum dado retornado pela API, por favor verificar com o suporte técnico".
    
    Returns:
        dash.html.P: Um componente Dash contendo a mensagem formatada.
    
    Example:
        >>> handle_no_data_to_show("Nenhum dado encontrado para este filtro")
        html.P("Nenhum dado encontrado para este filtro", className="no-content-message")
    """
    return html.P(message, className="no-content-message")
