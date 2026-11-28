"""Guía de teclas para la intro y el prólogo."""
import pygame


DURACION_MS = 10_000
FUNDIDO_MS = 700
INTERVALO_TECLAS_MS = 140
TECLAS = (
    ("tecla_espacio", "interactuar", 26),
    ("tecla_flechas", "moverte", 38),
    ("tecla_shift", "correr", 26),
    ("tecla_f11_", "pantalla completa", 26),
)


class GuiaControles:
    def __init__(self):
        self.inicio = None
        self.tarjetas = []

    def preparar(self):
        fuente = pygame.font.Font("recursos/fuentes/VT323-Regular.ttf", 25)
        for tecla, accion, alto in TECLAS:
            imagen = pygame.image.load(f"recursos/sprites/objetos/{tecla}.png").convert_alpha()
            imagen = imagen.subsurface(imagen.get_bounding_rect())
            ancho = round(imagen.get_width() * alto / imagen.get_height())
            icono = pygame.transform.scale(imagen, (ancho, alto))
            texto = fuente.render(accion, True, (255, 242, 214))
            tarjeta = pygame.Surface((ancho + texto.get_width() + 32, 52), pygame.SRCALPHA)
            pygame.draw.rect(tarjeta, (24, 19, 21, 235), tarjeta.get_rect(), border_radius=6)
            pygame.draw.rect(tarjeta, (211, 170, 91), tarjeta.get_rect(), width=1, border_radius=6)
            tarjeta.blit(icono, (11, (52 - alto) // 2))
            tarjeta.blit(texto, (ancho + 21, (52 - texto.get_height()) // 2))
            self.tarjetas.append(tarjeta)

    def dibujar(self, pantalla, mapa_actual, alpha_transicion, *, puede_moverse):
        if mapa_actual not in ("intro", "prologo"):
            return
        ahora = pygame.time.get_ticks()
        if self.inicio is None:
            if not puede_moverse:
                return
            self.inicio = ahora
            self.preparar()
        transcurrido = ahora - self.inicio
        if transcurrido >= DURACION_MS:
            return

        separacion = 12
        ancho = sum(tarjeta.get_width() for tarjeta in self.tarjetas) + separacion * (len(self.tarjetas) - 1)
        x = (pantalla.get_width() - ancho) // 2
        salida = min(1, (DURACION_MS - transcurrido) / FUNDIDO_MS)
        visibilidad_mapa = (255 - alpha_transicion) / 255
        for indice, tarjeta in enumerate(self.tarjetas):
            entrada = (transcurrido - indice * INTERVALO_TECLAS_MS) / FUNDIDO_MS
            opacidad = round(255 * max(0, min(entrada, salida, visibilidad_mapa)))
            tarjeta.set_alpha(opacidad)
            pantalla.blit(tarjeta, (x, 15))
            x += tarjeta.get_width() + separacion
