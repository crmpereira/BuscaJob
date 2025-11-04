# BuscaJob – Modo Somente API

API Flask para coleta e consolidação de vagas de emprego (sem frontend). Inclui endpoints para relatório fixo, busca por critérios, último resultado e health check. Oferece automação via PowerShell.

## Quickstart (GitHub)
- Clonar: `git clone https://github.com/crmpereira/BuscaJob.git`
- Entrar: `cd BuscaJob`
- Venv: `python -m venv .venv`
- Dependências: `.\.venv\Scripts\pip.exe install -r BuscaJobBackEnd\requirements.txt`
- Rodar servidor: `.\.venv\Scripts\python.exe BuscaJobBackEnd\api_server.py` (opcional)

## Endpoints
- `/` – Status da API e lista de endpoints
- `/api/health` – Verificação de saúde (`{"status":"ok"}`)
- `/api/relatorio-fixo` – Gera e salva `relatorio_fixo_YYYYMMDD_HHMMSS.json`
- `/api/ultimo-resultado` – Retorna conteúdo do `resultados_*.json` mais recente
- `/api/buscar-vagas` (POST) – Busca vagas por critérios JSON

## Script PowerShell (sem servidor)
- Arquivo: `BuscaJobBackEnd\run_relatorio.ps1`
- Uso: `powershell -ExecutionPolicy Bypass -File .\BuscaJobBackEnd\run_relatorio.ps1`
- Com email: `powershell -ExecutionPolicy Bypass -File .\BuscaJobBackEnd\run_relatorio.ps1 -EnviarEmail`
- Observação: usa Flask test client, imprime `Arquivo` e `Total de vagas`.

## Requisitos e variáveis
- Python 3.10+
- `SMTP_HOST`, `SMTP_PORT`, `SMTP_USER`, `SMTP_PASS`, `EMAIL_FROM`, `EMAIL_TO` (opcional)
- Ativar envio automático: `EMAIL_ENABLED=true`

## Saídas geradas
- `/api/relatorio-fixo` -> `relatorio_fixo_YYYYMMDD_HHMMSS.json`
- `/api/buscar-vagas` -> `resultados_YYYYMMDD_HHMMSS.json`

## Organização do repo
- Backend em `BuscaJobBackEnd/` (API Flask e scripts). Frontend e CLI removidos.
- Dependências enxutas em `BuscaJobBackEnd/requirements.txt` (removido `selenium` e `python-dotenv`).