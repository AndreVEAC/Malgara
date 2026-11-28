"""Regreso a la casa roja. Se activa sólo después del encuentro con Morales."""
import pygame
from reloj_juego import ahora_ms
import sistema_mapa as mapa
import sistema_dialogo as dialogo
import sistema_escondites as escondites
from funciones_mapas.escena_morales import (
    Director, Recorrido, crear_npc, colocar, mirar, sonido, cargar_linternas,
    linterna, MARCA_REGRESO, MARCA_HOGAR)

activo = False
director = None
luces = None
ruta_loco = None
canal_puerta = None


def iniciar():
    global activo, director, luces, ruta_loco, canal_puerta
    activo = MARCA_REGRESO in mapa.eventos_completados
    if not activo: return False
    mapa.jugador_bloqueado = True
    escondites.escondido = False
    # Los vigilantes ordinarios quedan fuera de esta escena.
    for npc in mapa.npcs_activos.values():
        npc['visible'] = False
        npc['pausado'] = True
    colocar('mateo',18,18,'izq')
    crear_npc('lucas','lucas',17,18,'izq')
    crear_npc('morales','morales',19,18,'izq')
    crear_npc('vigilante_regreso','loco',-1,17,'der')
    luces = cargar_linternas()
    ruta_loco = Recorrido('vigilante_regreso',[(7,17)],650)
    canal_puerta = None
    dialogo.cargar_json('datos/pueblo_3_noche_1.json')
    director = Director(_secuencia())
    return True


def _abrir():
    global canal_puerta
    canal_puerta = sonido('open_door')


def _ocultar(nombre):
    if nombre == 'mateo': escondites.escondido = True
    else: mapa.npcs_activos[nombre]['visible'] = False


def _entrar():
    mapa.eventos_completados.discard(MARCA_REGRESO)
    mapa.eventos_completados.add(MARCA_HOGAR)
    mapa.cargar_nivel('hogar_noche_1',8,6)


def _secuencia():
    # Plano amplio, con el vigilante entrando lentamente desde la izquierda.
    yield 'pausa', 2300
    yield 'dialogo', 'evento_morales_regreso'
    yield 'hacer', _abrir
    yield 'mover', [Recorrido('morales',[(18,18),(18,17),(18,16)],125)]
    yield 'hacer', lambda: _ocultar('morales')
    yield 'mover', [Recorrido('mateo',[(18,17),(18,16)],125),
                    Recorrido('lucas',[(18,18),(18,17)],125,250)]
    yield 'hacer', lambda: _ocultar('mateo')
    yield 'mover', [Recorrido('lucas',[(18,16)],125)]
    yield 'hacer', lambda: _ocultar('lucas')
    yield 'hacer', _entrar


def actualizar():
    if not activo: return False
    if not mapa.transicion_activa and dialogo.obtener_evento_activo() is None:
        ruta_loco.actualizar(ahora_ms())
        director.actualizar()
    return True


def dibujar_efectos(pantalla, cx, cy):
    if activo and luces:
        linterna(pantalla,luces,'vigilante_regreso',cx,cy)
