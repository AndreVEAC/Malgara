import pygame

import sistema_dialogo as dialogo
import sistema_mapa as mapa
from mapas.prision_dia_2 import CENTRAR_FONDO, FILA_BARROTES, HUECO, ORIGEN_BARROTES
from mapas.habitaciones_dia_2 import ABRIR_PUERTA

barrotes = {}
abierta = False


def iniciar():
    global abierta
    dialogo.cargar_json()
    abierta = False
    if not barrotes:
        for estado, nombre in ((False, "cerrada"), (True, "abierta")):
            barrotes[estado] = pygame.image.load(
                f"recursos/sprites/objetos/carcel_{nombre}.png"
            ).convert_alpha()


def abrir():
    global abierta
    abierta = True
    mapa.matriz_activa[FILA_BARROTES][HUECO] = 0
    mapa._reproducir_sonido_portal(ABRIR_PUERTA)


def capa_profundidad(camara_x, camara_y):
    x, y = ORIGEN_BARROTES
    imagen = barrotes[abierta]
    return y + imagen.get_height(), imagen, x - camara_x, y - camara_y
