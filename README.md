# BuscaJob

Aplicação para buscar e listar vagas com um backend em Python e um frontend em React (Vite + Tailwind).

## Visão Geral
- Backend expõe endpoints de busca e resultados (`/api/buscar-vagas`, `/api/ultimo-resultado`, `/api/sites`, `/api/salvar-configuracao`, `/api/configuracoes`).
- Frontend fornece formulário de filtros e lista de vagas com abertura do link da vaga.

## Requisitos
- Node.js 18+ e npm
- Python 3.10+
- Git

## Configuração
1. Na raiz do projeto, defina a URL do backend no arquivo `BuscaJobFrontEnd/.env` (opcional, padrão `http://localhost:5000`):
   
   ```env
   VITE_API_URL=http://localhost:5000
   ```

## Executando o Backend
1. Criar e ativar ambiente virtual (Windows PowerShell):
   
   ```powershell
   python -m venv .venv
   .\.venv\Scripts\Activate.ps1
   ```

2. Instalar dependências e iniciar a API:
   
   ```powershell
   pip install -r BuscaJobBackEnd/requirements.txt
   python BuscaJobBackEnd/api_server.py
   ```

## Executando o Frontend
1. Instalar dependências:
   
   ```powershell
   cd BuscaJobFrontEnd
   npm install
   ```

2. Rodar o servidor de desenvolvimento:
   
   ```powershell
   npm run dev
   ```

## Funcionalidades principais
- Filtros agrupados em card com borda e sombra.
- Checkboxes para `Cargo`, `Localização` e `Sites` com opção **Todos** como primeiro item de cada grupo.
- Remoção dos botões "Limpar"; a limpeza é feita desmarcando **Todos**.
- Área de `Sites` com rolagem e tipografia reduzida.
- Botão **Buscar** alinhado à direita.
- Botão **Abrir Vaga** agora utiliza link direto quando a URL é válida e normaliza casos sem protocolo (ex.: `www.exemplo.com`, `http//exemplo.com`).

## Imagens em funcionamento

![Home](https://raw.githubusercontent.com/crmpereira/BuscaJob/main/docs/screenshots/01-home.svg)

![Filtros](https://raw.githubusercontent.com/crmpereira/BuscaJob/main/docs/screenshots/02-filtros.svg)

![Abrir Vaga](https://raw.githubusercontent.com/crmpereira/BuscaJob/main/docs/screenshots/03-abrir-vaga.svg)

## Testes manuais de "Abrir Vaga"
- Vaga com URL válida (`https://exemplo.com/vaga`): abre em nova aba.
- Vaga com URL sem protocolo (`www.exemplo.com/vaga`): normaliza para `https://` e abre.
- Vaga com URL inválida/vazia: botão desabilitado com título "Link indisponível".

## Estrutura
```
BuscaJob/
├── BuscaJobBackEnd/
│   ├── api_server.py
│   ├── job_scraper.py
│   ├── requirements.txt
│   └── ...
└── BuscaJobFrontEnd/
    ├── src/
    │   ├── App.tsx
    │   ├── api/
    │   └── components/
    ├── package.json
    └── ...
```

## Versionamento
- Branch principal: `main`
- Remoto: `origin`

Passos típicos para commitar e enviar alterações:

```powershell
git add -A
git commit -m "feat(frontend): filtros com checkbox 'Todos'; fix: Abrir Vaga; docs: README"
git push origin main
```

---

Observações:
- O backend persiste configurações em `configuracoes.json` e exporta resultados em arquivos `resultados_*.json`.
- Ajustes adicionais podem incluir seleção única por rádio, bloqueio de submit sem seleção e opções dinâmicas do backend.
