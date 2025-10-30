# Changelog

## v1-api-only (2025-10-30)

Resumo
- Modo somente API consolidado; frontend removido
- CLI removido do repositório
- Dependências enxutas (remoção de `selenium` e `python-dotenv`); `openpyxl` mantido
- `.gitignore` cobre arquivos gerados (`relatorio_fixo_*`, `resultados_*`, `vagas_buscajob_*`, `estatisticas.json`, `vagas_salvas.json`, `configuracoes.json`)

Mudanças
- Remoção: `index.html`, `script.js`, `styles.css`, `cli_buscajob.py`
- Adição: `run_relatorio.ps1` (aciona `/api/relatorio-fixo` via Flask test client)
- Atualização: `README.md` com Quickstart GitHub, endpoints, script PowerShell e organização
- Atualização: `requirements.txt` sem `selenium` e `python-dotenv`

Endpoints
- `/` – status da API e lista de endpoints
- `/api/health` – verificação de saúde
- `/api/relatorio-fixo` – gera `relatorio_fixo_YYYYMMDD_HHMMSS.json`
- `/api/ultimo-resultado` – lê `resultados_*.json` mais recente
- `/api/buscar-vagas` (POST) – busca por critérios JSON

Notas
- Para rodar sem servidor: `run_relatorio.ps1` usa Flask test client
- Avisos de fim de linha (LF/CRLF) no Windows são esperados ao commitar