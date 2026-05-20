# APTUS — versão browser/PC com seletor PT/EN

Alteração aplicada apenas à versão Streamlit/browser.

## O que foi alterado

- Foi adicionado um seletor de idioma PT/EN no topo da página de login.
- Foi adicionado o mesmo seletor no cabeçalho das páginas autenticadas.
- A escolha do idioma fica guardada na sessão do Streamlit e também pode ser alterada via `?lang=PT` ou `?lang=EN`.
- A tradução é aplicada aos textos principais do login, navegação, filtros, dashboard e formulário de atividade.

## O que NÃO foi alterado

- Não mexe na app Android.
- Não altera Supabase.
- Não altera dados CSV.
- Não altera a lógica de login, permissões, modos ou dashboards.

## Como testar localmente

```bash
pip install -r requirements.txt
streamlit run app.py
```

Depois abre a aplicação e usa o seletor `🌐 PT/EN` no topo.

## Como atualizar a Streamlit Cloud

Substitui estes ficheiros no repositório GitHub e faz commit/push.
A app web atualiza automaticamente quando a Streamlit Cloud fizer redeploy.

## App PC instalada

Se a app PC instalada abre a versão online da Streamlit, esta alteração aparece automaticamente depois do redeploy.
Se a app PC tem ficheiros locais empacotados, é preciso gerar novamente o instalador com este `app.py` atualizado.
