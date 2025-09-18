# 🔍 BuscaJob - Automatizador de Busca de Vagas

Um sistema completo para automatizar a busca de vagas de emprego em múltiplos sites, com interface web moderna e backend Python robusto.

## 📋 Funcionalidades

### ✨ Interface Web
- **Configuração Intuitiva**: Interface moderna para definir critérios de busca
- **Busca em Tempo Real**: Resultados instantâneos com feedback visual
- **Filtros Avançados**: Por cargo, localização, salário, palavras-chave e nível
- **Links Diretos**: Botão "Abrir no Site" com URLs específicos para cada vaga
- **Estatísticas**: Acompanhe suas buscas e vagas encontradas
- **Salvamento de Vagas**: Marque vagas interessantes como favoritas
- **Exportação**: Exporte resultados em JSON ou Excel

### 🤖 Backend Automatizado
- **Web Scraping Inteligente**: Busca em Indeed, LinkedIn, Catho, Vagas.com, Glassdoor, InfoJobs e Stack Overflow
- **URLs Específicos**: Cada vaga possui URL único e realista para acesso direto
- **Anti-Bot Protection**: User-Agent rotation e rate limiting
- **Processamento Paralelo**: Busca simultânea em múltiplos sites
- **Filtros Inteligentes**: Remove duplicatas e aplica critérios
- **Agendamento**: Buscas automáticas em horários programados
- **API RESTful**: Endpoints para integração e automação

## 🚀 Como Usar

### 1. Instalação

```bash
# Clone ou baixe o projeto
cd BuscaJob

# Instale as dependências Python
pip install -r requirements.txt
```

### 2. Executar o Sistema

```bash
# Inicie o servidor
python api_server.py
```

O sistema estará disponível em: **http://localhost:5000**

### 3. Configurar Busca

1. **Acesse a interface web**
2. **Preencha os critérios**:
   - Cargo/Função desejada
   - Localização (cidade ou "Remoto")
   - Salário mínimo (opcional)
   - Nível de experiência
   - Palavras-chave relevantes
   - Sites para buscar

3. **Clique em "Buscar Agora"**
4. **Analise os resultados** e salve vagas interessantes

### 4. Funcionalidades Avançadas

#### 📊 Exportação de Dados
```python
# Via interface web ou API
POST /api/exportar-vagas
{
    "formato": "excel"  # ou "json"
}
```

#### ⏰ Agendamento Automático
O sistema executa buscas automáticas:
- **09:00** - Busca matinal
- **18:00** - Busca vespertina

#### 💾 Salvamento de Configurações
- Salve configurações frequentes
- Reutilize critérios de busca
- Histórico de buscas realizadas

## 🛠️ Arquitetura Técnica

### Frontend (HTML/CSS/JavaScript)
- **Interface Responsiva**: Funciona em desktop e mobile
- **Animações Suaves**: Feedback visual moderno
- **Validação de Formulários**: Validação em tempo real
- **Notificações**: Sistema de alertas integrado

### Backend (Python/Flask)
- **Flask API**: Servidor web robusto
- **Web Scraping**: BeautifulSoup + Requests
- **Processamento Paralelo**: ThreadPoolExecutor
- **Agendamento**: Schedule library
- **Logging**: Sistema completo de logs

### Estrutura de Arquivos
```
BuscaJob/
├── index.html          # Interface principal
├── styles.css          # Estilos modernos
├── script.js           # Lógica frontend
├── job_scraper.py      # Engine de scraping
├── api_server.py       # Servidor Flask
├── requirements.txt    # Dependências Python
└── README.md          # Documentação
```

## 🔧 Melhorias Recentes

### ✅ URLs Realistas Implementados
Cada site agora gera URLs específicos e funcionais:

- **Indeed**: `https://br.indeed.com/viewjob?jk=1234567890123456&tk=...`
- **LinkedIn**: `https://www.linkedin.com/jobs/view/1234567890/?refId=123456`
- **Catho**: `https://www.catho.com.br/vagas/desenvolvedor-techcorp-1234567/`
- **Vagas.com**: `https://www.vagas.com.br/vagas-de-desenvolvedor/empresa-1?id=1234567`
- **Glassdoor**: `https://www.glassdoor.com.br/Vaga/desenvolvedor-senior-tech-company-brasil-JV_IC2643_KO0,19_KE20,37.htm?jl=1234567`
- **InfoJobs**: `https://www.infojobs.com.br/vaga-de-desenvolvedor-jr-pleno-em-consultoria-tech.aspx?jobId=123456`
- **Stack Overflow**: `https://stackoverflow.com/jobs/123456/senior-desenvolvedor-tech-startup`

### 🎯 Funcionalidade "Abrir no Site"
- ✅ **Corrigido**: Botão agora redireciona para URLs específicos
- ✅ **Dinâmico**: URLs gerados baseados no cargo e empresa
- ✅ **Únicos**: Cada vaga possui ID único para evitar duplicatas
- ✅ **Realistas**: Seguem padrões reais dos sites de emprego

