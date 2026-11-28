import json
from pathlib import Path

import pygame

from configuracion import ALTO_PANTALLA, ANCHO_PANTALLA, FPS, TITULO_JUEGO


RAIZ = Path(__file__).resolve().parent.parent
FONDOS = (
    "fondo_pueblo_1_vacio.png",
    "fondo_pueblo_2_vacio.png",
    "fondo_pueblo_3_vacio.png",
    "fondo_iglesia_vacio.png",
    "fondo_casa_vacio.png",
    "fondo_tumbas.png",
)
FUNDIDO = 0.9
DURACION_FONDO = 5.0
DURACION_TUMBAS = DURACION_FONDO + 2.0


def envolver(texto, fuente, ancho):
    renglon = ""
    for palabra in texto.split():
        candidato = f"{renglon} {palabra}".strip()
        if renglon and fuente.size(candidato)[0] > ancho:
            yield renglon
            renglon = palabra
        else:
            renglon = candidato
    if renglon:
        yield renglon


class EpilogoLaboratorio:
    """Secuencia a pantalla completa para iniciar después del rescate policial."""

    def __init__(self, pantalla, *, eventos=None, fondos=FONDOS, titulo="Final: La última cura"):
        self.ancho, self.alto = pantalla.get_size()
        fuente = pygame.font.Font(None, round(self.alto * 0.043))
        fuente_fin = pygame.font.Font(None, round(self.alto * 0.11))
        if eventos is None:
            guion = json.loads((RAIZ / "datos" / "epilogo_laboratorio.json").read_text(encoding="utf-8"))
            eventos = guion["eventos"].values()
        self.nombres_fondos = fondos
        self.tarjetas = []
        for nodo in eventos:
            textos = [
                linea["texto"] if linea["hablante"] in ("", "Narración")
                else f'{linea["hablante"]}: {linea["texto"]}'
                for linea in nodo["lineas"]
            ]
            renglones = [
                [
                    fuente.render(renglon, True, (235, 235, 235))
                    for renglon in envolver(texto, fuente, self.ancho * 0.8)
                ]
                for texto in textos
            ]
            duracion = max(4.0, sum(len(texto.split()) for texto in textos) / 3.0)
            self.tarjetas.append((renglones, duracion + 2 * FUNDIDO))

        self.fondos = []
        for nombre in fondos:
            fondo = pygame.image.load(str(RAIZ / "recursos" / "sprites" / "fondos" / nombre))
            escala = max(self.ancho / fondo.get_width(), self.alto / fondo.get_height()) * 1.06
            tamano = round(fondo.get_width() * escala), round(fondo.get_height() * escala)
            self.fondos.append(pygame.transform.smoothscale(fondo.convert(), tamano))

        self.interlineado = fuente.get_linesize()
        self.fin = fuente_fin.render(titulo, True, (235, 235, 235))
        self.negro = pygame.Surface(pantalla.get_size())
        self.indice = 0
        self.transcurrido = 0.0

    @property
    def terminado(self):
        return (
            self.indice == len(self.tarjetas) + len(self.fondos)
            and self.transcurrido >= FUNDIDO
        )

    def actualizar_y_dibujar(self, pantalla, segundos):
        self.transcurrido += segundos
        total_tarjetas = len(self.tarjetas)
        total_escenas = total_tarjetas + len(self.fondos)
        while self.indice < total_escenas:
            if self.indice < total_tarjetas:
                duracion = self.tarjetas[self.indice][1]
            else:
                nombre_fondo = self.nombres_fondos[self.indice - total_tarjetas]
                duracion = DURACION_TUMBAS if nombre_fondo == "fondo_tumbas.png" else DURACION_FONDO
            if self.transcurrido < duracion:
                break
            self.transcurrido -= duracion
            self.indice += 1

        pantalla.fill((0, 0, 0))
        if self.indice == total_escenas:
            pantalla.blit(self.fin, self.fin.get_rect(center=pantalla.get_rect().center))
            visibilidad = min(1.0, self.transcurrido / FUNDIDO)
        elif self.indice < total_tarjetas:
            bloques, duracion = self.tarjetas[self.indice]
            separacion = self.interlineado // 2
            alto_texto = sum(len(bloque) for bloque in bloques) * self.interlineado
            alto_texto += (len(bloques) - 1) * separacion
            y = (self.alto - alto_texto) // 2
            for bloque in bloques:
                for renglon in bloque:
                    pantalla.blit(renglon, ((self.ancho - renglon.get_width()) // 2, y))
                    y += self.interlineado
                y += separacion
            visibilidad = self._visibilidad(duracion)
        else:
            fondo = self.fondos[self.indice - total_tarjetas]
            progreso = self.transcurrido / duracion
            x = (self.ancho - fondo.get_width()) // 2
            # Recorrer la parte central de la imagen, incluso en fondos verticales.
            y = round((self.alto - fondo.get_height()) * (0.35 + 0.30 * progreso))
            pantalla.blit(fondo, (x, y))
            visibilidad = self._visibilidad(duracion)

        self.negro.set_alpha(round(255 * (1.0 - visibilidad)))
        pantalla.blit(self.negro, (0, 0))

    def _visibilidad(self, duracion):
        return min(1.0, self.transcurrido / FUNDIDO, (duracion - self.transcurrido) / FUNDIDO)


def previsualizar():
    pygame.init()
    try:
        pantalla = pygame.display.set_mode((ANCHO_PANTALLA, ALTO_PANTALLA))
        pygame.display.set_caption(f"{TITULO_JUEGO} — Epílogo del laboratorio")
        epilogo = EpilogoLaboratorio(pantalla)
        reloj = pygame.time.Clock()
        while True:
            segundos = reloj.tick(FPS) / 1000
            for evento in pygame.event.get():
                if evento.type == pygame.QUIT:
                    return
                if evento.type == pygame.KEYDOWN and evento.key == pygame.K_ESCAPE:
                    return
            epilogo.actualizar_y_dibujar(pantalla, segundos)
            pygame.display.flip()
    finally:
        pygame.quit()


if __name__ == "__main__":
    previsualizar()
