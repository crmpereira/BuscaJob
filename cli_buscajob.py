#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
CLI BuscaJob
Ferramenta de linha de comando para consumir a API do BuscaJob sem frontend HTML.

Uso:
  - Carregar último resultado salvo:
      python cli_buscajob.py --ultimo

  - Buscar vagas por critérios:
      python cli_buscajob.py --cargo "Desenvolvedor" --localizacao "Joinville" --sites trampos,infojobs --tipos CLT --abrir primeiro

  - Exibir JSON bruto:
      python cli_buscajob.py --ultimo --json

Configure a URL base via env BUSCAJOB_URL se necessário (default http://localhost:5000).
"""

import os
import sys
import json
import argparse
import webbrowser
from typing import List, Dict

import requests

BASE_URL = os.environ.get('BUSCAJOB_URL', 'http://localhost:5000')


def _print_vagas(vagas: List[Dict]):
    if not vagas:
        print("Nenhuma vaga encontrada.")
        return
    for i, v in enumerate(vagas, 1):
        site = v.get('site', '')
        titulo = v.get('titulo', '')
        empresa = v.get('empresa', '')
        localizacao = v.get('localizacao', '')
        url = v.get('url', '')
        print(f"[{i}] [{site}] {titulo} — {empresa} — {localizacao}")
        print(f"    URL: {url}")


def _abrir_links(vagas: List[Dict], modo: str):
    if modo not in ('primeiro', 'todos'):
        return
    if not vagas:
        return
    if modo == 'primeiro':
        url = vagas[0].get('url')
        if url:
            webbrowser.open(url)
            print(f"Abrindo: {url}")
    else:
        for v in vagas:
            url = v.get('url')
            if url:
                webbrowser.open(url)
                print(f"Abrindo: {url}")


def carregar_ultimo(json_bruto: bool = False, abrir: str = None):
    url = f"{BASE_URL}/api/ultimo-resultado"
    resp = requests.get(url, timeout=30)
    resp.raise_for_status()
    data = resp.json()
    if json_bruto:
        print(json.dumps(data, ensure_ascii=False, indent=2))
        return
    if not data.get('success'):
        print(f"Erro: {data.get('error', 'Falha ao carregar último resultado')}")
        sys.exit(1)
    print(f"Arquivo: {data.get('arquivo')} | Total: {data.get('total')}")
    _print_vagas(data.get('vagas', []))
    _abrir_links(data.get('vagas', []), abrir)


def buscar(args, json_bruto: bool = False, abrir: str = None):
    url = f"{BASE_URL}/api/buscar-vagas"
    payload: Dict = {
        'cargo': args.cargo,
        'localizacao': args.localizacao,
        'sites': args.sites.split(',') if args.sites else [],
        'tipos_contratacao': args.tipos.split(',') if args.tipos else [],
        'palavras_chave': args.palavras or '',
    }
    if args.salario_minimo is not None:
        payload['salario_minimo'] = args.salario_minimo
    if args.salario_maximo is not None:
        payload['salario_maximo'] = args.salario_maximo

    headers = {'Content-Type': 'application/json'}
    resp = requests.post(url, headers=headers, data=json.dumps(payload, ensure_ascii=False).encode('utf-8'), timeout=60)
    resp.raise_for_status()
    data = resp.json()

    if json_bruto:
        print(json.dumps(data, ensure_ascii=False, indent=2))
        return

    if not data.get('success'):
        print(f"Erro: {data.get('error', 'Falha na busca')}")
        sys.exit(1)

    print(f"Busca concluída | Total: {data.get('total')}")
    _print_vagas(data.get('vagas', []))
    _abrir_links(data.get('vagas', []), abrir)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='CLI para BuscaJob (somente backend)')
    parser.add_argument('--ultimo', action='store_true', help='Carrega o último resultado salvo')
    parser.add_argument('--cargo', type=str, help='Cargo/Função (ex: Desenvolvedor)')
    parser.add_argument('--localizacao', type=str, help='Localização (ex: São Paulo, Remoto)')
    parser.add_argument('--sites', type=str, help='Sites (lista separada por vírgula)')
    parser.add_argument('--tipos', type=str, help='Tipos de contratação (ex: CLT,PJ)')
    parser.add_argument('--palavras', type=str, help='Palavras-chave (ex: Python, Django)')
    parser.add_argument('--salario-minimo', type=int, help='Salário mínimo (inteiro em BRL)')
    parser.add_argument('--salario-maximo', type=int, help='Salário máximo (inteiro em BRL)')
    parser.add_argument('--json', action='store_true', help='Exibe resultado em JSON bruto')
    parser.add_argument('--abrir', choices=['primeiro', 'todos'], help='Abre link(s) das vagas no navegador')

    args = parser.parse_args()

    try:
        if args.ultimo:
            carregar_ultimo(json_bruto=args.json, abrir=args.abrir)
        else:
            if not args.cargo:
                print('Erro: --cargo é obrigatório quando não se usa --ultimo')
                sys.exit(2)
            buscar(args, json_bruto=args.json, abrir=args.abrir)
    except requests.HTTPError as e:
        print(f"HTTP error: {e}")
        if e.response is not None:
            try:
                print(e.response.text)
            except Exception:
                pass
        sys.exit(1)
    except requests.RequestException as e:
        print(f"Erro de requisição: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"Erro: {e}")
        sys.exit(1)