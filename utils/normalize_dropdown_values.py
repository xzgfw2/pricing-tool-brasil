# from variables_dropdown import VARIABLES_DROPDOWN

VARIABLES_DROPDOWN = [
    "Ano frota",
    "Aplicações",
    "Elasticidade",
    "Estoque",
    "Frota",
    "Marca",
    "Price index",
]

def normalize_dropdown_values(value):
    if value in VARIABLES_DROPDOWN:
        value = value.lower().replace('ç', 'c').replace('õ', 'o')
    return value
