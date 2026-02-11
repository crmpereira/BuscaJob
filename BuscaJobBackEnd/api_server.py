#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
BuscaJob API Server
Servidor Flask para conectar frontend com backend de scraping
"""

from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import json
import os
from datetime import datetime
import logging
from job_scraper import JobScraper
import threading
import schedule
import time
import smtplib
from email.message import EmailMessage

# Diretório base do backend (para salvar/ler arquivos sempre dentro do pacote)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Utilitário: enviar e-mail com anexo
def send_email_with_attachment(subject: str, body: str, file_path: str):
    smtp_host = os.environ.get("SMTP_HOST")
    smtp_port = int(os.environ.get("SMTP_PORT", "587"))
    smtp_user = os.environ.get("SMTP_USER")
    smtp_pass = os.environ.get("SMTP_PASS")
    email_from = os.environ.get("EMAIL_FROM")
    email_to = os.environ.get("EMAIL_TO")

    if not all([smtp_host, smtp_user, smtp_pass, email_from, email_to]):
        raise RuntimeError(
            "Configuração de email incompleta (SMTP_HOST/SMTP_USER/SMTP_PASS/EMAIL_FROM/EMAIL_TO)"
        )

    msg = EmailMessage()
    msg["Subject"] = subject
    msg["From"] = email_from
    msg["To"] = email_to
    msg.set_content(body)

    with open(file_path, "rb") as f:
        data = f.read()
    msg.add_attachment(data, maintype="application", subtype="json", filename=os.path.basename(file_path))

    with smtplib.SMTP(smtp_host, smtp_port) as s:
        s.starttls()
        s.login(smtp_user, smtp_pass)
        s.send_message(msg)

# Configuração de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)  # Permite requisições do frontend

# Instância global do scraper
scraper = JobScraper()

# Armazenamento em memória (em produção, usar banco de dados)
resultados_cache = {}
configuracoes_salvas = {}
estatisticas = {
    'total_buscas': 0,
    'total_vagas': 0,
    'vagas_salvas': 0
}

# Removido: rotas de frontend que serviam arquivos estáticos
# @app.route('/')
# def index():
#     """Serve a página principal"""
#     return send_from_directory('.', 'index.html')

# @app.route('/<path:filename>')
# def serve_static(filename):
#     """Serve arquivos estáticos"""
#     return send_from_directory('.', filename)

# Nova rota raiz apenas informativa, sem frontend
@app.route('/')
def root():
    """Rota raiz informativa para ambiente somente API"""
    return jsonify({
        'success': True,
        'message': 'BuscaJob API ativa (sem frontend HTML)',
        'endpoints': [
            '/api/relatorio-fixo',
            '/api/ultimo-resultado',
            '/api/buscar-vagas',
            '/api/sites',
            '/api/health'
        ]
    })
@app.route('/api/ultimo-resultado', methods=['GET'])
def ultimo_resultado():
    """Retorna o último arquivo de resultados salvo"""
    try:
        base_dir = BASE_DIR
        files = [f for f in os.listdir(base_dir) if f.startswith('resultados_') and f.endswith('.json')]
        if not files:
            return jsonify({'success': False, 'error': 'Nenhum arquivo de resultados encontrado'}), 404
        latest_file = max(files, key=lambda f: os.path.getmtime(os.path.join(base_dir, f)))
        with open(os.path.join(base_dir, latest_file), 'r', encoding='utf-8') as f:
            data = json.load(f)
        vagas = data.get('vagas', [])
        normalized = []
        for idx, v in enumerate(vagas):
            normalized.append({
                'id': v.get('id') or f"vaga_{idx}_{int(time.time())}",
                'titulo': v.get('titulo', ''),
                'empresa': v.get('empresa', ''),
                'localizacao': v.get('localizacao', ''),
                'salario': v.get('salario', ''),
                'descricao': v.get('descricao', ''),
                'dataPublicacao': v.get('dataPublicacao', ''),
                'site': v.get('site') or v.get('site_origem', ''),
                'url': v.get('url', ''),
                'tipo': v.get('tipo') or v.get('tipo_contrato', ''),
                'nivel': v.get('nivel') or v.get('nivel_experiencia', ''),
                'modalidade': v.get('modalidade', ''),
            })
        return jsonify({'success': True, 'vagas': normalized, 'total': len(normalized), 'arquivo': latest_file})
    except Exception as e:
        logger.exception(f'Erro ao carregar último resultado: {e}')
        return jsonify({'success': False, 'error': 'Erro ao carregar arquivo'}), 500

@app.route('/api/buscar-vagas', methods=['POST'])
def buscar_vagas():
    """Endpoint para buscar vagas"""
    try:
        # Remove arquivos de resultados antigos antes de iniciar uma nova busca
        try:
            cleanup_old_result_files()
        except Exception as _cleanup_err:
            logger.warning(f"Falha ao limpar arquivos antigos antes da busca: {_cleanup_err}")

        criterios = request.get_json()
        
        if not criterios:
            return jsonify({'error': 'Critérios de busca não fornecidos'}), 400
        
        logger.info(f"Recebida solicitação de busca: {criterios}")
        
        # Valida critérios obrigatórios
        if not criterios.get('cargo'):
            return jsonify({'error': 'Campo cargo é obrigatório'}), 400
        
        # Executa busca
        vagas = scraper.buscar_vagas(criterios)
        
        # Converte vagas para dicionário
        vagas_dict = []
        for vaga in vagas:
            vaga_dict = {
                'id': f"vaga_{hash(vaga.titulo + vaga.empresa)}",
                'titulo': vaga.titulo,
                'empresa': vaga.empresa,
                'localizacao': vaga.localizacao,
                'salario': vaga.salario,
                'descricao': vaga.descricao,
                'dataPublicacao': vaga.data_publicacao,
                'site': vaga.site_origem,
                'url': vaga.url,
                'tipo': getattr(vaga, 'tipo_contrato', ''),
                'nivel': getattr(vaga, 'nivel_experiencia', ''),
                'modalidade': getattr(vaga, 'modalidade', '')
            }
            vagas_dict.append(vaga_dict)
        
        # Atualiza estatísticas
        estatisticas['total_buscas'] += 1
        estatisticas['total_vagas'] += len(vagas_dict)
        
        # Cache dos resultados
        timestamp = datetime.now().isoformat()
        resultados_cache[timestamp] = {
            'criterios': criterios,
            'vagas': vagas_dict,
            'timestamp': timestamp
        }
        
        # Salva resultados em arquivo
        salvar_resultados_arquivo(vagas_dict, criterios)
        
        response = {
            'success': True,
            'vagas': vagas_dict,
            'total': len(vagas_dict),
            'timestamp': timestamp
        }
        
        logger.info(f"Busca concluída: {len(vagas_dict)} vagas encontradas")
        return jsonify(response)
        
    except Exception as e:
        logger.error(f"Erro na busca de vagas: {e}")
        return jsonify({'error': f'Erro interno: {str(e)}'}), 500

@app.route('/api/salvar-configuracao', methods=['POST'])
def salvar_configuracao():
    """Salva configuração de busca"""
    try:
        config = request.get_json()
        
        if not config:
            return jsonify({'error': 'Configuração não fornecida'}), 400
        
        # Gera ID único para a configuração
        config_id = f"config_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        configuracoes_salvas[config_id] = {
            'id': config_id,
            'config': config,
            'timestamp': datetime.now().isoformat()
        }
        
        # Salva em arquivo
        with open(os.path.join(BASE_DIR, 'configuracoes.json'), 'w', encoding='utf-8') as f:
            json.dump(configuracoes_salvas, f, ensure_ascii=False, indent=2)
        
        logger.info(f"Configuração salva: {config_id}")
        
        return jsonify({
            'success': True,
            'config_id': config_id,
            'message': 'Configuração salva com sucesso'
        })
        
    except Exception as e:
        logger.error(f"Erro ao salvar configuração: {e}")
        return jsonify({'error': f'Erro interno: {str(e)}'}), 500

@app.route('/api/configuracoes', methods=['GET'])
def listar_configuracoes():
    """Lista configurações salvas"""
    try:
        # Carrega configurações do arquivo se existir
        if os.path.exists(os.path.join(BASE_DIR, 'configuracoes.json')):
            with open(os.path.join(BASE_DIR, 'configuracoes.json'), 'r', encoding='utf-8') as f:
                configuracoes_salvas.update(json.load(f))
        
        configs = list(configuracoes_salvas.values())
        
        return jsonify({
            'success': True,
            'configuracoes': configs
        })
        
    except Exception as e:
        logger.error(f"Erro ao listar configurações: {e}")
        return jsonify({'error': f'Erro interno: {str(e)}'}), 500

@app.route('/api/estatisticas', methods=['GET'])
def obter_estatisticas():
    """Retorna estatísticas de uso"""
    try:
        # Carrega estatísticas do arquivo se existir
        if os.path.exists(os.path.join(BASE_DIR, 'estatisticas.json')):
            with open(os.path.join(BASE_DIR, 'estatisticas.json'), 'r', encoding='utf-8') as f:
                estatisticas.update(json.load(f))
        
        return jsonify({
            'success': True,
            'estatisticas': estatisticas
        })
        
    except Exception as e:
        logger.error(f"Erro ao obter estatísticas: {e}")
        return jsonify({'error': f'Erro interno: {str(e)}'}), 500

@app.route('/api/salvar-vaga', methods=['POST'])
def salvar_vaga():
    """Salva uma vaga como favorita"""
    try:
        data = request.get_json()
        vaga_id = data.get('vaga_id')
        
        if not vaga_id:
            return jsonify({'error': 'ID da vaga não fornecido'}), 400
        
        # Carrega vagas salvas
        vagas_salvas = []
        if os.path.exists(os.path.join(BASE_DIR, 'vagas_salvas.json')):
            with open(os.path.join(BASE_DIR, 'vagas_salvas.json'), 'r', encoding='utf-8') as f:
                vagas_salvas = json.load(f)
        
        # Verifica se já foi salva
        if vaga_id not in vagas_salvas:
            vagas_salvas.append(vaga_id)
            estatisticas['vagas_salvas'] += 1
            
            # Salva arquivo
            with open(os.path.join(BASE_DIR, 'vagas_salvas.json'), 'w', encoding='utf-8') as f:
                json.dump(vagas_salvas, f, ensure_ascii=False, indent=2)
            
            # Atualiza estatísticas
            salvar_estatisticas()
        
        return jsonify({
            'success': True,
            'message': 'Vaga salva com sucesso'
        })
        
    except Exception as e:
        logger.error(f"Erro ao salvar vaga: {e}")
        return jsonify({'error': f'Erro interno: {str(e)}'}), 500

@app.route('/api/limpar-resultados', methods=['POST'])
def limpar_resultados():
    """Força a limpeza de arquivos de resultados"""
    try:
        cleanup_old_result_files()
        return jsonify({
            'success': True,
            'message': 'Limpeza de arquivos realizada com sucesso'
        })
    except Exception as e:
        logger.error(f"Erro ao limpar resultados: {e}")
        return jsonify({'error': f'Erro interno: {str(e)}'}), 500

@app.route('/api/exportar-vagas', methods=['POST'])
def exportar_vagas():
    """Exporta vagas para Excel"""
    try:
        data = request.get_json()
        formato = data.get('formato', 'json')
        
        if not resultados_cache:
            return jsonify({'error': 'Nenhum resultado para exportar'}), 400
        
        # Pega o resultado mais recente
        ultimo_resultado = list(resultados_cache.values())[-1]
        vagas = ultimo_resultado['vagas']
        
        if formato == 'excel':
            import pandas as pd
            
            # Converte para DataFrame
            df = pd.DataFrame(vagas)
            
            # Nome do arquivo
            filename = f"vagas_buscajob_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
            fullpath = os.path.join(BASE_DIR, filename)
            
            # Salva Excel
            df.to_excel(fullpath, index=False, engine='openpyxl')
            
            return jsonify({
                'success': True,
                'filename': filename,
                'message': f'Arquivo {filename} criado com sucesso'
            })
        
        else:  # JSON
            filename = f"vagas_buscajob_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            fullpath = os.path.join(BASE_DIR, filename)
            
            with open(fullpath, 'w', encoding='utf-8') as f:
                json.dump(ultimo_resultado, f, ensure_ascii=False, indent=2)
            
            return jsonify({
                'success': True,
                'filename': filename,
                'message': f'Arquivo {filename} criado com sucesso'
            })
        
    except Exception as e:
        logger.error(f"Erro ao exportar vagas: {e}")
        return jsonify({'error': f'Erro interno: {str(e)}'}), 500

# Limpeza de arquivos antigos (Dia-1 e anteriores)

def cleanup_old_result_files():
    """Mantém apenas os 2 arquivos de resultados mais recentes"""
    try:
        base_dir = BASE_DIR
        patterns = ('resultados_', 'relatorio_fixo_')
        
        # Lista todos os arquivos que correspondem aos padrões
        files = []
        for name in os.listdir(base_dir):
            if any(name.startswith(p) and name.endswith('.json') for p in patterns):
                full_path = os.path.join(base_dir, name)
                files.append((full_path, os.path.getmtime(full_path)))
        
        # Ordena por data de modificação (mais recentes primeiro)
        files.sort(key=lambda x: x[1], reverse=True)
        
        # Mantém apenas os 2 mais recentes
        files_to_remove = files[2:]
        removed = []
        
        for file_path, _ in files_to_remove:
            try:
                os.remove(file_path)
                removed.append(os.path.basename(file_path))
            except Exception as e:
                logger.warning(f"Erro ao remover arquivo antigo {file_path}: {e}")
                
        if removed:
            logger.info(f"Arquivos antigos removidos (limpeza estrita): {removed}")
            
    except Exception as e:
        logger.error(f"Erro na limpeza de arquivos: {e}")

@app.route('/api/relatorio-fixo', methods=['GET'])
def relatorio_fixo():
    try:
        cleanup_old_result_files()
        cargos = [
            'Analista de Sistemas',
            'Analista de Negocios',
            'Analista de Requisitos',
            'Desenvolvedor',
            'Gerente de TI',
            'Coordenador de TI',
        ]
        cidades = [
            'Joinville',
            'São Paulo',
            'Curitiba',
            'Porto Alegre',
            'Belo Horizonte',
            'Florianópolis',
            'Santa Catarina',
        ]
        # Obtém lista de sites do scraper, com fallback
        try:
            sites = list(getattr(scraper, 'scrapers', {}).keys())
            if not sites:
                sites = [
                    'linkedin','indeed','catho','infojobs','trampos','gupy','kenoby','empregos','glassdoor','stackoverflow','vagas'
                ]
        except Exception:
            sites = [
                'linkedin','indeed','catho','infojobs','trampos','gupy','kenoby','empregos','glassdoor','stackoverflow','vagas'
            ]

        all_vagas = []
        total_consultas = 0

        for cargo in cargos:
            for cidade in cidades:
                criterios = {
                    'cargo': cargo,
                    'localizacao': cidade,
                    'sites': sites,
                    'tipos_contratacao': ['CLT', 'PJ']
                }
                resultados = scraper.buscar_vagas(criterios)
                total_consultas += 1
        for v in resultados:
            vaga_dict = {
                'id': f"vaga_{hash(getattr(v, 'titulo', '') + getattr(v, 'empresa', ''))}",
                'titulo': getattr(v, 'titulo', ''),
                'empresa': getattr(v, 'empresa', ''),
                'localizacao': getattr(v, 'localizacao', cidade),
                'salario': getattr(v, 'salario', ''),
                'descricao': getattr(v, 'descricao', ''),
                'dataPublicacao': getattr(v, 'data_publicacao', ''),
                'site': getattr(v, 'site_origem', ''),
                'url': getattr(v, 'url', ''),
                'tipo': getattr(v, 'tipo_contrato', ''),
                'nivel': getattr(v, 'nivel_experiencia', ''),
                'modalidade': getattr(v, 'modalidade', '')
            }
            all_vagas.append(vaga_dict)

        # Deduplicação básica por (titulo, empresa, site, url)
        seen = set()
        dedup = []
        for v in all_vagas:
            key = (v.get('titulo'), v.get('empresa'), v.get('site'), v.get('url'))
            if key in seen:
                continue
            seen.add(key)
            dedup.append(v)

        # Salvar arquivo JSON
        filename = f"relatorio_fixo_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        fullpath = os.path.join(BASE_DIR, filename)
        payload = {
            'timestamp': datetime.now().isoformat(),
            'cargos': cargos,
            'cidades': cidades,
            'sites': sites,
            'total_consultas': total_consultas,
            'total_vagas': len(dedup),
            'vagas': dedup,
        }
        with open(fullpath, 'w', encoding='utf-8') as f:
            json.dump(payload, f, ensure_ascii=False, indent=2)

        # Enviar e-mail opcionalmente
        email_sent = False
        email_error = None
        if os.environ.get('EMAIL_ENABLED', '').lower() in ('1', 'true', 'yes'):
            try:
                send_email_with_attachment(
                    subject=f"BuscaJob Relatório Fixo - {datetime.now().strftime('%Y-%m-%d')}",
                    body=(
                        f"Relatório gerado em {payload['timestamp']}\n"
                        f"Cargos: {', '.join(cargos)}\n"
                        f"Cidades: {', '.join(cidades)}\n"
                        f"Total de vagas: {len(dedup)}\n"
                    ),
                    file_path=fullpath,
                )
                email_sent = True
            except Exception as e:
                email_error = str(e)
                logger.error(f"Falha ao enviar e-mail: {email_error}")

        resp = {
            'success': True,
            'arquivo': filename,
            'total': len(dedup),
            'email_enviado': email_sent,
            'email_erro': email_error,
            'vagas': dedup,
        }
        return jsonify(resp)

    except Exception as e:
        logger.exception("Erro ao gerar relatório fixo")
        return jsonify({'error': f'Erro interno: {str(e)}'}), 500

@app.route('/api/sites', methods=['GET'])
def listar_sites():
    """Lista os sites suportados pelo scraper."""
    try:
        sites = list(getattr(scraper, 'scrapers', {}).keys())
        if not sites:
            sites = [
                'linkedin','indeed','catho','infojobs','trampos','gupy','kenoby','empregos','glassdoor','stackoverflow','vagas'
            ]
        return jsonify({'sites': sites, 'total': len(sites)})
    except Exception:
        logger.exception("Erro ao listar sites")
        return jsonify({'error': 'Falha ao listar sites'}), 500

def salvar_resultados_arquivo(vagas, criterios):
    """Salva resultados em arquivo JSON"""
    try:
        dados = {
            'timestamp': datetime.now().isoformat(),
            'criterios': criterios,
            'total_vagas': len(vagas),
            'vagas': vagas
        }
        
        filename = f"resultados_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        fullpath = os.path.join(BASE_DIR, filename)
        
        with open(fullpath, 'w', encoding='utf-8') as f:
            json.dump(dados, f, ensure_ascii=False, indent=2)
        
        logger.info(f"Resultados salvos em {filename}")
        
    except Exception as e:
        logger.error(f"Erro ao salvar resultados: {e}")

def salvar_estatisticas():
    """Salva estatísticas em arquivo"""
    try:
        with open(os.path.join(BASE_DIR, 'estatisticas.json'), 'w', encoding='utf-8') as f:
            json.dump(estatisticas, f, ensure_ascii=False, indent=2)
    except Exception as e:
        logger.error(f"Erro ao salvar estatísticas: {e}")

def busca_agendada():
    """Executa busca agendada"""
    logger.info("Executando busca agendada...")
    
    # Carrega última configuração salva
    if configuracoes_salvas:
        ultima_config = list(configuracoes_salvas.values())[-1]['config']
        
        try:
            vagas = scraper.buscar_vagas(ultima_config)
            logger.info(f"Busca agendada concluída: {len(vagas)} vagas encontradas")
            
            # Salva resultados
            vagas_dict = []
            for vaga in vagas:
                vaga_dict = {
                    'titulo': vaga.titulo,
                    'empresa': vaga.empresa,
                    'localizacao': vaga.localizacao,
                    'salario': vaga.salario,
                    'site': vaga.site_origem
                }
                vagas_dict.append(vaga_dict)
            
            salvar_resultados_arquivo(vagas_dict, ultima_config)
            
        except Exception as e:
            logger.error(f"Erro na busca agendada: {e}")

def executar_agendador():
    """Executa o agendador em thread separada"""
    while True:
        schedule.run_pending()
        time.sleep(60)  # Verifica a cada minuto

# Configura agendamentos
schedule.every().day.at("09:00").do(busca_agendada)
schedule.every().day.at("18:00").do(busca_agendada)

# Inicia thread do agendador
agendador_thread = threading.Thread(target=executar_agendador, daemon=True)
agendador_thread.start()

# Nova rota de saúde para monitoramento simples
@app.route('/api/health', methods=['GET'])
def health():
    return jsonify({'status': 'ok', 'time': datetime.now().isoformat()})

if __name__ == '__main__':
    print("🚀 Iniciando BuscaJob API Server...")
    print("📱 Interface disponível em: http://localhost:5000")
    print("🔍 API endpoints disponíveis em: http://localhost:5000/api/")
    
    # Carrega dados existentes
    if os.path.exists(os.path.join(BASE_DIR, 'estatisticas.json')):
        try:
            with open(os.path.join(BASE_DIR, 'estatisticas.json'), 'r', encoding='utf-8') as f:
                estatisticas.update(json.load(f))
        except:
            pass
    
    app.run(debug=True, host='0.0.0.0', port=5000)

