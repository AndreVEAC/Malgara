"""Postes nocturnos con la misma huella de detección que en la primera noche."""
import pygame

import sistema_dialogo as dialogo
import sistema_mapa as mapa
import sistema_vigilancia as vigilancia
from configuracion import TAMANO_CASILLA as T

imagen = None
zonas = []


def iniciar():
    global imagen, zonas
    dialogo.cargar_json()
    if imagen is None:
        imagen = pygame.image.load("recursos/sprites/efectos/luz_2.png").convert_alpha()
        imagen = pygame.transform.scale(imagen, (160, 160))
        imagen.set_alpha(140)
    zonas = [imagen.get_rect(center=((x + .5) * T, (y - 2.5) * T))
             for y, fila in enumerate(mapa.matriz_activa)
             for x, celda in enumerate(fila) if celda == 20]


def obtener_zonas_iluminadas():
    return zonas


def dibujar_efectos(pantalla, camara_x, camara_y):
    capa = pygame.Surface(pantalla.get_size(), pygame.SRCALPHA)
    for zona in zonas:
        capa.blit(imagen, zona.move(-camara_x, -camara_y))
    vigilancia._ocultar_luz_en_copas(capa, mapa, camara_x, camara_y)
    pantalla.blit(capa, (0, 0))
