import logging
import threading
import time

import cv2

from . import db, relatorio

log = logging.getLogger(__name__)

PESSOA = 0                # classe "person" do modelo COCO
ESQUECER_APOS_S = 5       # some da imagem por mais que isso -> descarta o rastro
TENTAR_DE_NOVO_S = 5      # espera para reabrir a câmera quando ela cai

VERDE = (0, 200, 0)
VERMELHO = (0, 0, 255)


def dentro_da_area(area, ponto):
    x1, y1, x2, y2 = area
    return x1 <= ponto[0] <= x2 and y1 <= ponto[1] <= y2


class Camera(threading.Thread):
    def __init__(self, config):
        super().__init__(daemon=True, name='camera')
        self.config = config
        self.ok = False
        self.contando = False
        self.visitantes_na_sessao = 0
        self._jpeg = None
        self._trava = threading.Lock()

    def ultimo_quadro(self):
        with self._trava:
            return self._jpeg

    def run(self):
        from ultralytics import YOLO

        modelo = YOLO(self.config['modelo'])
        indice = self.config['camera_indice']
        while True:
            captura = cv2.VideoCapture(indice, cv2.CAP_DSHOW)
            if captura.isOpened():
                log.info('Câmera %s aberta', indice)
                try:
                    self._processar(captura, modelo)
                except Exception:
                    log.exception('Erro no processamento da câmera')
            else:
                log.warning('Não foi possível abrir a câmera %s', indice)
            captura.release()
            self.ok = False
            time.sleep(TENTAR_DE_NOVO_S)

    def _processar(self, captura, modelo):
        entrou_em = {}    # pessoa -> momento em que entrou na área
        visto_em = {}
        contados = set()

        while True:
            lido, quadro = captura.read()
            if not lido:
                log.warning('Câmera parou de enviar imagem')
                return
            self.ok = True

            altura, largura = quadro.shape[:2]
            x1, y1, x2, y2 = self.config['area']
            area = (x1 * largura, y1 * altura, x2 * largura, y2 * altura)

            # Parado: só mostra a imagem (para desenhar a área), sem detectar nem contar
            if not self.contando:
                entrou_em.clear()
                visto_em.clear()
                contados.clear()
                self._publicar(quadro, area, 'CONTAGEM PARADA', VERMELHO)
                continue

            resultado = modelo.track(
                quadro,
                persist=True,
                classes=[PESSOA],
                conf=self.config['confianca_minima'],
                tracker='bytetrack.yaml',
                verbose=False,
            )[0]

            agora = time.monotonic()
            if resultado.boxes.id is not None:
                caixas = resultado.boxes.xyxy.tolist()
                ids = resultado.boxes.id.int().tolist()
                for (bx1, by1, bx2, by2), pessoa in zip(caixas, ids):
                    visto_em[pessoa] = agora
                    if not dentro_da_area(area, ((bx1 + bx2) / 2, (by1 + by2) / 2)):
                        entrou_em.pop(pessoa, None)
                        continue
                    entrou_em.setdefault(pessoa, agora)
                    if pessoa not in contados and agora - entrou_em[pessoa] >= self.config['tempo_minimo_s']:
                        relatorio.abrir_dia()
                        db.registrar_entrada()
                        contados.add(pessoa)
                        self.visitantes_na_sessao += 1
                        log.info('Visitante registrado (pessoa %s)', pessoa)

            for pessoa in [p for p, momento in visto_em.items() if agora - momento > ESQUECER_APOS_S]:
                del visto_em[pessoa]
                entrou_em.pop(pessoa, None)
                contados.discard(pessoa)

            self._publicar(
                resultado.plot(), area,
                f'CONTANDO - visitantes nesta sessao: {self.visitantes_na_sessao}', VERDE,
            )

    def _publicar(self, imagem, area, texto, cor):
        x1, y1, x2, y2 = map(int, area)
        cv2.rectangle(imagem, (x1, y1), (x2, y2), cor, 3)
        cv2.putText(imagem, 'AREA DE CONTAGEM', (x1 + 8, y1 + 28), cv2.FONT_HERSHEY_SIMPLEX, 0.3, cor, 2)
        cv2.putText(imagem, texto, (10, imagem.shape[0] - 15), cv2.FONT_HERSHEY_SIMPLEX, 0.3, cor, 2)

        codificado, jpeg = cv2.imencode('.jpg', imagem)
        if codificado:
            with self._trava:
                self._jpeg = jpeg.tobytes()
