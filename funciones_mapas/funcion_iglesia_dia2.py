import pygame
from reloj_juego import ahora_ms

import sistema_dialogo as dialogo
import sistema_mapa as mapa
from estado import BUSQUEDA_DIA_2
from funciones_mapas.escena_morales import Director, Recorrido, colocar, mirar, ruta_a, sonido
from mapas import iglesia_dia2 as iglesia
from mapas.dentro_iglesia import MARCA_TUNEL_SUPERADO
from mapas.habitaciones_dia_2 import CERRAR_PUERTA


MARCA = "iglesia_dia2:llegada_completada"
MARCA_REUNION = "iglesia_dia2:reunion_completada"
MARCA_REGRESO = "iglesia_dia2:regreso_completado"
PASO_MS = 260
director = None
vieron_morales = False
en_borde = False
proximo_giro = 0
revision_oficina = -1


def iniciar():
    global director, vieron_morales, en_borde, proximo_giro

    dialogo.cargar_json("datos/iglesia_dia2.json")
    director = None
    vieron_morales = en_borde = False
    proximo_giro = ahora_ms() + 1300
    if {MARCA_TUNEL_SUPERADO, BUSQUEDA_DIA_2} & mapa.eventos_completados:
        for nombre, (x, y) in zip(iglesia.NINOS, iglesia.POSICIONES_NINOS):
            mapa.npcs_activos[nombre]["visible"] = False
            mapa.matriz_activa[y][x] = 0
        x, y = iglesia.ESCONDITE_MORALES
        mapa.matriz_activa[y][x] = 0
        if BUSQUEDA_DIA_2 in mapa.eventos_completados:
            _habilitar_busqueda()
        elif MARCA_REGRESO not in mapa.eventos_completados:
            _iniciar_regreso()
        else:
            colocar("lucas", 12, 3, "izq")
            mapa.jugador_bloqueado = True
            director = Director(_separacion())
        return

    if MARCA in mapa.eventos_completados:
        mapa.npcs_activos["lucas"]["comportamiento"] = "sigue_jugador"
        return

    mapa.jugador_bloqueado = True
    mirar("mateo", "der")
    director = Director(_secuencia())


def actualizar():
    global vieron_morales, en_borde, proximo_giro

    if director is not None and not director.terminado:
        director.actualizar()
        return
    if mapa.transicion_activa or dialogo.obtener_evento_activo() is not None:
        return

    ahora = ahora_ms()
    morales = mapa.npcs_activos["morales"]
    if ahora >= proximo_giro:
        morales["direccion"] = "der" if morales["direccion"] == "izq" else "izq"
        proximo_giro = ahora + 1500

    if MARCA_REUNION in mapa.eventos_completados:
        return

    en_salida = (mapa.mateo_x, mapa.mateo_y) == (0, 7)
    if en_salida and not en_borde:
        en_borde = True
        dialogo.iniciar_dialogo("evento_no_regresar")
        return
    en_borde = en_salida

    if not vieron_morales and _distancia(iglesia.ESCONDITE_MORALES) <= 2:
        vieron_morales = True
        dialogo.iniciar_dialogo("evento_vista_morales")


def actualizar_estado(estado_jugador):
    global revision_oficina
    if revision_oficina != mapa.revision_nivel:
        revision_oficina = mapa.revision_nivel
        # Un guardado anterior puede restaurar la matriz sin la nueva fachada.
        for x, y in iglesia.FACHADA_OFICINA:
            mapa.matriz_activa[y][x] = 1
        x, y = iglesia.ARBOL_RETIRADO
        mapa.matriz_activa[y][x] = 0
    if (
        BUSQUEDA_DIA_2 in mapa.eventos_completados
        and estado_jugador.confianza_lucas_separacion is None
    ):
        estado_jugador.confianza_lucas_separacion = estado_jugador.confianza_lucas


def _distancia(punto):
    return abs(mapa.mateo_x - punto[0]) + abs(mapa.mateo_y - punto[1])


