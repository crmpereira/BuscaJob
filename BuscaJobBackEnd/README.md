# BuscaJob - Backend

Este diretório contém o código fonte do backend da aplicação BuscaJob.

## 📋 Sobre

O backend é construído em Python utilizando Flask e é responsável por:
- Realizar o scraping de vagas em diversos sites.
- Expor uma API REST para o frontend.
- Gerenciar tarefas agendadas e envio de e-mails.
- Processar e exportar dados.

## 🚀 Como Executar

Consulte o [README principal](../README.md) na raiz do projeto para instruções detalhadas de instalação e execução.

## 🔧 Desenvolvimento

### Estrutura de Arquivos
- `api_server.py`: Servidor Flask principal.
- `job_scraper.py`: Lógica de extração de dados.
- `run_relatorio.ps1`: Script PowerShell para execução de relatórios via CLI.

### Dependências
As dependências estão listadas em `requirements.txt`.

```bash
pip install -r requirements.txt
```
