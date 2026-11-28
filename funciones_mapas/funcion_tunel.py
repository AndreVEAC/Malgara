import pygame
from reloj_juego import ahora_ms

import sistema_dialogo as dialogo
import sistema_guardado as guardado
import sistema_mapa as mapa
from configuracion import TAMANO_CASILLA as T
from funciones_mapas.escena_morales import Director, Recorrido, mirar, ruta_a
from mapas import tunel


CENTRAR_FONDO = True
director = None


def iniciar():
    global director

    dialogo.cargar_json("datos/tunel.json")
    director = None
    if guardado.cargando:
        _iniciar_exploracion()
        return

    mapa.jugador_bloqueado = True
    director = Director(_llegada())


def actualizar():
    # Los autoguardados anteriores tenían el evento en el suelo.
    x, y = tunel.FRENTE_A_PUERTA
    if mapa.matriz_activa[y][x] == 2:
        mapa.matriz_activa[y][x] = 0
        x, y = tunel.PUERTA_HIERRO
        mapa.matriz_activa[y][x] = 2

    if director is not None:
        director.actualizar()


def recortar_linternas(capa, camara_x, camara_y):
    mascara = pygame.Surface(capa.get_size(), pygame.SRCALPHA)
    blanco = (255, 255, 255, 255)
    mascara.fill(blanco, (-camara_x, T+4-camara_y, 20*T, T+4))
    for x in tunel.RAMAS:
        mascara.fill(blanco, (x*T+2-camara_x, 2*T-camara_y, T-4, 2*T))
    capa.blit(mascara, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)


def al_iniciar_dialogo(evento):
    global director

    if evento == "evento_puerta_hierro":
        x, y = tunel.PUERTA_HIERRO
        mapa.matriz_activa[y][x] = 1
        mapa.jugador_bloqueado = True
        for nombre in ("morales", "lucas"):
            mapa.npcs_activos[nombre]["comportamiento"] = "estatico"
        director = Director(_examinar_puerta())


def _llegada():
    yield "dialogo", "evento_vigilancia_tunel"
    yield "hacer", _guardar_entrada


def _guardar_entrada():
    _iniciar_exploracion()
    # El guardado se procesa al inicio del siguiente fotograma.
    mapa.tiempo_ultimo_paso_mateo = ahora_ms()
    guardado.solicitar("automatico", mapa_destino="tunel")


def _iniciar_exploracion():
    for nombre in ("morales", "lucas"):
        mapa.npcs_activos[nombre]["comportamiento"] = "sigue_jugador"
    mapa.jugador_bloqueado = False


def _examinar_puerta():
    x, y = tunel.FRENTE_A_PUERTA
    yield "mover", [Recorrido("mateo", [(x+1, y)])]
    morales = mapa.npcs_activos["morales"]
    ruta = ruta_a((morales["x"], morales["y"]), (x, y))
    yield "mover", [Recorrido("morales", ruta)]
    yield "hacer", lambda: mirar("morales", "arriba")
    yield "pausa", 2000
    yield "dialogo", "evento_necesitan_llave"
    yield "hacer", _habilitar_regreso


def _habilitar_regreso():
    x, y = tunel.SALIDA
    mapa.matriz_activa[y][x] = 97
    _iniciar_exploracion()