def al_iniciar_dialogo(evento):
    global director

    if evento == "evento_reunion_morales":
        mapa.jugador_bloqueado = True
        mapa.npcs_activos["lucas"]["comportamiento"] = "estatico"
        director = Director(_entrar_iglesia())


def _secuencia():
    yield "dialogo", "evento_lucas_iglesia"
    yield "hacer", _iniciar_exploracion


def _iniciar_exploracion():
    mapa.eventos_completados.add(MARCA)
    mapa.npcs_activos["lucas"]["comportamiento"] = "sigue_jugador"
    mapa.jugador_bloqueado = False


def _recorrido(nombre, destino, retraso=0, al_llegar=None):
    if nombre == "mateo":
        origen = mapa.mateo_x, mapa.mateo_y
    else:
        npc = mapa.npcs_activos[nombre]
        origen = npc["x"], npc["y"]
    return Recorrido(nombre, ruta_a(origen, destino), intervalo=PASO_MS,
                     retraso=retraso, al_llegar=al_llegar)


def _ocultar_al_entrar(nombre):
    mapa.npcs_activos[nombre]["visible"] = False
    if nombre == "morales":
        sonido("open_door")


def _entrar_iglesia():
    destino = iglesia.ENTRADA_IGLESIA
    morales = _recorrido("morales", destino, al_llegar=lambda: _ocultar_al_entrar("morales"))
    mateo = _recorrido("mateo", destino)
    lucas = _recorrido("lucas", destino, al_llegar=lambda: _ocultar_al_entrar("lucas"))
    # Compensar la distancia de cada personaje para cruzar la puerta en orden.
    mateo.retraso = max(1, len(morales.puntos) - len(mateo.puntos) + 2) * PASO_MS
    llegada_mateo = mateo.retraso + len(mateo.puntos) * PASO_MS
    lucas.retraso = max(0, llegada_mateo - (len(lucas.puntos) - 2) * PASO_MS)
    yield "mover", [morales, mateo, lucas]
    yield "hacer", _girar_ninos
    yield "pausa", 1000
    yield "hacer", _cargar_iglesia


def _girar_ninos():
    for nombre in iglesia.NINOS:
        nino = mapa.npcs_activos[nombre]
        if "espaldas" in nino["sprites_especiales"]:
            nino["sprite_override"] = "espaldas"


def _cargar_iglesia():
    mapa.eventos_completados.add(MARCA_REUNION)
    mapa.cargar_nivel("dentro_iglesia", sonido_llegada=CERRAR_PUERTA)


def _iniciar_regreso():
    global director

    x, y = iglesia.REGRESO_INTERIOR
    colocar("morales", x, y+1, "der")
    colocar("lucas", x-1, y, "der")
    mapa.jugador_bloqueado = True
    director = Director(_regresar_escondite())


def _regresar_escondite():
    yield "dialogo", "evento_siguen_morales"
    yield "mover", [
        _recorrido("morales", iglesia.ESCONDITE_MORALES),
        _recorrido("mateo", (11, 3), retraso=650),
        _recorrido("lucas", (12, 3), retraso=1050),
    ]
    yield from _separacion()


def _separacion():
    yield "hacer", lambda: mirar("morales", "der")
    yield "hacer", lambda: mirar("mateo", "izq")
    yield "hacer", lambda: mirar("lucas", "izq")
    yield "dialogo", "evento_plan_de_busqueda"
    yield "mover", [_recorrido("lucas", iglesia.SALIDA_PUEBLO)]
    yield "hacer", _despedir_lucas
    yield "dialogo", "evento_informar_morales"
    yield "hacer", _habilitar_busqueda


def _despedir_lucas():
    mapa.npcs_activos["lucas"]["visible"] = False


def _habilitar_busqueda():
    mapa.eventos_completados.update((MARCA_REGRESO, BUSQUEDA_DIA_2))
    _despedir_lucas()
    x, y = iglesia.SALIDA_PUEBLO
    mapa.matriz_activa[y][x] = 97
    mapa.jugador_bloqueado = False
