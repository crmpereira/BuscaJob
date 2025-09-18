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

@app.route('/')
def index():
    """Serve a página principal"""
    return send_from_directory('.', 'index.html')

@app.route('/<path:filename>')
def serve_static(filename):
    """Serve arquivos estáticos"""
    return send_from_directory('.', filename)

@app.route('/api/buscar-vagas', methods=['POST'])
def buscar_vagas():
    """Endpoint para buscar vagas"""
    try:
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
                'nivel': getattr(vaga, 'nivel_experiencia', '')
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
        with open('configuracoes.json', 'w', encoding='utf-8') as f:
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
        if os.path.exists('configuracoes.json'):
            with open('configuracoes.json', 'r', encoding='utf-8') as f:
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
        if os.path.exists('estatisticas.json'):
            with open('estatisticas.json', 'r', encoding='utf-8') as f:
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
        if os.path.exists('vagas_salvas.json'):
            with open('vagas_salvas.json', 'r', encoding='utf-8') as f:
                vagas_salvas = json.load(f)
        
        # Verifica se já foi salva
        if vaga_id not in vagas_salvas:
            vagas_salvas.append(vaga_id)
            estatisticas['vagas_salvas'] += 1
            
            # Salva arquivo
            with open('vagas_salvas.json', 'w', encoding='utf-8') as f:
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
            
            # Salva Excel
            df.to_excel(filename, index=False, engine='openpyxl')
            
            return jsonify({
                'success': True,
                'filename': filename,
                'message': f'Arquivo {filename} criado com sucesso'
            })
        
        else:  # JSON
            filename = f"vagas_buscajob_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(ultimo_resultado, f, ensure_ascii=False, indent=2)
            
            return jsonify({
                'success': True,
                'filename': filename,
                'message': f'Arquivo {filename} criado com sucesso'
            })
        
    except Exception as e:
        logger.error(f"Erro ao exportar vagas: {e}")
        return jsonify({'error': f'Erro interno: {str(e)}'}), 500

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
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(dados, f, ensure_ascii=False, indent=2)
        
        logger.info(f"Resultados salvos em {filename}")
        
    except Exception as e:
        logger.error(f"Erro ao salvar resultados: {e}")

def salvar_estatisticas():
    """Salva estatísticas em arquivo"""
    try:
        with open('estatisticas.json', 'w', encoding='utf-8') as f:
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

if __name__ == '__main__':
    print("🚀 Iniciando BuscaJob API Server...")
    print("📱 Interface disponível em: http://localhost:5000")
    print("🔍 API endpoints disponíveis em: http://localhost:5000/api/")
    
    # Carrega dados existentes
    if os.path.exists('estatisticas.json'):
        try:
            with open('estatisticas.json', 'r', encoding='utf-8') as f:
                estatisticas.update(json.load(f))
        except:
            pass
    
    app.run(debug=True, host='0.0.0.0', port=5000)