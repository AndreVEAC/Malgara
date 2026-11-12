import pygame
import sistema_mapa

# Registro de comportamientos
def actualizar_npcs(tiempo_actual):
    """Itera todos los NPCs y ejecuta su comportamiento si lo tienen."""
    for npc_id, npc in sistema_mapa.npcs_activos.items():
        comportamiento = npc.get("comportamiento")
        if comportamiento is None or comportamiento == "estatico":
            continue
        elif comportamiento == "patrulla":
            _actualizar_patrulla(npc, tiempo_actual)
        elif comportamiento == "sigue_jugador":
            _actualizar_sigue_jugador(npc, tiempo_actual)
        # Añadir más aquí en el futuro


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
    if (nx, ny) == (sistema_mapa.mateo_x, sistema_mapa.mateo_y):
        if empuja:
            _intentar_empujar_mateo(dx, dy)
        return

    # Colisión con otros NPCs
    for otro in sistema_mapa.npcs_activos.values():
        if otro is npc:
            continue
        if otro["visible"] and (nx, ny) == (otro["x"], otro["y"]):
            return

    # Colisión con muros
    if sistema_mapa.matriz_activa[ny][nx] == 1:
        return
    if sistema_mapa.matriz_activa[ny][nx] in sistema_mapa.interactuables_activos:
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
    if not (0 <= nx < sistema_mapa.columnas_mapa and 0 <= ny < sistema_mapa.filas_mapa):
        return False
    casilla = sistema_mapa.matriz_activa[ny][nx]
    if casilla == 1:
        return False
    if casilla in sistema_mapa.interactuables_activos:
        return False
    for npc in sistema_mapa.npcs_activos.values():
        if npc["visible"] and (nx, ny) == (npc["x"], npc["y"]):
            return False
    return True


def _actualizar_sigue_jugador(npc, tiempo_actual):
    """El NPC persigue a Mateo a una casilla de distancia."""
    # (implementación futura)
    pass