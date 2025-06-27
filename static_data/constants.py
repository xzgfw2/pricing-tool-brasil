VARIABLES_QUARTER = [
    "Q1",
    "Q2",
    "Q3",
    "Q4",
]

# VARIABLES_YEAR = [str(year) for year in range(2100, 2019, -1)]

LIST_OF_ALLOWERD_ROLES_TO_ACCESS_APPROVAL = [
    "Gerente de Pricing", 
    "Gerente de Finanças"
]

LIST_OF_ALLOWERD_ROLES_TO_EDIT_AND_WHERE = {
    "Analista de Pricing": [], 
    "Gerente de Pricing": [],
    "Gerente de Finanças": [
        "buildup",
    ],
    "Analista de Marketing": [
        "catlote",
        "optimization",
        "captain",
        "strategy",
        "marketing",
    ],
}
