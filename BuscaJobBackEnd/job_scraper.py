#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
BuscaJob - Automatizador de Busca de Vagas de Emprego
Script principal para web scraping de sites de emprego
"""

import requests
from bs4 import BeautifulSoup
import json
import time
import random
from datetime import datetime, timedelta
import re
from urllib.parse import urljoin, quote_plus
import logging
import os
from dataclasses import dataclass, asdict
from typing import List, Dict, Optional
import concurrent.futures
from fake_useragent import UserAgent

# Diretório base do backend
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Configuração de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(os.path.join(BASE_DIR, 'buscajob.log')),
        logging.StreamHandler()
    ]
)

@dataclass
class Vaga:
    """Classe para representar uma vaga de emprego"""
    titulo: str
    empresa: str
    localizacao: str
    salario: str
    descricao: str
    data_publicacao: str
    site_origem: str
    url: str
    tipo_contrato: str = ""
    nivel_experiencia: str = ""
    palavras_chave: List[str] = None
    modalidade: str = ""
    
    def __post_init__(self):
        if self.palavras_chave is None:
            self.palavras_chave = []

class JobScraper:
    """Classe principal para scraping de vagas de emprego"""
    
    def __init__(self):
        self.ua = UserAgent()
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': self.ua.random,
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'pt-BR,pt;q=0.9,en;q=0.8',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
        })
        
        self.scrapers = {
            'indeed': self._scrape_indeed,
            'catho': self._scrape_catho,
            'vagas': self._scrape_vagas_com,
            'linkedin': self._scrape_linkedin,
            'glassdoor': self._scrape_glassdoor,
            'infojobs': self._scrape_infojobs,
            'stackoverflow': self._scrape_stackoverflow,
            'github': self._scrape_github,
            'trampos': self._scrape_trampos,
            'rocket': self._scrape_rocket,
            'startup': self._scrape_startup
        }

    def _gerar_descricao(self, cargo: str, empresa: str) -> str:
        """Gera uma descrição variada e curta para a vaga (mock)."""
        responsaveis = [
            f"Atuar como {cargo} em times ágeis",
            "Colaborar com produto e UX",
            "Desenvolver features escaláveis",
            "Escrever código limpo e testável",
            "Participar de code reviews",
        ]
        requisitos = [
            "Experiência com tecnologias modernas",
            "Conhecimento em APIs REST/GraphQL",
            "Boas práticas de versionamento (Git)",
            "Atenção a performance e segurança",
            "Boa comunicação e proatividade",
        ]
        beneficios = [
            "Plano de saúde",
            "Horário flexível",
            "Remoto híbrido",
            "Auxílio educação",
            "Day off no aniversário",
        ]
        # Escolhas aleatórias para variar a mensagem
        r1 = random.choice(responsaveis)
        r2 = random.choice(responsaveis)
        req = random.choice(requisitos)
        ben = random.choice(beneficios)
        # Evita duplicar exatamente a mesma frase
        if r2 == r1:
            r2 = random.choice([r for r in responsaveis if r != r1])
        return (
            f"Oportunidade como {cargo} na {empresa}. "
            f"{r1}. {r2}. {req}. Benefícios: {ben}."
        )
        
    def buscar_vagas(self, criterios: Dict) -> List[Vaga]:
        """
        Busca vagas baseado nos critérios fornecidos
        
        Args:
            criterios: Dicionário com critérios de busca
            
        Returns:
            Lista de vagas encontradas
        """
        logging.info(f"Iniciando busca com critérios: {criterios}")
        
        todas_vagas = []
        sites_selecionados = criterios.get('sites', ['indeed', 'catho'])
        
        # Executa scraping em paralelo para melhor performance
        with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executor:
            futures = {}
            
            for site in sites_selecionados:
                if site in self.scrapers:
                    future = executor.submit(self.scrapers[site], criterios)
                    futures[future] = site
            
            for future in concurrent.futures.as_completed(futures):
                site = futures[future]
                try:
                    vagas = future.result()
                    todas_vagas.extend(vagas)
                    logging.info(f"Encontradas {len(vagas)} vagas no {site}")
                except Exception as e:
                    logging.error(f"Erro ao buscar no {site}: {e}")
        
        # Remove duplicatas baseado no título e empresa
        vagas_unicas = self._remover_duplicatas(todas_vagas)

        # Normaliza URLs de vagas (corrige caminhos relativos e ausência de esquema)
        for v in vagas_unicas:
            try:
                v.url = self._normalize_url(getattr(v, 'url', ''), getattr(v, 'site_origem', ''))
            except Exception:
                pass

        # Infere modalidade quando não fornecida
        for v in vagas_unicas:
            if not getattr(v, 'modalidade', ''):
                v.modalidade = self._inferir_modalidade(v.titulo, v.descricao, v.localizacao)

        # Aplica filtros adicionais
        vagas_filtradas = self._aplicar_filtros(vagas_unicas, criterios)
        
        logging.info(f"Total de vagas encontradas: {len(vagas_filtradas)}")
        return vagas_filtradas
    
    def _scrape_indeed(self, criterios: Dict) -> List[Vaga]:
        """Scraping do Indeed (implementação simplificada para demonstração)"""
        vagas = []
        
        try:
            cargo = criterios.get('cargo', '')
            localizacao = criterios.get('localizacao', 'Brasil')
            
            # Implementação mock para demonstração
            empresas_mock = ['TechCorp', 'InnovaSoft', 'DataSolutions', 'CloudTech', 'DevCompany']
            localizacoes_mock = ['São Paulo, SP', 'Rio de Janeiro, RJ', 'Belo Horizonte, MG', 'Florianópolis, SC', 'Joinville, SC', 'Remoto']
            
            for i in range(random.randint(3, 8)):
                empresa = empresas_mock[i % len(empresas_mock)]
                # Link estável de busca no Indeed (evita IDs aleatórios que expiram)
                from urllib.parse import quote_plus
                q = quote_plus(f"{cargo} {empresa}")
                l = quote_plus(localizacao)
                vaga = Vaga(
                    titulo=f"{cargo} - {empresa}",
                    empresa=empresa,
                    localizacao=localizacoes_mock[i % len(localizacoes_mock)],
                    salario=f"R$ {random.randint(3000, 12000):,}".replace(',', '.'),
                    descricao=self._gerar_descricao(cargo, empresa),
                    data_publicacao=(datetime.now() - timedelta(days=random.randint(0, 7))).strftime('%d/%m/%Y'),
                    site_origem='Indeed',
                    url=f'https://br.indeed.com/jobs?q={q}&l={l}',
                    tipo_contrato='CLT'
                )
                vagas.append(vaga)
                
        except Exception as e:
            logging.error(f"Erro no scraping do Indeed: {e}")
        
        return vagas
    
    def _extrair_vaga_indeed(self, card) -> Optional[Vaga]:
        """Extrai dados de uma vaga do Indeed"""
        try:
            # Título
            titulo_elem = card.find('h2', class_='jobTitle') or card.find('a', {'data-jk': True})
            titulo = titulo_elem.get_text(strip=True) if titulo_elem else "Título não encontrado"
            
            # Empresa
            empresa_elem = card.find('span', class_='companyName') or card.find('a', class_='turnstileLink')
            empresa = empresa_elem.get_text(strip=True) if empresa_elem else "Empresa não informada"
            
            # Localização
            loc_elem = card.find('div', class_='companyLocation')
            localizacao = loc_elem.get_text(strip=True) if loc_elem else "Localização não informada"
            
            # Salário
            salary_elem = card.find('span', class_='salary-snippet') or card.find('div', class_='salary-snippet-container')
            salario = salary_elem.get_text(strip=True) if salary_elem else "Salário não informado"
            
            # Descrição
            desc_elem = card.find('div', class_='job-snippet') or card.find('ul')
            descricao = desc_elem.get_text(strip=True)[:200] + "..." if desc_elem else "Descrição não disponível"
            
            # Tentar extrair tipo de contratação da descrição
            tipo_contrato = ""
            descricao_upper = descricao.upper()
            if any(palavra in descricao_upper for palavra in ['CLT', 'CARTEIRA', 'EFETIVO']):
                tipo_contrato = "CLT"
            elif any(palavra in descricao_upper for palavra in ['PJ', 'PESSOA JURÍDICA', 'CNPJ']):
                tipo_contrato = "PJ"
            elif any(palavra in descricao_upper for palavra in ['ESTÁGIO', 'ESTAGIÁRIO', 'TRAINEE']):
                tipo_contrato = "Estágio"
            elif any(palavra in descricao_upper for palavra in ['FREELANCER', 'FREELA', 'AUTÔNOMO']):
                tipo_contrato = "Freelancer"
            elif any(palavra in descricao_upper for palavra in ['TEMPORÁRIO', 'TEMP']):
                tipo_contrato = "Temporário"
            elif any(palavra in descricao_upper for palavra in ['TERCEIRIZADO', 'OUTSOURCING']):
                tipo_contrato = "Terceirizado"
            
            # URL
            link_elem = card.find('a', {'data-jk': True}) or titulo_elem
            url = urljoin("https://br.indeed.com", link_elem.get('href', '')) if link_elem else ""
            
            return Vaga(
                titulo=titulo,
                empresa=empresa,
                localizacao=localizacao,
                salario=salario,
                descricao=descricao,
                data_publicacao=datetime.now().strftime('%d/%m/%Y'),
                site_origem='Indeed',
                url=url,
                tipo_contrato=tipo_contrato
            )
            
        except Exception as e:
            logging.warning(f"Erro ao extrair vaga: {e}")
            return None
    
    def _scrape_catho(self, criterios: Dict) -> List[Vaga]:
        """Scraping do Catho (implementação simplificada)"""
        vagas = []
        
        try:
            # Implementação simulada - em produção, usar seletores reais
            cargo = criterios.get('cargo', '')
            
            # Gera vagas mock para demonstração
            empresas_mock = ['TechCorp', 'InnovaSoft', 'DataSolutions', 'CloudTech']
            localizacoes_mock = ['São Paulo, SP', 'Rio de Janeiro, RJ', 'Florianópolis, SC', 'Joinville, SC', 'Remoto']
            
            for i in range(random.randint(3, 8)):
                empresa = empresas_mock[i % len(empresas_mock)]
                from urllib.parse import quote_plus
                q = quote_plus(f"{cargo} {empresa}")
                l = quote_plus(localizacoes_mock[i % len(localizacoes_mock)])
                vaga = Vaga(
                    titulo=f"{cargo} - {empresa}",
                    empresa=empresa,
                    localizacao=localizacoes_mock[i % len(localizacoes_mock)],
                    salario=f"R$ {random.randint(3000, 12000):,}".replace(',', '.'),
                    descricao=self._gerar_descricao(cargo, empresa),
                    data_publicacao=(datetime.now() - timedelta(days=random.randint(0, 7))).strftime('%d/%m/%Y'),
                    site_origem='Catho',
                    url=f'https://www.catho.com.br/vagas/?q={q}&where={l}',
                    tipo_contrato='CLT'
                )
                vagas.append(vaga)
                
        except Exception as e:
            logging.error(f"Erro no scraping do Catho: {e}")
        
        return vagas
    
    def _scrape_vagas_com(self, criterios: Dict) -> List[Vaga]:
        """Scraping do Vagas.com (implementação simplificada)"""
        vagas = []
        
        try:
            cargo = criterios.get('cargo', '')
            
            # Implementação mock
            for i in range(random.randint(2, 6)):
                from urllib.parse import quote_plus
                q = quote_plus(cargo)
                vaga = Vaga(
                    titulo=f"{cargo} Pleno/Sênior",
                    empresa=f"Empresa {i+1}",
                    localizacao="São Paulo, SP" if i % 2 == 0 else "Remoto",
                    salario=f"R$ {random.randint(4000, 15000):,}".replace(',', '.'),
                    descricao=f"Vaga para {cargo} com foco em desenvolvimento de soluções inovadoras.",
                    data_publicacao=(datetime.now() - timedelta(days=random.randint(0, 5))).strftime('%d/%m/%Y'),
                    site_origem='Vagas.com',
                    url=f'https://www.vagas.com.br/vagas-de-{cargo.lower().replace(" ", "-")}',
                    nivel_experiencia='Pleno'
                )
                vagas.append(vaga)
                
        except Exception as e:
            logging.error(f"Erro no scraping do Vagas.com: {e}")
        
        return vagas
    
    def _scrape_linkedin(self, criterios: Dict) -> List[Vaga]:
        """Scraping do LinkedIn (Vagas e Publicações)"""
        vagas = []
        
        try:
            cargo = criterios.get('cargo', '')
            local = criterios.get('localizacao', 'São Paulo')
            modalidades = criterios.get('modalidades', [])
            
            from urllib.parse import quote_plus

            # Empresas fictícias mais realistas
            empresas_tech = [
                'TechFlow Solutions', 'DataMinds Analytics', 'AgileSoft Systems', 
                'CloudNexus', 'DevStream', 'InovaTech Brasil', 'FutureStack',
                'CodeCrafters', 'ByteVision', 'NextLevel Digital'
            ]

            # Variações de títulos
            niveis = ['Júnior', 'Pleno', 'Sênior', 'Especialista', 'Tech Lead', '']
            complementos = ['Full Stack', 'Backend', 'Frontend', 'Mobile', 'Cloud', 'DevOps']

            # 1. Busca de Vagas (Jobs) - Mock aprimorado
            for i in range(random.randint(3, 8)):
                q = quote_plus(cargo)
                l = quote_plus(local)
                
                # Gera título mais realista
                nivel = random.choice(niveis)
                comp = ""
                if random.random() > 0.7:
                    comp = f" - {random.choice(complementos)}"
                
                titulo_vaga = f"{cargo} {nivel}{comp}".strip()
                empresa = random.choice(empresas_tech)
                
                # Gera descrição mais rica
                desc = self._gerar_descricao(cargo, empresa)

                vaga = Vaga(
                    titulo=titulo_vaga,
                    empresa=empresa,
                    localizacao="Híbrido" if i % 3 == 0 else local,
                    salario=f"R$ {random.randint(4000, 18000):,}".replace(',', '.'),
                    descricao=desc,
                    data_publicacao=(datetime.now() - timedelta(days=random.randint(0, 5))).strftime('%d/%m/%Y'),
                    site_origem='LinkedIn',
                    url=f'https://www.linkedin.com/jobs/search/?keywords={q}&location={l}',
                    tipo_contrato='CLT' if random.random() > 0.3 else 'PJ'
                )
                vagas.append(vaga)

            # 2. Busca em Publicações (Posts)
            # Formato de busca: "Cargo" AND "Modalidade" AND "Local"
            query_parts = []
            if cargo:
                query_parts.append(f'"{cargo}"')
            
            for mod in modalidades:
                if mod:
                    query_parts.append(f'"{mod}"')
                
            if local and local.lower() != 'remoto':
                query_parts.append(f'"{local}"')
                
            boolean_query = " AND ".join(query_parts)
            encoded_query = quote_plus(boolean_query)
            
            # Recrutadores fictícios
            recrutadores = [
                'Ana Silva (Tech Recruiter)', 'Carlos Mendes (HR Manager)', 
                'Juliana Costa (Talent Acquisition)', 'Roberto Santos (Headhunter)',
                'Mariana Oliveira (Recrutamento)'
            ]
            
            # Gera resultados simulados de posts
            for i in range(random.randint(2, 5)):
                recrutador = random.choice(recrutadores)
                
                # Títulos de posts parecem mais "chamadas"
                titulos_post = [
                    f"Estamos contratando: {cargo}",
                    f"Vaga aberta para {cargo}!",
                    f"Oportunidade de {cargo} na nossa equipe",
                    f"Procuramos {cargo} para início imediato",
                    f"Nova posição: {cargo}"
                ]
                
                titulo_post = random.choice(titulos_post)
                
                vaga_post = Vaga(
                    titulo=titulo_post,
                    empresa=recrutador, # Nos posts, quem posta é o "empresa" muitas vezes
                    localizacao=local,
                    salario="A combinar",
                    descricao=f"Olá rede! {titulo_post}. Estamos buscando profissionais com experiência em tecnologias modernas. Interessados enviem CV ou comentem 'Eu quero'. #vagas #{cargo.lower().replace(' ', '')} #emprego",
                    data_publicacao=datetime.now().strftime('%d/%m/%Y'),
                    site_origem='LinkedIn Posts',
                    url=f'https://www.linkedin.com/search/results/content/?keywords={encoded_query}&origin=GLOBAL_SEARCH_HEADER',
                    tipo_contrato='PJ' if i % 2 == 0 else 'CLT'
                )
                vagas.append(vaga_post)

                
        except Exception as e:
            logging.error(f"Erro no scraping do LinkedIn: {e}")
        
        return vagas
    
    def _fazer_requisicao(self, url: str, max_retries: int = 3) -> Optional[requests.Response]:
        """Faz requisição HTTP com retry e rate limiting"""
        for tentativa in range(max_retries):
            try:
                # Rate limiting
                time.sleep(random.uniform(1, 3))
                
                # Rotaciona User-Agent
                self.session.headers['User-Agent'] = self.ua.random
                
                response = self.session.get(url, timeout=10)
                response.raise_for_status()
                
                return response
                
            except requests.RequestException as e:
                logging.warning(f"Tentativa {tentativa + 1} falhou para {url}: {e}")
                if tentativa == max_retries - 1:
                    logging.error(f"Falha definitiva ao acessar {url}")
                    return None
                time.sleep(random.uniform(2, 5))
        
        return None
    
    def _remover_duplicatas(self, vagas: List[Vaga]) -> List[Vaga]:
        """Remove vagas duplicadas baseado em título e empresa"""
        vagas_unicas = []
        chaves_vistas = set()
        
        for vaga in vagas:
            chave = f"{vaga.titulo.lower()}_{vaga.empresa.lower()}"
            if chave not in chaves_vistas:
                chaves_vistas.add(chave)
                vagas_unicas.append(vaga)
        
        return vagas_unicas
    
    def _aplicar_filtros(self, vagas: List[Vaga], criterios: Dict) -> List[Vaga]:
        """Aplica filtros adicionais nas vagas"""
        vagas_filtradas = []
        
        for vaga in vagas:
            # Filtro por palavras-chave
            if criterios.get('palavras_chave'):
                palavras = criterios['palavras_chave'].lower().split()
                texto_vaga = f"{vaga.titulo} {vaga.descricao}".lower()
                if not any(palavra in texto_vaga for palavra in palavras):
                    continue

            # Filtro por localização
            if criterios.get('localizacao'):
                loc = criterios['localizacao'].strip().lower()
                texto_loc_vaga = (vaga.localizacao or '').lower()
                if loc == 'remoto':
                    if 'remoto' not in texto_loc_vaga:
                        continue
                else:
                    # Suporta múltiplas localidades separadas por vírgula, barra, ponto e vírgula ou pipe
                    tokens = [t.strip() for t in re.split(r'[;,/\\|]', loc) if t.strip()]
                    match = any(token in texto_loc_vaga for token in tokens)
                    if not match:
                        continue
            
            # Filtro por range salarial
            if criterios.get('salario_minimo') or criterios.get('salario_maximo'):
                salario_vaga = self._extrair_valor_salario(vaga.salario)
                if salario_vaga:
                    if criterios.get('salario_minimo') and salario_vaga < criterios['salario_minimo']:
                        continue
                    if criterios.get('salario_maximo') and salario_vaga > criterios['salario_maximo']:
                        continue
            
            # Filtro por tipo de contratação
            if criterios.get('tipos_contratacao'):
                tipo_vaga = vaga.tipo_contrato.upper()
                tipos_aceitos = [t.upper() for t in criterios['tipos_contratacao']]
                
                # Verificar se o tipo da vaga está nos tipos aceitos
                # ou se a descrição/título contém indicações do tipo
                tipo_encontrado = False
                
                if tipo_vaga in tipos_aceitos:
                    tipo_encontrado = True
                else:
                    # Buscar indicações na descrição e título
                    texto_busca = f"{vaga.titulo} {vaga.descricao}".upper()
                    
                    for tipo_aceito in tipos_aceitos:
                        if tipo_aceito == 'CLT' and any(palavra in texto_busca for palavra in ['CLT', 'CARTEIRA', 'EFETIVO', 'CONTRATO']):
                            tipo_encontrado = True
                            break
                        elif tipo_aceito == 'PJ' and any(palavra in texto_busca for palavra in ['PJ', 'PESSOA JURÍDICA', 'CNPJ', 'PRESTADOR']):
                            tipo_encontrado = True
                            break
                        elif tipo_aceito == 'ESTÁGIO' and any(palavra in texto_busca for palavra in ['ESTÁGIO', 'ESTAGIÁRIO', 'TRAINEE']):
                            tipo_encontrado = True
                            break
                        elif tipo_aceito == 'FREELANCER' and any(palavra in texto_busca for palavra in ['FREELANCER', 'FREELA', 'AUTÔNOMO', 'PROJETO']):
                            tipo_encontrado = True
                            break
                        elif tipo_aceito == 'TEMPORÁRIO' and any(palavra in texto_busca for palavra in ['TEMPORÁRIO', 'TEMP', 'SAZONAL']):
                            tipo_encontrado = True
                            break
                        elif tipo_aceito == 'TERCEIRIZADO' and any(palavra in texto_busca for palavra in ['TERCEIRIZADO', 'OUTSOURCING']):
                            tipo_encontrado = True
                            break
                
                if not tipo_encontrado:
                    continue

            # Filtro por modalidade (home office, presencial, híbrido)
            if criterios.get('modalidades'):
                mods_aceitas = [self._normalize_modalidade(m) for m in criterios['modalidades']]
                mod_vaga = self._normalize_modalidade(getattr(vaga, 'modalidade', ''))
                # Quando não é possível inferir, não filtra por modalidade
                if mod_vaga and mod_vaga not in mods_aceitas:
                    continue
            
            vagas_filtradas.append(vaga)
        
        return vagas_filtradas
    
    def _extrair_valor_salario(self, salario_str: str) -> float:
        """Extrai valor numérico do salário"""
        if not salario_str or salario_str.lower() in ['a combinar', 'não informado']:
            return 0.0
        
        # Remove caracteres não numéricos exceto vírgula e ponto
        numeros = re.findall(r'[\d.,]+', salario_str)
        if numeros:
            try:
                # Assume formato brasileiro (vírgula como decimal)
                valor_str = numeros[0].replace('.', '').replace(',', '.')
                return float(valor_str)
            except ValueError:
                return 0.0
        
        return 0.0

    def _normalize_url(self, url: Optional[str], site: Optional[str]) -> Optional[str]:
        """Normaliza URLs de vagas, resolvendo caminhos relativos e adicionando esquema quando necessário."""
        if not url:
            return None
        s = str(url).strip()
        if not s:
            return None

        site_key = (site or '').strip().lower()
        base_map = {
            'indeed': 'https://br.indeed.com',
            'catho': 'https://www.catho.com.br',
            'vagas': 'https://www.vagas.com.br',
            'vagas.com.br': 'https://www.vagas.com.br',
            'linkedin': 'https://www.linkedin.com',
            'glassdoor': 'https://www.glassdoor.com.br',
            'infojobs': 'https://www.infojobs.com.br',
            'stackoverflow': 'https://stackoverflow.com',
            'stack overflow jobs': 'https://stackoverflow.com',
            'github': 'https://github.com',
            'github jobs': 'https://github.com',
            'trampos': 'https://trampos.co',
            'trampos.co': 'https://trampos.co',
            'rocket': 'https://rocketjobs.com.br',
            'rocket jobs': 'https://rocketjobs.com.br',
            'startup': 'https://startupjobs.com',
            'startup jobs': 'https://startupjobs.com',
        }
        base = base_map.get(site_key)

        # Corrige protocolo sem dois-pontos (ex.: "https//")
        if s.lower().startswith('http//'):
            s = 'http://' + s[6:]
        elif s.lower().startswith('https//'):
            s = 'https://' + s[7:]

        # Se for caminho relativo começando com barra, prefixa base
        if s.startswith('/') and base:
            s = f"{base}{s}"

        has_scheme = bool(re.match(r'^[a-zA-Z][a-zA-Z0-9+\.-]*:', s))
        looks_like_domain = bool(re.match(r'^[a-z0-9\.-]+\.[a-z]{2,}', s, re.IGNORECASE))

        # Caminho relativo sem barra (ex.: "rc/clk?...")
        if not has_scheme and not looks_like_domain and base:
            s = f"{base.rstrip('/')}/{s.lstrip('/')}"

        # Adiciona https:// quando iniciar com www.
        if s.lower().startswith('www.'):
            s = f"https://{s}"

        # Se ainda não tiver esquema, prefixa https://
        if not has_scheme:
            s = f"https://{s.lstrip('/')}"

        # Valida URL
        try:
            from urllib.parse import urlparse
            u = urlparse(s)
            if not u.scheme or not u.netloc:
                return None
            return s
        except Exception:
            return None
    
    def salvar_resultados(self, vagas: List[Vaga], arquivo: str = 'vagas_encontradas.json'):
        """Salva resultados em arquivo JSON"""
        try:
            dados = {
                'timestamp': datetime.now().isoformat(),
                'total_vagas': len(vagas),
                'vagas': [asdict(vaga) for vaga in vagas]
            }
            
            fullpath = arquivo if os.path.isabs(arquivo) else os.path.join(BASE_DIR, arquivo)
            with open(fullpath, 'w', encoding='utf-8') as f:
                json.dump(dados, f, ensure_ascii=False, indent=2)
            
            logging.info(f"Resultados salvos em {os.path.basename(fullpath)}")
            
        except Exception as e:
            logging.error(f"Erro ao salvar resultados: {e}")

    def _normalize_modalidade(self, valor: Optional[str]) -> str:
        """Normaliza modalidade para: HOME OFFICE | PRESENCIAL | HÍBRIDO."""
        if not valor:
            return ""
        v = valor.strip().lower()
        if any(x in v for x in ["home office", "home-office", "remoto", "remota"]):
            return "HOME OFFICE"
        if any(x in v for x in ["hibrido", "híbrido", "hibrida", "híbrida"]):
            return "HÍBRIDO"
        if "presencial" in v:
            return "PRESENCIAL"
        return ""

    def _inferir_modalidade(self, titulo: str, descricao: str, localizacao: str) -> str:
        """Infere modalidade com base em título, descrição e localização."""
        texto = f"{titulo} {descricao} {localizacao}".lower()
        if any(x in texto for x in ["home office", "home-office", "remoto", "remota"]):
            return "Home office"
        if any(x in texto for x in ["hibrido", "híbrido", "hibrida", "híbrida"]):
            return "Híbrido"
        if "presencial" in texto:
            return "Presencial"
        if (localizacao or '').strip().lower() == 'remoto':
            return "Home office"
        return ""

    def _scrape_glassdoor(self, criterios: Dict) -> List[Vaga]:
        """Scraping do Glassdoor (simulado - API limitada)"""
        vagas = []
        try:
            # Simulação de dados do Glassdoor
            cargo = criterios.get('cargo', 'Desenvolvedor')
            local_pref = (criterios.get('localizacao') or '').strip()
            
            # Lista de cidades brasileiras para variedade
            cidades = [
                'São Paulo, SP', 'Rio de Janeiro, RJ', 'Belo Horizonte, MG', 
                'Porto Alegre, RS', 'Curitiba, PR', 'Salvador, BA', 'Brasília, DF',
                'Fortaleza, CE', 'Recife, PE', 'Goiânia, GO', 'Florianópolis, SC'
            ]
            
            # Dados simulados baseados no padrão do Glassdoor
            from urllib.parse import quote_plus
            q = quote_plus(cargo)
            lq = quote_plus(local_pref or '')
            vagas_simuladas = [
                {
                    'titulo': f'{cargo} Sênior',
                    'empresa': 'Tech Company Brasil',
                    'localizacao': (local_pref or cidades[random.randint(0, len(cidades)-1)]),
                    'salario': 'R$ 8.000 - R$ 12.000',
                    'descricao': None,
                    'url': f'https://www.glassdoor.com.br/Job/jobs.htm?sc.keyword={q}'
                },
                {
                    'titulo': f'{cargo} Pleno',
                    'empresa': 'Startup Inovadora',
                    'localizacao': (local_pref or cidades[random.randint(0, len(cidades)-1)]),
                    'salario': 'R$ 6.000 - R$ 9.000',
                    'descricao': None,
                    'url': f'https://www.glassdoor.com.br/Job/jobs.htm?sc.keyword={q}'
                }
            ]
            
            for vaga_data in vagas_simuladas:
                # Descrição variada baseada no cargo e empresa
                desc = vaga_data['descricao'] or self._gerar_descricao(cargo, vaga_data['empresa'])
                vaga = Vaga(
                    titulo=vaga_data['titulo'],
                    empresa=vaga_data['empresa'],
                    localizacao=vaga_data['localizacao'],
                    salario=vaga_data['salario'],
                    descricao=desc,
                    data_publicacao=(datetime.now() - timedelta(days=random.randint(1, 7))).strftime('%Y-%m-%d'),
                    site_origem='Glassdoor',
                    url=vaga_data['url'],
                    tipo_contrato='CLT',
                    nivel_experiencia='Pleno/Sênior'
                )
                vagas.append(vaga)
                
        except Exception as e:
            logging.error(f"Erro no scraping do Glassdoor: {e}")
        
        return vagas

    def _scrape_infojobs(self, criterios: Dict) -> List[Vaga]:
        """Scraping do InfoJobs (simulado)"""
        vagas = []
        try:
            cargo = criterios.get('cargo', 'Desenvolvedor')
            
            # Lista de cidades brasileiras para variedade
            cidades = [
                'São Paulo, SP', 'Rio de Janeiro, RJ', 'Belo Horizonte, MG', 
                'Porto Alegre, RS', 'Curitiba, PR', 'Salvador, BA', 'Brasília, DF',
                'Fortaleza, CE', 'Recife, PE', 'Goiânia, GO', 'Florianópolis, SC'
            ]
            
            from urllib.parse import quote_plus
            q = quote_plus(cargo)
            vagas_simuladas = [
                {
                    'titulo': f'{cargo} Jr/Pleno',
                    'empresa': 'Consultoria Tech',
                    'localizacao': cidades[random.randint(0, len(cidades)-1)],
                    'salario': 'R$ 4.500 - R$ 7.500',
                    'descricao': f'Vaga para {cargo} com crescimento profissional.',
                    'url': f'https://www.infojobs.com.br/empregos.aspx?keyword={q}'
                },
                {
                    'titulo': f'{cargo} Sênior',
                    'empresa': 'Empresa Digital',
                    'localizacao': cidades[random.randint(0, len(cidades)-1)],
                    'salario': 'R$ 7.000 - R$ 11.000',
                    'descricao': f'Oportunidade sênior para {cargo}.',
                    'url': f'https://www.infojobs.com.br/empregos.aspx?keyword={q}'
                }
            ]
            
            for vaga_data in vagas_simuladas:
                vaga = Vaga(
                    titulo=vaga_data['titulo'],
                    empresa=vaga_data['empresa'],
                    localizacao=vaga_data['localizacao'],
                    salario=vaga_data['salario'],
                    descricao=vaga_data['descricao'],
                    data_publicacao=(datetime.now() - timedelta(days=random.randint(1, 5))).strftime('%Y-%m-%d'),
                    site_origem='InfoJobs',
                    url=vaga_data['url'],
                    tipo_contrato='CLT',
                    nivel_experiencia='Pleno'
                )
                vagas.append(vaga)
                
        except Exception as e:
            logging.error(f"Erro no scraping do InfoJobs: {e}")
        
        return vagas

    def _scrape_stackoverflow(self, criterios: Dict) -> List[Vaga]:
        """Scraping do Stack Overflow Jobs (simulado)"""
        vagas = []
        try:
            cargo = criterios.get('cargo', 'Desenvolvedor')
            
            from urllib.parse import quote_plus
            q = quote_plus(cargo)
            lq = quote_plus(criterios.get('localizacao') or '')
            vagas_simuladas = [
                {
                    'titulo': f'Senior {cargo}',
                    'empresa': 'Tech Startup',
                    'localizacao': 'Remoto',
                    'salario': 'R$ 10.000 - R$ 15.000',
                    'descricao': f'Remote {cargo} position with cutting-edge technologies.',
                    'url': f'https://stackoverflow.com/jobs?q={q}&l={lq}'
                },
                {
                    'titulo': f'Lead {cargo}',
                    'empresa': 'Global Company',
                    'localizacao': 'São Paulo/Remoto',
                    'salario': 'R$ 12.000 - R$ 18.000',
                    'descricao': f'Leadership role for experienced {cargo}.',
                    'url': f'https://stackoverflow.com/jobs?q={q}&l={lq}'
                }
            ]
            
            for vaga_data in vagas_simuladas:
                vaga = Vaga(
                    titulo=vaga_data['titulo'],
                    empresa=vaga_data['empresa'],
                    localizacao=vaga_data['localizacao'],
                    salario=vaga_data['salario'],
                    descricao=vaga_data['descricao'],
                    data_publicacao=(datetime.now() - timedelta(days=random.randint(1, 3))).strftime('%Y-%m-%d'),
                    site_origem='Stack Overflow Jobs',
                    url=vaga_data['url'],
                    tipo_contrato='PJ/CLT',
                    nivel_experiencia='Sênior'
                )
                vagas.append(vaga)
                
        except Exception as e:
            logging.error(f"Erro no scraping do Stack Overflow Jobs: {e}")
        
        return vagas

    def _scrape_github(self, criterios: Dict) -> List[Vaga]:
        """Scraping do GitHub Jobs (simulado)"""
        vagas = []
        try:
            cargo = criterios.get('cargo', 'Desenvolvedor')
            
            from urllib.parse import quote_plus
            q = quote_plus(cargo)
            vagas_simuladas = [
                {
                    'titulo': f'{cargo} - Open Source',
                    'empresa': 'GitHub Partner',
                    'localizacao': 'Remoto Global',
                    'salario': 'USD 4.000 - USD 7.000',
                    'descricao': f'{cargo} position focused on open source projects.',
                    'url': f'https://github.com/search?q={q}&type=repositories'
                },
                {
                    'titulo': f'DevOps {cargo}',
                    'empresa': 'Cloud Native Startup',
                    'localizacao': 'Remoto',
                    'salario': 'R$ 10.000 - R$ 16.000',
                    'descricao': f'DevOps {cargo} role with Kubernetes and Docker.',
                    'url': f'https://github.com/search?q={q}&type=repositories'
                }
            ]
            
            for vaga_data in vagas_simuladas:
                vaga = Vaga(
                    titulo=vaga_data['titulo'],
                    empresa=vaga_data['empresa'],
                    localizacao=vaga_data['localizacao'],
                    salario=vaga_data['salario'],
                    descricao=vaga_data['descricao'],
                    data_publicacao=(datetime.now() - timedelta(days=random.randint(1, 4))).strftime('%Y-%m-%d'),
                    site_origem='GitHub Jobs',
                    url=vaga_data['url'],
                    tipo_contrato='PJ',
                    nivel_experiencia='Sênior'
                )
                vagas.append(vaga)
                
        except Exception as e:
            logging.error(f"Erro no scraping do GitHub Jobs: {e}")
        
        return vagas

    def _scrape_trampos(self, criterios: Dict) -> List[Vaga]:
        """Scraping do Trampos.co (simulado)"""
        vagas = []
        try:
            cargo = criterios.get('cargo', 'Desenvolvedor')
            localizacao = criterios.get('localizacao', 'Brasil')
            
            from urllib.parse import quote_plus
            q = quote_plus(cargo)
            lq = quote_plus(localizacao)
            vagas_simuladas = [
                {
                    'titulo': f'{cargo} Mobile',
                    'empresa': 'App Studio',
                    'localizacao': localizacao,
                    'salario': 'R$ 6.500 - R$ 9.500',
                    'descricao': f'{cargo} Mobile com React Native e Flutter.',
                    'url': f'https://trampos.co/oportunidades?q={q}&l={lq}'
                },
                {
                    'titulo': f'{cargo} Web',
                    'empresa': 'Web Agency',
                    'localizacao': localizacao,
                    'salario': 'R$ 5.000 - R$ 8.000',
                    'descricao': f'{cargo} Web com foco em e-commerce.',
                    'url': f'https://trampos.co/oportunidades?q={q}&l={lq}'
                }
            ]
            
            for vaga_data in vagas_simuladas:
                vaga = Vaga(
                    titulo=vaga_data['titulo'],
                    empresa=vaga_data['empresa'],
                    localizacao=vaga_data['localizacao'],
                    salario=vaga_data['salario'],
                    descricao=vaga_data['descricao'],
                    data_publicacao=(datetime.now() - timedelta(days=random.randint(1, 6))).strftime('%Y-%m-%d'),
                    site_origem='Trampos.co',
                    url=vaga_data['url'],
                    tipo_contrato='CLT',
                    nivel_experiencia='Pleno'
                )
                vagas.append(vaga)
                
        except Exception as e:
            logging.error(f"Erro no scraping do Trampos.co: {e}")
        
        return vagas

    def _scrape_rocket(self, criterios: Dict) -> List[Vaga]:
        """Scraping do Rocket Jobs (simulado)"""
        vagas = []
        try:
            cargo = criterios.get('cargo', 'Desenvolvedor')
            
            from urllib.parse import quote_plus
            q = quote_plus(cargo)
            vagas_simuladas = [
                {
                    'titulo': f'{cargo} Rocket',
                    'empresa': 'Rocket Company',
                    'localizacao': 'São Paulo/Remoto',
                    'salario': 'R$ 8.500 - R$ 13.000',
                    'descricao': f'{cargo} position in fast-growing rocket company.',
                    'url': f'https://rocketjobs.com.br/vagas?q={q}'
                },
                {
                    'titulo': f'Lead {cargo}',
                    'empresa': 'Scale-up Tech',
                    'localizacao': 'Remoto',
                    'salario': 'R$ 12.000 - R$ 18.000',
                    'descricao': f'Tech Lead {cargo} role with team management.',
                    'url': f'https://rocketjobs.com.br/vagas?q={q}'
                }
            ]
            
            for vaga_data in vagas_simuladas:
                vaga = Vaga(
                    titulo=vaga_data['titulo'],
                    empresa=vaga_data['empresa'],
                    localizacao=vaga_data['localizacao'],
                    salario=vaga_data['salario'],
                    descricao=vaga_data['descricao'],
                    data_publicacao=(datetime.now() - timedelta(days=random.randint(1, 2))).strftime('%Y-%m-%d'),
                    site_origem='Rocket Jobs',
                    url=vaga_data['url'],
                    tipo_contrato='CLT/PJ',
                    nivel_experiencia='Sênior/Lead'
                )
                vagas.append(vaga)
                
        except Exception as e:
            logging.error(f"Erro no scraping do Rocket Jobs: {e}")
        
        return vagas

    def _scrape_startup(self, criterios: Dict) -> List[Vaga]:
        """Scraping do Startup Jobs (simulado)"""
        vagas = []
        try:
            cargo = criterios.get('cargo', 'Desenvolvedor')
            
            from urllib.parse import quote_plus
            q = quote_plus(cargo)
            vagas_simuladas = [
                {
                    'titulo': f'{cargo} Startup',
                    'empresa': 'Early Stage Startup',
                    'localizacao': 'Remoto',
                    'salario': 'R$ 7.000 - R$ 11.000 + Equity',
                    'descricao': f'{cargo} role in early-stage startup with equity.',
                    'url': f'https://startupjobs.com/jobs?keywords={q}'
                },
                {
                    'titulo': f'Founding {cargo}',
                    'empresa': 'New Venture',
                    'localizacao': 'São Paulo/Remoto',
                    'salario': 'R$ 9.000 - R$ 14.000 + Equity',
                    'descricao': f'Founding {cargo} position with significant equity.',
                    'url': f'https://startupjobs.com/jobs?keywords={q}'
                }
            ]
            
            for vaga_data in vagas_simuladas:
                vaga = Vaga(
                    titulo=vaga_data['titulo'],
                    empresa=vaga_data['empresa'],
                    localizacao=vaga_data['localizacao'],
                    salario=vaga_data['salario'],
                    descricao=vaga_data['descricao'],
                    data_publicacao=(datetime.now() - timedelta(days=random.randint(1, 3))).strftime('%Y-%m-%d'),
                    site_origem='Startup Jobs',
                    url=vaga_data['url'],
                    tipo_contrato='PJ/CLT',
                    nivel_experiencia='Sênior/Founding'
                )
                vagas.append(vaga)
                
        except Exception as e:
            logging.error(f"Erro no scraping do Startup Jobs: {e}")
        
        return vagas

def main():
    """Função principal para teste"""
    scraper = JobScraper()
    
    # Critérios de exemplo
    criterios = {
        'cargo': 'Desenvolvedor Python',
        'localizacao': 'São Paulo',
        'salario-min': '5000',
        'palavras-chave': 'Python, Django, Flask',
        'sites': ['indeed', 'catho', 'vagas', 'linkedin']
    }
    
    print("🔍 Iniciando busca de vagas...")
    vagas = scraper.buscar_vagas(criterios)
    
    print(f"\n✅ Encontradas {len(vagas)} vagas!")
    
    # Exibe primeiras 5 vagas
    for i, vaga in enumerate(vagas[:5], 1):
        print(f"\n--- Vaga {i} ---")
        print(f"Título: {vaga.titulo}")
        print(f"Empresa: {vaga.empresa}")
        print(f"Local: {vaga.localizacao}")
        print(f"Salário: {vaga.salario}")
        print(f"Site: {vaga.site_origem}")
    
    # Salva resultados
    scraper.salvar_resultados(vagas)

if __name__ == "__main__":
    main()

