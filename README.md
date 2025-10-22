# BuscaJob – Modo Somente API

Este projeto fornece uma API Flask para coleta e consolidação de vagas de emprego, sem frontend HTML. As rotas expõem operações de geração de relatório fixo, consulta ao último resultado, busca por critérios e verificação de saúde.

## Endpoints

- `/` – Status informativo da API e lista de endpoints
- `/api/health` – Verificação de saúde simples (`{"status":"ok"}`)
- `/api/relatorio-fixo` – Gera relatório fixo consolidado e salva em arquivo `relatorio_fixo_YYYYMMDD_HHMMSS.json`
- `/api/ultimo-resultado` – Retorna o conteúdo do arquivo `resultados_*.json` mais recente
- `/api/buscar-vagas` (POST) – Busca de vagas por critérios enviados em JSON

## Requisitos

- Python 3.10+
- Windows (testado) ou outro SO compatível

## Setup

1. Criar venv e instalar dependências:
   - `python -m venv .venv`
   - `.\.venv\Scripts\pip.exe install -r requirements.txt`

2. Variáveis de ambiente para envio de email (opcional):
   - `SMTP_HOST`, `SMTP_PORT`, `SMTP_USER`, `SMTP_PASS`, `EMAIL_FROM`, `EMAIL_TO`
   - Para ativar o envio automático no endpoint `/api/relatorio-fixo`, defina `EMAIL_ENABLED=true`.

## Executar servidor (opcional)

- `.\.venv\Scripts\python.exe api_server.py`
- A API fica acessível em `http://localhost:5000`.

Observação: para automação, você pode acionar o relatório sem subir o servidor HTTP usando o cliente de teste do Flask via o script PowerShell abaixo.

## Script PowerShell – Acionar relatório

- Arquivo: `run_relatorio.ps1`
- Uso básico:
  - `powershell -ExecutionPolicy Bypass -File .\run_relatorio.ps1`
  - Com envio de email: `powershell -ExecutionPolicy Bypass -File .\run_relatorio.ps1 -EnviarEmail`

O script:
- Cria um script Python temporário que importa `api_server` e chama `/api/relatorio-fixo` via `Flask test client` (não precisa do servidor HTTP rodando).
- Imprime um resumo com `Arquivo` e `Total de vagas`.
- Respeita `EMAIL_ENABLED` conforme o parâmetro `-EnviarEmail`.

## Exemplos de uso da API

- Health check (sem iniciar servidor usando test client):
  - `.\.venv\Scripts\python.exe -c "from api_server import app; c=app.test_client(); import sys; r=c.get('/api/health'); print(r.get_data(as_text=True))"`

- Buscar vagas (quando servidor está rodando):
  - `Invoke-RestMethod -Method Post -Uri http://localhost:5000/api/buscar-vagas -ContentType 'application/json' -Body '{"cargo":"Analista de Sistemas","localizacao":"Joinville","sites":["linkedin","indeed"],"tipos_contratacao":["CLT","PJ"]}'`

## Saída gerada

- `/api/relatorio-fixo` salva `relatorio_fixo_YYYYMMDD_HHMMSS.json` na raiz do projeto.
- `/api/buscar-vagas` salva `resultados_YYYYMMDD_HHMMSS.json`.

## Notas

- O projeto está configurado para modo somente API; arquivos de frontend (`index.html`, `script.js`, `styles.css`) foram removidos.
- Há um agendador que roda em thread daemon ao importar `api_server` (horários em `09:00` e `18:00`) para execução automática se configurado.