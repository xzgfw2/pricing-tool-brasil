from dash import html
from translations import _

"""
Dicionário que armazena os textos de ajuda exibidos em cada tela da aplicação.

Cada chave representa uma funcionalidade específica da interface, e o valor associado 
é o texto de ajuda a ser exibido para orientar o usuário sobre a funcionalidade da tela.

Variáveis:
    helper_text (dict): Dicionário com as chaves representando os nomes das telas e os valores
    como strings com os textos explicativos.

"""

approval_helper_text = {
    "title": _("Ajuda - Aprovações"), 
    "description": html.Div([
        html.P(_("Workflow de aprovações")),
        html.P(_("Clique na aba para visualizar os registros pendentes de aprovação.")),
        html.P(_("Clique nos botões para aceitar ou recusar a aprovação.")),
    ])
}

approvals_requests_helper_text = {
    "title": _("Ajuda - Requisições de Aprovação"),
    "description": html.Div([
        html.P(_("Permite visualizar o status das requisições de aprovação.")),
    ]),
}

buildup_helper_text = {
    "title": _("Ajuda - Buildup"),
    "description": html.Div([
        html.P(_("Permite visualizar e editar os fatores de buildup")),
        html.P(_("Permite calcular o buildup por base price e custo médio.")),
        html.P(_("Permite enviar as alterações realizadas para a aprovação do gestor.")),
    ]),
}

captain_helper_text = {
    "title": _("Ajuda - Capitão"),
    "description": html.Div([
        html.P(_("Permite visualizar e editar as variáveis de parametrização do capitão.")),
        html.P(_("Permite visualizar a lista de produtos com os respectivos capitães atuais.")),
        html.P(_("Use o botão de simulação para gerar uma lista com os capitães sugeridos pelo sistema, de acordo com as variáveis de parametrização.")),
    ]),
}

captain_simulation_helper_text = {
    "title": _("Ajuda - Simulação do Capitão"),
    "description": html.Div([
        html.P(_("Permite visualizar e editar o capitão sugerido pelo algoritmo de simulação.")),
        html.P(_("A lista apresentada permite visualizar o capitão atual, o capitão sugerido pelo algoritmo e realizar ações como aprovar, recusar ou manter o capitão atual.")),
        html.P(_("Permite enviar a simulação para a aprovação do gestor.")),
        html.Hr(),
        html.P(_("Sistema de mudança de capitão")),
        html.P(_("Por padrão ao efetuar a simulação o campo 'Aprovar Mudança?' vem preenchido com 'Aceitar'")),
        html.P(_("Abaixo o significado de cada uma das categorias do campo 'Aprovar Mudança?':")),
        html.Ul([
            html.Li(_("Aceitar: Aceita o novo capitão sugerido pelo sistema.")),
            html.Li(_("Anterior: Mantém o capitão anterior, recusando o novo capitão sugerido pelo sistema.")),
            html.Li(_("Recusar: Recusa a sugestão do sistema e o capitão anterior, sendo necessário informar um novo capitão na coluna 'Capitão (novo)'")),
        ]),
    ]),
}

captain_margin_helper_text = {
    "title": _("Ajuda - Margem do Capitão"),
    "description": html.Div([
        html.P(_("Permite visualizar e editar as variáveis de parametrização da margem do capitão com uma margem mínima e máxima")),
        html.P(_("Permite enviar as alterações realizadas para a aprovação do gestor.")),
    ]),
}

catlote_helper_text = {
    "title": _("Ajuda - Catlote Desconto"),
    "description": html.Div([
        html.P(_("Permite a parametrização dos descontos de cada catlote")),
        html.P(_("Clique no checkbox para selecionar os catlotes que deseja simular. Essa ação também configura automaticamente a data inicial e final em 30 dias, sendo possível editar essas datas.")),
        html.P(_("Após selecionar os catlotes, o botão de simulação será habilitado, permitindo o acesso à página de simulação de impactos.")),
        html.P(_("Colunas editáveis:")),
        html.Ul([
            html.Li(_("Data Inicial")),
            html.Li(_("Data Final")),
            html.Li(_("Quantidade")),
            html.Li(_("Participação % (Estim.)")),
        ]),
    ]),
}

catlote_simulation_helper_text = {
    "title": _("Ajuda - Simulação de Catlote"),
    "description": html.Div([
        html.P(_("Permite visualizar e editar os resultados estimados das principais métricas de receita, com e sem a campanha de desconto.")),
        html.P(_("Permite enviar as alterações realizadas para a aprovação do gestor.")),
    ]),
}

command_center_helper_text = {
    "title": _("Ajuda - Command Center"),
    "description": html.Div([
        html.P(_("Análises diversas para identificação de inconsistências, erros, pontos de atenção e oportunidades.")),
        html.P(_("Cada card mostra a quantidade de registros identificados para cada análise.")),
        html.P(_("Ao clicar no card, é exibido o detalhamento dos registros.")),
    ]),
}

delta_helper_text = {
    "title": _("Ajuda - Delta Preço"),
    "description": html.Div([
        html.P(_("Permite visualizar e editar o delta preço por CPC 136")),
        html.P(_("Permite enviar as alterações realizadas para a aprovação do gestor.")),
    ]),
}

marketing_helper_text = {
    "title": _("Ajuda - Posicionamento de Mercado"),
    "description": html.Div([
        html.P(_("Permite visualizar e editar o posicionamento de mercado por CPC 136")),
        html.P(_("Permite enviar as alterações realizadas para a aprovação do gestor.")),
    ]),
}

price_helper_text = {
    "title": _("Ajuda - Arquitetura de Preços"),
    "description": html.Div([
        html.P(_("Permite visualizar e editar as variáveis que definem o preço de cada peça.")),
        html.P(_("Permite simular os resultados das alterações nas variáveis.")),
    ]),
}

price_simulation_helper_text = {
    "title": _("Ajuda - Simulação de Preços"),
    "description": html.Div([
        html.P(_("Permite visualizar os resultados estimados da arquitetura de preços nas principais métricas de receita por peça.")),
        html.P(_("Permite enviar a simulação para a aprovação do gestor.")),
    ]),
}

optimization_helper_text = {
    "title": _("Ajuda - Otimização de Preços"),
    "description": html.Div([
        html.P(_("Permite visualizar e editar o preço de cada peça e avaliar os impactos nas principais métricas de receita")),
        html.P(_("Permite enviar as alterações realizadas para a aprovação do gestor.")),
    ]),
}

strategy_helper_text = {
    "title": _("Ajuda - Estratégia Comercial"),
    "description": html.Div([
        html.P(_("Permite visualizar e editar a estratégia comercial por CPC 136")),
        html.P(_("Permite enviar as alterações realizadas para a aprovação do gestor.")),
    ]),
}

helper_text = {
    "approval": approval_helper_text,
    "approvals_requests": approvals_requests_helper_text,
    "buildup": buildup_helper_text,
    "catlote": catlote_helper_text,
    "catlote_simulation": catlote_simulation_helper_text,
    "captain": captain_helper_text,
    "captain_margin": captain_margin_helper_text,
    "captain_simulation": captain_simulation_helper_text,
    "command_center": command_center_helper_text,
    "delta": delta_helper_text,
    "marketing": marketing_helper_text,
    "price": price_helper_text,
    "price_simulation": price_simulation_helper_text,
    "optimization": optimization_helper_text,
    "strategy": strategy_helper_text,
}
