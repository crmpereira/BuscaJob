# BuscaJob – Modo Somente API

API Flask para coleta e consolidação de vagas de emprego (sem frontend). Inclui endpoints para relatório fixo, busca por critérios, último resultado e health check. Oferece automação via PowerShell e um CLI opcional.

## Quickstart (GitHub)
- Clonar: `git clone https://github.com/crmpereira/BuscaJob.git`
- Entrar: `cd BuscaJob`
- Venv: `python -m venv .venv`
- Dependências: `.\.venv\Scripts\pip.exe install -r requirements.txt`
- Rodar servidor: `.\.venv\Scripts\python.exe api_server.py` (opcional)

## Endpoints
- `/` – Status da API e lista de endpoints
- `/api/health` – Verificação de saúde (`{"status":"ok"}`)
- `/api/relatorio-fixo` – Gera e salva `relatorio_fixo_YYYYMMDD_HHMMSS.json`
- `/api/ultimo-resultado` – Retorna conteúdo do `resultados_*.json` mais recente
- `/api/buscar-vagas` (POST) – Busca vagas por critérios JSON

## Script PowerShell (sem servidor)
- Arquivo: `run_relatorio.ps1`
- Uso: `powershell -ExecutionPolicy Bypass -File .\run_relatorio.ps1`
- Com email: `powershell -ExecutionPolicy Bypass -File .\run_relatorio.ps1 -EnviarEmail`
- Observação: usa Flask test client, imprime `Arquivo` e `Total de vagas`.

## CLI (opcional)
- Arquivo: `cli_buscajob.py`
- Base URL: `BUSCAJOB_URL` (default `http://localhost:5000`)
- Último resultado:
  - `python cli_buscajob.py --ultimo`
  - JSON bruto: `python cli_buscajob.py --ultimo --json`
- Busca por critérios:
  - `python cli_buscajob.py --cargo "Desenvolvedor" --localizacao "Joinville" --sites linkedin,indeed --tipos CLT --abrir primeiro`

## Requisitos e variáveis
- Python 3.10+
- `SMTP_HOST`, `SMTP_PORT`, `SMTP_USER`, `SMTP_PASS`, `EMAIL_FROM`, `EMAIL_TO` (opcional)
- Ativar envio automático: `EMAIL_ENABLED=true`

## Saídas geradas
- `/api/relatorio-fixo` -> `relatorio_fixo_YYYYMMDD_HHMMSS.json`
- `/api/buscar-vagas` -> `resultados_YYYYMMDD_HHMMSS.json`

## Organização do repo
- Frontend removido; `.gitignore` ignora arquivos gerados (`relatorio_fixo_*`, `resultados_*`, `vagas_buscajob_*`, `estatisticas.json`, `vagas_salvas.json`, `configuracoes.json`).
- Dependências enxutas em `requirements.txt` (removido `selenium` e `python-dotenv`).