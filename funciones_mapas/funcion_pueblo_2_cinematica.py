# funciones_mapas/funcion_pueblo_2_cinematica.py

from collections import deque

import pygame
import sistema_mapa
import sistema_dialogo
from configuracion import TAMANO_CASILLA
from mapas import pueblo_2_cinematica as mapa


estado_escena = "EXPLORACION"
tiempos_paso = {}
rutas = {}

RETRASO_PASO = 220
MARCA_COMPLETADA = "bienvenida_pueblo_completada"

# Puntos intermedios: caminar por el costado y después al centro.
# Lucas llega por una fila inferior para no bloquearse con Mateo.
RUTA_MATEO = [
    (9, 14),
    mapa.DESTINO_MATEO,
]

RUTA_LUCAS = [
    (9, 8),
    (9, 15),
    (20, 15),
    mapa.DESTINO_LUCAS,
]


def iniciar():
    global estado_escena, tiempos_paso, rutas

    sistema_dialogo.cargar_json(
        "datos/pueblo_2_cinematica.json"
    )

    # Detectar un JSON incompleto antes de empezar la escena.
    for evento in ("evento_antes_bienvenida", "evento_bienvenida"):
        if evento not in sistema_dialogo.datos_dialogo:
            raise ValueError(
                f"Falta '{evento}' en pueblo_2_cinematica.json"
            )

    tiempos_paso = {"mateo": 0, "lucas": 0}
    rutas = {
        "mateo": deque(RUTA_MATEO),
        "lucas": deque(RUTA_LUCAS),
    }

    lucas = sistema_mapa.npcs_activos["lucas"]
    lucas["comportamiento"] = "sigue_jugador"
    lucas["pausado"] = False

    if MARCA_COMPLETADA in sistema_mapa.eventos_completados:
        # Si vuelve a entrar por un portal antiguo, saltar la escena.
        sistema_mapa.jugador_bloqueado = True
        lucas["pausado"] = True
        estado_escena = "SALTAR_ESCENA"
    else:
        sistema_mapa.jugador_bloqueado = False
        estado_escena = "EXPLORACION"


def actualizar():
    global estado_escena

    # Esperar a que termine el fundido de entrada.
    if sistema_mapa.transicion_activa:
        return

    if estado_escena == "CAMBIANDO_MAPA":
        return

    if estado_escena == "SALTAR_ESCENA":
        _cambiar_a_exploracion()
        return

    evento_activo = sistema_dialogo.obtener_evento_activo()

    if estado_escena == "EXPLORACION":
        posicion = (sistema_mapa.mateo_x, sistema_mapa.mateo_y)

        if posicion in mapa.TRIGGERS_CINEMATICA :
            sistema_mapa.jugador_bloqueado = True

            lucas = sistema_mapa.npcs_activos["lucas"]
            lucas["pausado"] = True

            # Dejar que ambos terminen el paso que ya habían dado.
            estado_escena = "ESPERAR_PARADA"

    elif estado_escena == "ESPERAR_PARADA":
        if _ha_llegado("mateo") and _ha_llegado("lucas"):
            sistema_dialogo.iniciar_dialogo(
                "evento_antes_bienvenida"
            )
            estado_escena = "DIALOGO_INICIAL"

    elif estado_escena == "DIALOGO_INICIAL":
        if evento_activo is None:
            ahora = pygame.time.get_ticks()
            tiempos_paso["mateo"] = ahora

            # Lucas empieza ligeramente después.
            tiempos_paso["lucas"] = ahora + 120
            estado_escena = "CAMINANDO"

    elif estado_escena == "CAMINANDO":
        ahora = pygame.time.get_ticks()

        _avanzar_personaje("mateo", ahora)
        _avanzar_personaje("lucas", ahora)

        terminaron = not rutas["mateo"] and not rutas["lucas"]

        if (
            terminaron
            and _ha_llegado("mateo")
            and _ha_llegado("lucas")
        ):
            sistema_mapa.direccion_mateo = "arriba"
            sistema_mapa.npcs_activos["lucas"]["direccion"] = "arriba"
            sistema_mapa.npcs_activos["lider"]["direccion"] = "abajo"
            sistema_mapa.npcs_activos["abuela"]["direccion"] = "abajo"

            sistema_dialogo.iniciar_dialogo("evento_bienvenida")
            estado_escena = "DIALOGO_BIENVENIDA"

    elif estado_escena == "DIALOGO_BIENVENIDA":
        if evento_activo is None:
            sistema_mapa.eventos_completados.add(MARCA_COMPLETADA)
            _cambiar_a_exploracion()


