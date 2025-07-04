# Pricing Dash App

#### Visão Geral
Dashboard para arquitetura de preços, alteração de parâmetros, workflow de aprovação e configurações

#### Principais tecnologias
- Python
- Pandas
- Dash
- Dash Bootstrap Components (para estilo e layout)

#### Principais Funcionalidades

1. **Arquitetura de Preços**
   - Visualização e análise de estruturas de preços
   - Simulação de cenários de precificação
   - Análise comparativa de preços

2. **Gestão de Parâmetros**
   - Configuração de parâmetros de precificação
   - Ajuste de variáveis e métricas
   - Histórico de alterações de parâmetros

3. **Análise e Relatórios**
   - Geração de relatórios customizados
   - Dashboards interativos
   - Exportação de dados em diferentes formatos

4. **Workflow de Aprovação**
   - Sistema de aprovação em múltiplos níveis
   - Rastreamento de status de aprovações
   - Notificações de alterações e aprovações pendentes

5. **Configurações do Sistema**
   - Gerenciamento de usuários e permissões
   - Configurações de integração
   - Personalização de interface

#### Recursos Técnicos
- Interface responsiva e moderna
- Integração com APIs externas
- Cache de dados para melhor performance
- Sistema de logs para auditoria
- Backup automático de configurações

#### Instalação

Clonar o repositório

Criar um ambiente virtual (opcional mas recomendado)
`python -m venv .venv`

Ativar o ambiente virtual
`.venv\Scripts\activate`

##### Instalar as dependências

`pip install -r requirements.txt`

##### Crie o arquivo .env (secrets)
Crie um arquivo com nome .env na raiz do projeto e adicione os secrets, conforme o arquivo de exemplo .env-example.

#### Como rodar a aplicação

`python app.py`

Ao rodar esse comando a aplicação deve abrir por padrão em: http://127.0.0.1:8050/.

#### Estrutura de pastas

- **api/**: chamadas para API
- **assets/** */: estilos, imagens e ícones
- **components/**: componentes da aplicação
- **locales/**: arquivos utilizados de tradução
- **pages/**: páginas da aplicação
- **static_data/**: dados estáticos
- **utils/**: funções abstraídas para reutilização
- **.env-example**: exemplo de arquivo .env (secrets) da aplicação
- **.gitignore**: especifica quais arquivos ou pastas serão ignorados pelo Git
- **app.py**: arquivo principal para rodar a aplicação
- **README.md**: instruções e informações sobre o projeto
- **requirements.txt**: dependências para instalação
- **styles.py**: arquivo de estilos
- **translations.py**: código para tradução