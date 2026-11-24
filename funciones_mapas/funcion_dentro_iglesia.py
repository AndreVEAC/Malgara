import pygame

import sistema_dialogo as dialogo
import sistema_mapa as mapa
from funciones_mapas.escena_morales import Director, Recorrido, mirar, ruta_a, sonido
from mapas import dentro_iglesia as interior


MARCA_PUERTA = "dentro_iglesia:puerta_abierta"
director = None
luces = ()


def iniciar():
    global director, luces

    dialogo.cargar_json("datos/dentro_iglesia.json")
    if not luces:
        luz = pygame.image.load("recursos/sprites/efectos/luz_iglesia.png").convert_alpha()
        luces = (luz, pygame.transform.flip(luz, False, True))

    director = None
    if (mapa.mateo_x, mapa.mateo_y) == interior.REGRESO_TUNEL:
        mapa.eventos_completados.add(interior.MARCA_TUNEL_SUPERADO)
    if interior.MARCA_TUNEL_SUPERADO in mapa.eventos_completados:
        mapa.matriz_activa[0][1:3] = [1, 1]
        x, y = interior.PUERTA_PRINCIPAL
        mapa.matriz_activa[y][x] = 98
        for nombre in ("morales", "lucas"):
            mapa.npcs_activos[nombre]["comportamiento"] = "sigue_jugador"
        return
    if MARCA_PUERTA in mapa.eventos_completados:
        _habilitar_tunel()
        return

    mapa.jugador_bloqueado = True
    director = Director(_llegada())


def actualizar():
    if director is not None:
        director.actualizar()


def dibujar_efectos(pantalla, camara_x, camara_y):
    abajo, arriba = luces
    ancho, alto = mapa.fondo_actual.get_size()
    for x in (80, ancho-80):
        pantalla.blit(arriba, arriba.get_rect(midtop=(x-camara_x, -camara_y)))
        pantalla.blit(abajo, abajo.get_rect(midbottom=(x-camara_x, alto-camara_y)))


def al_iniciar_dialogo(evento):
    global director

    if evento == "evento_bano":
        mapa.jugador_bloqueado = True
        sonido("open_door")
        director = Director(_cerrar_bano())
    elif evento == "evento_puerta_izquierda":
        mapa.jugador_bloqueado = True
        mapa.npcs_activos["lucas"]["comportamiento"] = "estatico"
        director = Director(_abrir_tunel())


def _llegada():
    yield "dialogo", "evento_buscar_entrada"
    yield "hacer", _iniciar_exploracion


def _iniciar_exploracion():
    mapa.npcs_activos["lucas"]["comportamiento"] = "sigue_jugador"
    mapa.jugador_bloqueado = False


def _cerrar_bano():
    yield "hacer", lambda: sonido("close_door")
    yield "hacer", _iniciar_exploracion


def _caminar(nombre, destino):
    npc = mapa.npcs_activos[nombre]
    return Recorrido(nombre, ruta_a((npc["x"], npc["y"]), destino))


def _abrir_tunel():
    x, y = interior.PUERTA_TUNEL
    yield "mover", [_caminar("morales", (x+1, y+2))]
    yield "hacer", lambda: mirar("morales", "arriba")
    yield "dialogo", "evento_aparta_morales"
    yield "mover", [Recorrido("mateo", [(x+1, y+1)])]
    yield "mover", [_caminar("morales", (x, y+1))]
    yield "hacer", lambda: mirar("morales", "arriba")
    yield "hacer", lambda: sonido("cerrojo")
    yield "pausa", 2000
    yield "dialogo", "evento_bingo"
    yield "hacer", lambda: sonido("open_door")
    yield "mover", [_caminar("morales", interior.PUERTA_TUNEL)]
    yield "hacer", lambda: _ocultar("morales")
    yield "mover", [_caminar("lucas", interior.PUERTA_TUNEL)]
    yield "hacer", _habilitar_tunel


def _ocultar(nombre):
    mapa.npcs_activos[nombre]["visible"] = False


def _habilitar_tunel():
    mapa.eventos_completados.add(MARCA_PUERTA)
    mapa.matriz_activa[0][1:3] = [97, 97]
    for nombre in ("morales", "lucas"):
        _ocultar(nombre)
    mapa.jugador_bloqueado = False
