from dash import html, dcc
from typing import Optional, Union

def create_upload_file(
    id: str,
    children: Optional[Union[str, html.Div]] = None,
    multiple: bool = False,
    className: Optional[str] = "upload-file"
) -> dcc.Upload:
    """
    Cria um componente de upload de arquivo com conteúdo padrão ou customizado.

    Args:
        id (str): ID do componente.
        children (str | html.Div, opcional): Conteúdo interno do componente. Se None, usa texto padrão.
        multiple (bool, opcional): Permite múltiplos arquivos. Default é False.
        className (str, opcional): Classe CSS para estilização. Default é "upload-file".

    Returns:
        dcc.Upload: Componente de upload configurado.
    """

    default_children = html.Div([
        "Arraste e solte ou selecione um arquivo"
    ])

    return dcc.Upload(
        id=id,
        children=children if children is not None else default_children,
        className=className,
        multiple=multiple
    )
