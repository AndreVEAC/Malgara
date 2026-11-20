import pygame
import sistema_mapa
import sistema_escondites
import sistema_vigilancia
from collections import deque
import sistema_dialogo

def actualizar_npcs(tiempo_actual):
    """Actualizar vigilancia antes que los seguidores."""

    sistema_vigilancia.actualizar(tiempo_actual)

    for npc_id, npc in sistema_mapa.npcs_activos.items():
        if not npc.get("visible", True):
            continue

        comportamiento = npc.get("comportamiento")

        if comportamiento in (None, "estatico", "vigilante"):
            # Los vigilantes ya se actualizaron arriba.
            continue

        elif comportamiento == "patrulla":
            _actualizar_patrulla(npc, tiempo_actual)

        elif comportamiento == "sigue_jugador":
            _actualizar_sigue_jugador(npc, tiempo_actual)


def _actualizar_patrulla(npc, tiempo_actual):
    """Un NPC camina en línea recta hasta un límite y se detiene."""
    if npc.get("pausado", False):
        return
    config = npc.get("patrulla", {})
    velocidad_ms = config.get("velocidad_ms", 250)
    hasta_x = config.get("hasta_x")
    hasta_y = config.get("hasta_y")
    empuja = config.get("empuja_jugador", False)
    esperar_en_x = config.get("esperar_en_x", [])
    
    if npc["x"] in esperar_en_x and npc["x"] not in npc.get("_esperas_resueltas", set()):
        if npc["x"] in (9, 23, 37):
            print(f"[NPC] Lucas bloqueado en x={npc['x']}, "
                  f"esperas={npc.get('_esperas_resueltas', set())}")
        return 
    
    if npc["x"] in esperar_en_x and npc["x"] not in npc.get("_esperas_resueltas", set()):
        return

    ultimo_paso = npc.get("_tiempo_ultimo_paso", 0)
    if tiempo_actual - ultimo_paso < velocidad_ms:
        return
    npc["_tiempo_ultimo_paso"] = tiempo_actual

    # Calcular dirección de patrulla
    if hasta_x is not None and npc["x"] < hasta_x:
        dx, dy = 1, 0
        npc["direccion"] = "der"
    elif hasta_x is not None and npc["x"] > hasta_x:
        dx, dy = -1, 0
        npc["direccion"] = "izq"
    elif hasta_y is not None and npc["y"] < hasta_y:
        dx, dy = 0, 1
        npc["direccion"] = "abajo"
    elif hasta_y is not None and npc["y"] > hasta_y:
        dx, dy = 0, -1
        npc["direccion"] = "arriba"
    else:
        return  # ya llegó al destino

    nx, ny = npc["x"] + dx, npc["y"] + dy

    # Colisión con Mateo (si empuja, lo mueve; si no, se para)
    if (
        not sistema_escondites.escondido
        and (nx, ny) == (
            sistema_mapa.mateo_x,
            sistema_mapa.mateo_y,
        )
    ):
        if empuja:
            _intentar_empujar_mateo(dx, dy)
        return

    # Colisión con otros NPCs
    for otro in sistema_mapa.npcs_activos.values():
        if otro is npc:
            continue
        if otro["visible"] and (nx, ny) == (otro["x"], otro["y"]):
            return

    if sistema_mapa.casilla_bloqueada(nx, ny):
        return
    
    npc["x"], npc["y"] = nx, ny


def _intentar_empujar_mateo(dx, dy):
    """Empuja a Mateo a un lado (perpendicular). Fallback: hacia delante."""
    if dx != 0:
        candidatos = [(0, -1), (0, 1), (dx, dy)]
    elif dy != 0:
        candidatos = [(-1, 0), (1, 0), (dx, dy)]
    else:
        candidatos = [(dx, dy)]

    for ex, ey in candidatos:
        if _puede_mover_mateo(ex, ey):
            sistema_mapa.mateo_x += ex
            sistema_mapa.mateo_y += ey
            return


