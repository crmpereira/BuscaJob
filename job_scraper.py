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
from dataclasses import dataclass, asdict
from typing import List, Dict, Optional
import concurrent.futures
from fake_useragent import UserAgent

# Configuração de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('buscajob.log'),
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
            localizacoes_mock = ['São Paulo, SP', 'Rio de Janeiro, RJ', 'Belo Horizonte, MG', 'Remoto']
            
            for i in range(random.randint(3, 8)):
                empresa = empresas_mock[i % len(empresas_mock)]
                vaga = Vaga(
                    titulo=f"{cargo} - {empresa}",
                    empresa=empresa,
                    localizacao=localizacoes_mock[i % len(localizacoes_mock)],
                    salario=f"R$ {random.randint(3000, 12000):,}".replace(',', '.'),
                    descricao=f"Oportunidade para {cargo} em empresa inovadora. Requisitos: experiência com tecnologias modernas.",
                    data_publicacao=(datetime.now() - timedelta(days=random.randint(0, 7))).strftime('%d/%m/%Y'),
                    site_origem='Indeed',
                    url=f'https://br.indeed.com/viewjob?jk={random.randint(1000000000000000, 9999999999999999)}&tk={random.randint(100000000000000000000000000000000, 999999999999999999999999999999999)}',
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
            localizacoes_mock = ['São Paulo, SP', 'Rio de Janeiro, RJ', 'Remoto']
            
            for i in range(random.randint(3, 8)):
                empresa = empresas_mock[i % len(empresas_mock)]
                vaga = Vaga(
                    titulo=f"{cargo} - {empresa}",
                    empresa=empresa,
                    localizacao=localizacoes_mock[i % len(localizacoes_mock)],
                    salario=f"R$ {random.randint(3000, 12000):,}".replace(',', '.'),
                    descricao=f"Oportunidade para {cargo} em empresa inovadora. Requisitos: experiência com tecnologias modernas.",
                    data_publicacao=(datetime.now() - timedelta(days=random.randint(0, 7))).strftime('%d/%m/%Y'),
                    site_origem='Catho',
                    url=f'https://www.catho.com.br/vagas/{cargo.lower().replace(" ", "-")}-{empresa.lower()}-{random.randint(1000000, 9999999)}/',
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
                vaga = Vaga(
                    titulo=f"{cargo} Pleno/Sênior",
                    empresa=f"Empresa {i+1}",
                    localizacao="São Paulo, SP" if i % 2 == 0 else "Remoto",
                    salario=f"R$ {random.randint(4000, 15000):,}".replace(',', '.'),
                    descricao=f"Vaga para {cargo} com foco em desenvolvimento de soluções inovadoras.",
                    data_publicacao=(datetime.now() - timedelta(days=random.randint(0, 5))).strftime('%d/%m/%Y'),
                    site_origem='Vagas.com',
                    url=f'https://www.vagas.com.br/vagas-de-{cargo.lower().replace(" ", "-")}/empresa-{i+1}?id={random.randint(1000000, 9999999)}',
                    nivel_experiencia='Pleno'
                )
                vagas.append(vaga)
                
        except Exception as e:
            logging.error(f"Erro no scraping do Vagas.com: {e}")
        
        return vagas
    
    def _scrape_linkedin(self, criterios: Dict) -> List[Vaga]:
        """Scraping do LinkedIn (implementação simplificada)"""
        vagas = []
        
        try:
            cargo = criterios.get('cargo', '')
            
            # LinkedIn tem proteções anti-bot, implementação mock
            for i in range(random.randint(4, 10)):
                vaga = Vaga(
                    titulo=f"{cargo} - Oportunidade Exclusiva",
                    empresa=f"LinkedIn Company {i+1}",
                    localizacao="Híbrido" if i % 3 == 0 else "São Paulo, SP",
                    salario="A combinar",
                    descricao=f"Excelente oportunidade para {cargo} em empresa de tecnologia. Benefícios competitivos.",
                    data_publicacao=(datetime.now() - timedelta(days=random.randint(0, 3))).strftime('%d/%m/%Y'),
                    site_origem='LinkedIn',
                    url=f'https://www.linkedin.com/jobs/view/{random.randint(1000000000, 9999999999)}/?refId={random.randint(100000, 999999)}',
                    tipo_contrato='CLT'
                )
                vagas.append(vaga)
                
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
    
    def salvar_resultados(self, vagas: List[Vaga], arquivo: str = 'vagas_encontradas.json'):
        """Salva resultados em arquivo JSON"""
        try:
            dados = {
                'timestamp': datetime.now().isoformat(),
                'total_vagas': len(vagas),
                'vagas': [asdict(vaga) for vaga in vagas]
            }
            
            with open(arquivo, 'w', encoding='utf-8') as f:
                json.dump(dados, f, ensure_ascii=False, indent=2)
            
            logging.info(f"Resultados salvos em {arquivo}")
            
        except Exception as e:
            logging.error(f"Erro ao salvar resultados: {e}")

    def _scrape_glassdoor(self, criterios: Dict) -> List[Vaga]:
        """Scraping do Glassdoor (simulado - API limitada)"""
        vagas = []
        try:
            # Simulação de dados do Glassdoor
            cargo = criterios.get('cargo', 'Desenvolvedor')
            
            # Lista de cidades brasileiras para variedade
            cidades = [
                'São Paulo, SP', 'Rio de Janeiro, RJ', 'Belo Horizonte, MG', 
                'Porto Alegre, RS', 'Curitiba, PR', 'Salvador, BA', 'Brasília, DF',
                'Fortaleza, CE', 'Recife, PE', 'Goiânia, GO', 'Florianópolis, SC'
            ]
            
            # Dados simulados baseados no padrão do Glassdoor
            vagas_simuladas = [
                {
                    'titulo': f'{cargo} Sênior',
                    'empresa': 'Tech Company Brasil',
                    'localizacao': cidades[random.randint(0, len(cidades)-1)],
                    'salario': 'R$ 8.000 - R$ 12.000',
                    'descricao': f'Vaga para {cargo} com experiência em tecnologias modernas.',
                    'url': f'https://www.glassdoor.com.br/Vaga/{cargo.lower().replace(" ", "-")}-senior-tech-company-brasil-JV_IC2643_KO0,{len(cargo)+7}_KE{len(cargo)+8},{len(cargo)+25}.htm?jl={random.randint(1000000, 9999999)}'
                },
                {
                    'titulo': f'{cargo} Pleno',
                    'empresa': 'Startup Inovadora',
                    'localizacao': cidades[random.randint(0, len(cidades)-1)],
                    'salario': 'R$ 6.000 - R$ 9.000',
                    'descricao': f'Oportunidade para {cargo} em ambiente ágil.',
                    'url': f'https://www.glassdoor.com.br/Vaga/{cargo.lower().replace(" ", "-")}-pleno-startup-inovadora-JV_IC2643_KO0,{len(cargo)+6}_KE{len(cargo)+7},{len(cargo)+23}.htm?jl={random.randint(1000000, 9999999)}'
                }
            ]
            
            for vaga_data in vagas_simuladas:
                vaga = Vaga(
                    titulo=vaga_data['titulo'],
                    empresa=vaga_data['empresa'],
                    localizacao=vaga_data['localizacao'],
                    salario=vaga_data['salario'],
                    descricao=vaga_data['descricao'],
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
            
            vagas_simuladas = [
                {
                    'titulo': f'{cargo} Jr/Pleno',
                    'empresa': 'Consultoria Tech',
                    'localizacao': cidades[random.randint(0, len(cidades)-1)],
                    'salario': 'R$ 4.500 - R$ 7.500',
                    'descricao': f'Vaga para {cargo} com crescimento profissional.',
                    'url': f'https://www.infojobs.com.br/vaga-de-{cargo.lower().replace(" ", "-")}-jr-pleno-em-consultoria-tech.aspx?jobId={random.randint(100000, 999999)}'
                },
                {
                    'titulo': f'{cargo} Sênior',
                    'empresa': 'Empresa Digital',
                    'localizacao': cidades[random.randint(0, len(cidades)-1)],
                    'salario': 'R$ 7.000 - R$ 11.000',
                    'descricao': f'Oportunidade sênior para {cargo}.',
                    'url': f'https://www.infojobs.com.br/vaga-de-{cargo.lower().replace(" ", "-")}-senior-em-empresa-digital.aspx?jobId={random.randint(100000, 999999)}'
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
            
            vagas_simuladas = [
                {
                    'titulo': f'Senior {cargo}',
                    'empresa': 'Tech Startup',
                    'localizacao': 'Remoto',
                    'salario': 'R$ 10.000 - R$ 15.000',
                    'descricao': f'Remote {cargo} position with cutting-edge technologies.',
                    'url': f'https://stackoverflow.com/jobs/{random.randint(100000, 999999)}/senior-{cargo.lower().replace(" ", "-")}-tech-startup'
                },
                {
                    'titulo': f'Lead {cargo}',
                    'empresa': 'Global Company',
                    'localizacao': 'São Paulo/Remoto',
                    'salario': 'R$ 12.000 - R$ 18.000',
                    'descricao': f'Leadership role for experienced {cargo}.',
                    'url': f'https://stackoverflow.com/jobs/{random.randint(100000, 999999)}/lead-{cargo.lower().replace(" ", "-")}-global-company'
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
            
            vagas_simuladas = [
                {
                    'titulo': f'{cargo} - Open Source',
                    'empresa': 'GitHub Partner',
                    'localizacao': 'Remoto Global',
                    'salario': 'USD 4.000 - USD 7.000',
                    'descricao': f'{cargo} position focused on open source projects.',
                    'url': 'https://github.com/jobs/exemplo'
                },
                {
                    'titulo': f'DevOps {cargo}',
                    'empresa': 'Cloud Native Startup',
                    'localizacao': 'Remoto',
                    'salario': 'R$ 10.000 - R$ 16.000',
                    'descricao': f'DevOps {cargo} role with Kubernetes and Docker.',
                    'url': 'https://github.com/jobs/exemplo-2'
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
            
            vagas_simuladas = [
                {
                    'titulo': f'{cargo} Mobile',
                    'empresa': 'App Studio',
                    'localizacao': localizacao,
                    'salario': 'R$ 6.500 - R$ 9.500',
                    'descricao': f'{cargo} Mobile com React Native e Flutter.',
                    'url': 'https://trampos.co/vaga-exemplo'
                },
                {
                    'titulo': f'{cargo} Web',
                    'empresa': 'Web Agency',
                    'localizacao': localizacao,
                    'salario': 'R$ 5.000 - R$ 8.000',
                    'descricao': f'{cargo} Web com foco em e-commerce.',
                    'url': 'https://trampos.co/vaga-exemplo-2'
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
            
            vagas_simuladas = [
                {
                    'titulo': f'{cargo} Rocket',
                    'empresa': 'Rocket Company',
                    'localizacao': 'São Paulo/Remoto',
                    'salario': 'R$ 8.500 - R$ 13.000',
                    'descricao': f'{cargo} position in fast-growing rocket company.',
                    'url': 'https://rocketjobs.com.br/vaga-exemplo'
                },
                {
                    'titulo': f'Lead {cargo}',
                    'empresa': 'Scale-up Tech',
                    'localizacao': 'Remoto',
                    'salario': 'R$ 12.000 - R$ 18.000',
                    'descricao': f'Tech Lead {cargo} role with team management.',
                    'url': 'https://rocketjobs.com.br/vaga-exemplo-2'
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
            
            vagas_simuladas = [
                {
                    'titulo': f'{cargo} Startup',
                    'empresa': 'Early Stage Startup',
                    'localizacao': 'Remoto',
                    'salario': 'R$ 7.000 - R$ 11.000 + Equity',
                    'descricao': f'{cargo} role in early-stage startup with equity.',
                    'url': 'https://startupjobs.com/vaga-exemplo'
                },
                {
                    'titulo': f'Founding {cargo}',
                    'empresa': 'New Venture',
                    'localizacao': 'São Paulo/Remoto',
                    'salario': 'R$ 9.000 - R$ 14.000 + Equity',
                    'descricao': f'Founding {cargo} position with significant equity.',
                    'url': 'https://startupjobs.com/vaga-exemplo-2'
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