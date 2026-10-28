import json
import logging
import time
from datetime import date
from pathlib import Path

from flask import Flask, Response, abort, jsonify, request

from contador import db, relatorio
from contador.camera import Camera

RAIZ = Path(__file__).resolve().parent
CAMINHO_CONFIG = RAIZ / 'config.json'
config = json.loads(CAMINHO_CONFIG.read_text(encoding='utf-8'))

app = Flask(__name__, static_folder=str(RAIZ / 'web'), static_url_path='')
camera = Camera(config)


def salvar_config():
    CAMINHO_CONFIG.write_text(json.dumps(config, indent=2), encoding='utf-8')


def definir_contando(contando):
    camera.contando = contando
    # Guardado no banco para retomar a contagem se o PC reiniciar no meio do dia
    db.salvar_estado('contando', '1' if contando else '0')


def baixar_csv(conteudo, nome):
    return Response(
        conteudo,
        mimetype='text/csv; charset=utf-8',
        headers={'Content-Disposition': f'attachment; filename={nome}'},
    )


@app.get('/')
def telao():
    return app.send_static_file('index.html')


@app.get('/relatorio')
def pagina_relatorio():
    return app.send_static_file('relatorio.html')


@app.get('/camera')
def pagina_camera():
    return app.send_static_file('camera.html')


@app.get('/video')
def video():
    def quadros():
        while True:
            jpeg = camera.ultimo_quadro()
            if jpeg:
                yield b'--quadro\r\nContent-Type: image/jpeg\r\n\r\n' + jpeg + b'\r\n'
            time.sleep(0.1)

    return Response(quadros(), mimetype='multipart/x-mixed-replace; boundary=quadro')


@app.get('/api/contagem')
def api_contagem():
    if camera.contando:
        relatorio.abrir_dia()
    else:
        relatorio.fechar_dias_anteriores()
    return jsonify(**db.contagem_atual(), camera_ok=camera.ok, contando=camera.contando)


@app.post('/api/contagem/iniciar')
def api_iniciar():
    relatorio.abrir_dia()
    definir_contando(True)
    return api_contagem()


@app.post('/api/contagem/encerrar')
def api_encerrar():
    definir_contando(False)
    # Salva o relatório parcial de hoje; ele é refeito como definitivo quando o dia virar
    hoje = date.today().isoformat()
    if db.dia_existe(hoje):
        relatorio.gerar_arquivo(hoje)
    return api_contagem()


@app.get('/api/area')
def api_area():
    return jsonify(area=config['area'])


@app.post('/api/area')
def api_salvar_area():
    dados = request.get_json(silent=True) or {}
    try:
        x1, y1, x2, y2 = (float(valor) for valor in dados.get('area'))
    except (TypeError, ValueError):
        abort(400)
    if not (0 <= x1 < x2 <= 1 and 0 <= y1 < y2 <= 1):
        abort(400)
    config['area'] = [round(valor, 4) for valor in (x1, y1, x2, y2)]
    salvar_config()
    return jsonify(area=config['area'])


@app.get('/api/historico')
def api_historico():
    relatorio.fechar_dias_anteriores()
    return jsonify(db.historico())


@app.get('/api/relatorio/completo.csv')
def api_relatorio_completo_csv():
    return baixar_csv(relatorio.csv_completo_em_texto(), 'relatorio_completo.csv')


@app.get('/api/relatorio/<data>.csv')
def api_relatorio_csv(data):
    try:
        date.fromisoformat(data)
    except ValueError:
        abort(404)
    return baixar_csv(relatorio.csv_em_texto(data), f'relatorio_{data}.csv')


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s %(message)s')
    db.iniciar()
    relatorio.fechar_dias_anteriores()
    camera.contando = db.ler_estado('contando') == '1'
    camera.start()
    app.run(host='127.0.0.1', port=config['porta'], threaded=True)