def _puede_mover_mateo(ex, ey):
    nx = sistema_mapa.mateo_x + ex
    ny = sistema_mapa.mateo_y + ey

    if sistema_mapa.casilla_bloqueada(nx, ny):
        return False

    for npc in sistema_mapa.npcs_activos.values():
        if npc["visible"] and (nx, ny) == (npc["x"], npc["y"]):
            return False

    return True


def _actualizar_sigue_jugador(npc, tiempo_actual):
    """Sigue a Mateo por casillas, buscando un camino libre."""
    if not npc.get("visible", True):
        return

    if npc.get("pausado", False):
        return

    if sistema_mapa.transicion_activa:
        return

    if sistema_dialogo.obtener_evento_activo() is not None:
        return

    config = npc.get("seguimiento", {})

    velocidad_ms = (
        max(1, sistema_mapa.RETRASO_MATEO // 2)
        if sistema_vigilancia.persecucion_activa
        else config.get("velocidad_ms", 200)
    )

    ultimo_paso = npc.get("_tiempo_ultimo_paso", 0)
    if tiempo_actual - ultimo_paso < velocidad_ms:
        return

    mateo = (sistema_mapa.mateo_x, sistema_mapa.mateo_y)
    distancia = abs(npc["x"] - mateo[0]) + abs(npc["y"] - mateo[1])

    if distancia == 1:
        # Ya está junto a Mateo: mirarlo y quedarse quieto.
        _orientar_hacia(npc, mateo[0], mateo[1])
        return

    # También limita la frecuencia de búsqueda si no hay camino.
    npc["_tiempo_ultimo_paso"] = tiempo_actual

    paso = _buscar_paso_hacia_jugador(npc, mateo)
    if paso is None:
        return

    nx, ny = paso
    _orientar_hacia(npc, nx, ny)
    npc["x"], npc["y"] = nx, ny


def _orientar_hacia(npc, x, y):
    """Cambiar la dirección del sprite sin mover al NPC."""
    dx = x - npc["x"]
    dy = y - npc["y"]

    if abs(dx) > abs(dy):
        npc["direccion"] = "der" if dx > 0 else "izq"
    elif dy != 0:
        npc["direccion"] = "abajo" if dy > 0 else "arriba"


def _buscar_paso_hacia_jugador(npc, mateo):
    """Devuelve el primer paso de una ruta hasta una casilla junto a Mateo."""
    inicio = (npc["x"], npc["y"])

    ocupadas = {
        (otro["x"], otro["y"])
        for otro in sistema_mapa.npcs_activos.values()
        if otro is not npc and otro.get("visible", True)
    }

    # Cada entrada guarda la posición explorada y el primer paso
    # que habría que dar para llegar hasta ella.
    pendientes = deque([(inicio, None)])
    visitadas = {inicio}

    while pendientes:
        (x, y), primer_paso = pendientes.popleft()

        distancia = abs(x - mateo[0]) + abs(y - mateo[1])

        if distancia == 1:
            return primer_paso

        vecinos = [
            (x + 1, y),
            (x - 1, y),
            (x, y + 1),
            (x, y - 1),
        ]

        # Entre caminos equivalentes, preferir acercarse a Mateo.
        vecinos.sort(
            key=lambda posicion: (
                abs(posicion[0] - mateo[0])
                + abs(posicion[1] - mateo[1])
            )
        )

        for nx, ny in vecinos:
            posicion = (nx, ny)

            if posicion in visitadas:
                continue

            visitadas.add(posicion)

            if posicion == mateo or posicion in ocupadas:
                continue

            # Incluye límites, muros, interactuables y objetos sólidos.
            if sistema_mapa.casilla_bloqueada(nx, ny):
                continue

            siguiente_paso = (
                posicion if primer_paso is None else primer_paso
            )
            pendientes.append((posicion, siguiente_paso))

    # No existe un camino accesible: esperar.
    return None