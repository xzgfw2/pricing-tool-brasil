import dash_bootstrap_components as dbc

def create_modal(
        modal_title,
        modal_id=None,
        modal_title_id=None,
        modal_body_id=None,
        modal_footer_id=None,
        modal_body=None,
        modal_footer=None,
        is_open=False,
        size=None,
    ):
    return dbc.Modal(
        id=modal_id,
        children=[
            dbc.ModalHeader(
                **({"id": modal_title_id} if modal_title_id else {}),
                children=modal_title,
            ),
            dbc.ModalBody(
                **({"id": modal_body_id} if modal_body_id else {}),
                children=modal_body,
            ),
            dbc.ModalFooter(
                **({"id": modal_footer_id} if modal_footer_id else {}),
                children=modal_footer,
            ),
        ],
        centered=True,
        is_open=is_open,
        **({"size": size} if size else {}),
    )