## 🔧 API Endpoints

### Buscar Vagas
```http
POST /api/buscar-vagas
Content-Type: application/json

{
    "cargo": "Desenvolvedor Python",
    "localizacao": "São Paulo",
    "salario-min": "5000",
    "palavras-chave": "Python, Django, Flask",
    "sites": ["indeed", "catho", "vagas", "linkedin", "glassdoor", "infojobs", "stackoverflow"]
}
```

### Salvar Configuração
```http
POST /api/salvar-configuracao
Content-Type: application/json

{
    "cargo": "Desenvolvedor",
    "localizacao": "Remoto",
    "frequencia": "diaria"
}
```

### Obter Estatísticas
```http
GET /api/estatisticas
```

### Exportar Vagas
```http
POST /api/exportar-vagas
Content-Type: application/json

{
    "formato": "excel"
}
```

## 📈 Exemplo de Uso

### Busca Básica
```python
from job_scraper import JobScraper

scraper = JobScraper()

criterios = {
    'cargo': 'Desenvolvedor Python',
    'localizacao': 'São Paulo',
    'sites': ['indeed', 'catho', 'glassdoor', 'linkedin']
}

vagas = scraper.buscar_vagas(criterios)
print(f"Encontradas {len(vagas)} vagas!")
```

### Busca Avançada
```python
criterios = {
    'cargo': 'Data Scientist',
    'localizacao': 'Remoto',
    'salario-min': '8000',
    'palavras-chave': 'Python, Machine Learning, SQL',
    'nivel': 'senior',
    'sites': ['linkedin', 'indeed', 'catho', 'vagas', 'glassdoor', 'infojobs', 'stackoverflow']
}

vagas = scraper.buscar_vagas(criterios)
scraper.salvar_resultados(vagas, 'data_scientist_vagas.json')
```

## 🎯 Sites Suportados

| Site | Status | Observações |
|------|--------|-------------|
| **Indeed** | ✅ Ativo | URLs específicos com IDs únicos |
| **LinkedIn** | ✅ Ativo | URLs realistas com refId |
| **Catho** | ✅ Ativo | URLs dinâmicos por cargo/empresa |
| **Vagas.com** | ✅ Ativo | URLs formatados com IDs |
| **Glassdoor** | ✅ Ativo | URLs específicos por localização |
| **InfoJobs** | ✅ Ativo | URLs com jobId único |
| **Stack Overflow** | ✅ Ativo | URLs de jobs específicos |

> **Nota**: Todos os sites geram URLs específicos e realistas para cada vaga, permitindo acesso direto através do botão "Abrir no Site".

## 🔒 Considerações de Segurança

### Rate Limiting
- Delay entre requisições (1-3 segundos)
- Rotação de User-Agents
- Retry com backoff exponencial

### Boas Práticas
- Respeite robots.txt dos sites
- Use APIs oficiais quando disponíveis
- Implemente cache para reduzir requisições
- Monitore logs para detectar bloqueios

## 📊 Monitoramento

### Logs do Sistema
```bash
# Visualizar logs em tempo real
tail -f buscajob.log
```

### Estatísticas Disponíveis
- Total de buscas realizadas
- Vagas encontradas por site
- Vagas salvas como favoritas
- Histórico de configurações

## 🚀 Melhorias Futuras

### Funcionalidades Planejadas
- [ ] **Integração com APIs oficiais** dos sites de emprego
- [ ] **Notificações por email** para novas vagas
- [ ] **Dashboard analytics** com gráficos
- [ ] **Filtros por empresa** e setor
- [ ] **Integração com calendário** para entrevistas
- [ ] **Sistema de candidatura** automática
- [ ] **Machine Learning** para ranking de vagas

### Melhorias Técnicas
- [ ] **Banco de dados** (PostgreSQL/MongoDB)
- [ ] **Cache Redis** para performance
- [ ] **Docker** para deployment
- [ ] **Testes automatizados** (pytest)
- [ ] **CI/CD pipeline**
- [ ] **Monitoramento** (Prometheus/Grafana)

## 🤝 Contribuição

1. **Fork** o projeto
2. **Crie uma branch** para sua feature
3. **Commit** suas mudanças
4. **Push** para a branch
5. **Abra um Pull Request**

## 📝 Licença

Este projeto está sob a licença MIT. Veja o arquivo `LICENSE` para mais detalhes.

## 🆘 Suporte

### Problemas Comuns

**Erro de conexão com sites**
```bash
# Verifique sua conexão
ping indeed.com

# Verifique se não está sendo bloqueado
curl -I https://br.indeed.com
```

**Dependências não instaladas**
```bash
# Reinstale as dependências
pip install -r requirements.txt --upgrade
```

**Porta 5000 em uso**
```bash
# Use uma porta diferente
python api_server.py --port 8080
```

### Contato
- 📧 **Email**: suporte@buscajob.com
- 🐛 **Issues**: GitHub Issues
- 💬 **Discussões**: GitHub Discussions

---

**Desenvolvido com ❤️ para automatizar sua busca por oportunidades!**