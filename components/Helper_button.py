from dash import html
import dash_bootstrap_components as dbc

def create_help_button(
    id,
    tooltip_text="Informações sobre a página",
):
    """
    Cria um componente de botão de ajuda com um ícone e um tooltip.

    Este componente retorna um ícone clicável (representado por uma imagem SVG)
    e um tooltip (balão de informação) que exibe um texto quando o ícone é
    apontado pelo cursor. Ideal para fornecer dicas ou informações adicionais
    sobre elementos na página.

    Parâmetros
    ----------
    id : str
        ID único para o componente de imagem (`html.Img`), que também será o alvo
        do tooltip (`dbc.Tooltip`). Esse ID é necessário para que o tooltip
        possa ser vinculado corretamente ao ícone.
    tooltip_text : str, opcional
        Texto a ser exibido dentro do tooltip. Por padrão, é "Informações sobre a página".
    
    Retorna
    -------
    list
        Uma lista contendo dois elementos:
        - `html.Img`: Imagem que representa o ícone de ajuda, configurada para
        ser clicável e exibir um cursor de ponteiro.
        - `dbc.Tooltip`: Tooltip associado ao ícone de ajuda, exibindo o texto
        fornecido em `tooltip_text` quando o ícone é apontado.

    Exemplos
    --------
    Uso dentro de um layout Dash:
    
    ```python
    app.layout = html.Div(
        HelpButton(id="help_button", tooltip_text="Clique para mais informações"),
    )
    ```

    """
    
    return html.Div([
        html.Img(
            id=id,
            src="./assets/icons/help.svg",
            style={
                "cursor": "pointer",
                "width": "32px",
            }
        ),
        dbc.Tooltip(
            tooltip_text,
            target=id,
            placement="top",
        ),
    ])