def _cambiar_a_exploracion():
    global estado_escena

    # Cambiar de estado primero evita solicitar la carga cada frame.
    estado_escena = "CAMBIANDO_MAPA"
    sistema_mapa.jugador_bloqueado = True

    sistema_mapa.cargar_nivel(
        "pueblo_2",
        spawn_x=mapa.DESTINO_MATEO[0],
        spawn_y=mapa.DESTINO_MATEO[1]
    )


def _posicion(personaje):
    if personaje == "mateo":
        return sistema_mapa.mateo_x, sistema_mapa.mateo_y

    npc = sistema_mapa.npcs_activos[personaje]
    return npc["x"], npc["y"]


def _ha_llegado(personaje):
    """Comprobar que el sprite terminó de llegar a su casilla."""
    x, y = _posicion(personaje)

    if personaje == "mateo":
        px = sistema_mapa.mateo_px_x
        py = sistema_mapa.mateo_px_y
    else:
        npc = sistema_mapa.npcs_activos[personaje]
        px = npc["px_x"]
        py = npc["px_y"]

    return (
        abs(px - x * TAMANO_CASILLA) < 1
        and abs(py - y * TAMANO_CASILLA) < 1
    )


def _avanzar_personaje(personaje, ahora):
    ruta = rutas[personaje]

    if not ruta or not _ha_llegado(personaje):
        return

    posicion = _posicion(personaje)

    # Retirar los puntos intermedios ya alcanzados.
    while ruta and posicion == ruta[0]:
        ruta.popleft()

    if not ruta:
        return

    if ahora - tiempos_paso[personaje] < RETRASO_PASO:
        return

    tiempos_paso[personaje] = ahora
    paso = _buscar_paso(personaje, ruta[0])

    # Si otro personaje bloquea temporalmente el camino, esperar.
    if paso is None:
        return

    x, y = posicion
    nx, ny = paso

    if nx > x:
        direccion = "der"
    elif nx < x:
        direccion = "izq"
    elif ny > y:
        direccion = "abajo"
    else:
        direccion = "arriba"

    if personaje == "mateo":
        sistema_mapa.mateo_x = nx
        sistema_mapa.mateo_y = ny
        sistema_mapa.direccion_mateo = direccion
    else:
        npc = sistema_mapa.npcs_activos[personaje]
        npc["x"] = nx
        npc["y"] = ny
        npc["direccion"] = direccion


def _buscar_paso(personaje, destino):
    """Buscar un paso hasta el siguiente punto de la ruta."""
    inicio = _posicion(personaje)

    ocupadas = {
        (npc["x"], npc["y"])
        for npc_id, npc in sistema_mapa.npcs_activos.items()
        if npc_id != personaje and npc.get("visible", True)
    }

    if personaje != "mateo":
        ocupadas.add(
            (sistema_mapa.mateo_x, sistema_mapa.mateo_y)
        )

    pendientes = deque([(inicio, None)])
    visitadas = {inicio}

    while pendientes:
        (x, y), primer_paso = pendientes.popleft()

        if (x, y) == destino:
            return primer_paso

        vecinos = [
            (x + 1, y),
            (x - 1, y),
            (x, y + 1),
            (x, y - 1),
        ]

        vecinos.sort(
            key=lambda punto: (
                abs(punto[0] - destino[0])
                + abs(punto[1] - destino[1])
            )
        )

        for nx, ny in vecinos:
            punto = (nx, ny)

            if punto in visitadas:
                continue

            visitadas.add(punto)

            if punto in ocupadas:
                continue

            if sistema_mapa.casilla_bloqueada(nx, ny):
                continue

            paso = punto if primer_paso is None else primer_paso
            pendientes.append((punto, paso))

    return None