import csv
import io
import logging
import threading
from datetime import date
from pathlib import Path

from . import db

PASTA = Path(__file__).resolve().parent.parent / 'relatorios'

log = logging.getLogger(__name__)
_trava = threading.Lock()


def fechar_dias_anteriores():
    """Gera o relatório definitivo de cada dia que já passou e ainda não foi fechado."""
    hoje = date.today().isoformat()
    with _trava:
        for data in db.dias_sem_relatorio(antes_de=hoje):
            gerar_arquivo(data)
            db.marcar_relatorio_gerado(data)
    return hoje


def abrir_dia():
    """Registra hoje como dia de funcionamento (só acontece com a contagem ligada)."""
    hoje = fechar_dias_anteriores()
    if not db.dia_existe(hoje):
        db.criar_dia(hoje)
        log.info('Dia %s iniciado', formatar_data(hoje))
    return hoje


def formatar_data(data):
    return date.fromisoformat(data).strftime('%d/%m/%Y')


def escrever_csv(arquivo, data):
    escritor = csv.writer(arquivo, delimiter=';')
    escritor.writerow(['Relatório de visitantes', formatar_data(data)])
    escritor.writerow([])
    escritor.writerow(['Hora', 'Visitantes'])
    for hora, total in db.entradas_por_hora(data):
        escritor.writerow([f'{hora}:00', total])
    escritor.writerow([])
    escritor.writerow(['Total do dia', db.total_do_dia(data)])
    escritor.writerow(['Acumulado até o dia', db.acumulado_ate(data)])


def escrever_csv_completo(arquivo):
    escritor = csv.writer(arquivo, delimiter=';')
    escritor.writerow(['Relatório de visitantes - todos os dias'])
    escritor.writerow([])
    escritor.writerow(['Data', 'Visitantes'])
    total = 0
    for dia in db.historico():
        escritor.writerow([formatar_data(dia['data']), dia['total']])
        total += dia['total']
    escritor.writerow([])
    escritor.writerow(['Total de visitantes', total])


def gerar_arquivo(data):
    PASTA.mkdir(exist_ok=True)
    caminho = PASTA / f'relatorio_{data}.csv'
    # utf-8-sig grava o BOM para o Excel abrir os acentos corretamente
    with open(caminho, 'w', newline='', encoding='utf-8-sig') as arquivo:
        escrever_csv(arquivo, data)
    log.info('Relatório de %s gerado em %s', formatar_data(data), caminho)
    return caminho


def _em_texto(escrever, *argumentos):
    arquivo = io.StringIO(newline='')
    escrever(arquivo, *argumentos)
    return '﻿' + arquivo.getvalue()


def csv_em_texto(data):
    return _em_texto(escrever_csv, data)


def csv_completo_em_texto():
    return _em_texto(escrever_csv_completo)
