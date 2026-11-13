import pygame
import sistema_mapa
import sistema_dialogo
from configuracion import TAMANO_CASILLA


estado_escena = "INICIO"
tiempo_inicio = 0
tiempo_paso = 0

RETRASO_PASO = 250


def iniciar():
    global estado_escena, tiempo_inicio, tiempo_paso

    sistema_dialogo.cargar_json("datos/llegada.json")

    # Al volver a este mapa, la escena ya no se repite.
    if "llegada_completada" in sistema_mapa.eventos_completados:
        sistema_mapa.npcs_activos["abuela"]["visible"] = False
        sistema_mapa.npcs_activos["lucas"]["visible"] = False
        sistema_mapa.jugador_bloqueado = False
        estado_escena = "JUGABLE"
        return

    sistema_mapa.jugador_bloqueado = True

    sistema_mapa.mateo_x = 2
    sistema_mapa.mateo_y = 7
    sistema_mapa.mateo_px_x = float(2 * TAMANO_CASILLA)
    sistema_mapa.mateo_px_y = float(9 * TAMANO_CASILLA)
    sistema_mapa.direccion_mateo = "der"

    # Los NPC ya fueron creados por sistema_mapa al cargar llegada.py.
    lucas = sistema_mapa.npcs_activos["lucas"]
    abuela = sistema_mapa.npcs_activos["abuela"]

    for npc, x, y, direccion in (
        (lucas, 2, 8, "der"),
        (abuela, 16, 5, "abajo"),
    ):
        npc["x"] = x
        npc["y"] = y
        npc["px_x"] = float(x * TAMANO_CASILLA)
        npc["px_y"] = float(y * TAMANO_CASILLA)
        npc["direccion"] = direccion
        npc["visible"] = True
        npc["comportamiento"] = "estatico"
        npc["sprite_override"] = None

    estado_escena = "ESPERA_INICIAL"
    tiempo_inicio = pygame.time.get_ticks()
    tiempo_paso = tiempo_inicio


def actualizar():
    global estado_escena, tiempo_paso

    if estado_escena == "JUGABLE":
        return

    tiempo_actual = pygame.time.get_ticks()
    abuela = sistema_mapa.npcs_activos["abuela"]
    lucas = sistema_mapa.npcs_activos["lucas"]
    evento_activo = sistema_dialogo.obtener_evento_activo()

    if estado_escena == "ESPERA_INICIAL":
        if tiempo_actual - tiempo_inicio > 1000:
            sistema_dialogo.iniciar_dialogo("evento_llegada_1")
            estado_escena = "DIALOGO_1"

    elif estado_escena == "DIALOGO_1":
        if evento_activo is None:
            estado_escena = "ABUELA_BAJA"
            tiempo_paso = tiempo_actual

    elif estado_escena == "ABUELA_BAJA":
        abuela["direccion"] = "abajo"

        if tiempo_actual - tiempo_paso >= RETRASO_PASO:
            abuela["y"] += 1
            tiempo_paso = tiempo_actual

            if abuela["y"] >= 7:
                estado_escena = "ABUELA_ACERCA"

    elif estado_escena == "ABUELA_ACERCA":
        abuela["direccion"] = "izq"

        if tiempo_actual - tiempo_paso >= RETRASO_PASO:
            abuela["x"] -= 1
            tiempo_paso = tiempo_actual

            if abuela["x"] <= 3:
                sistema_mapa.direccion_mateo = "der"
                sistema_dialogo.iniciar_dialogo("evento_llegada_2")
                estado_escena = "DIALOGO_2"

    elif estado_escena == "DIALOGO_2":
        if evento_activo is None:
            estado_escena = "ABUELA_SE_VA"
            tiempo_paso = tiempo_actual

    elif estado_escena == "ABUELA_SE_VA":
        abuela["direccion"] = "der"

        if tiempo_actual - tiempo_paso >= RETRASO_PASO:
            abuela["x"] += 1
            tiempo_paso = tiempo_actual

            if abuela["x"] > 20:
                abuela["visible"] = False
                sistema_dialogo.iniciar_dialogo("evento_llegada_3")
                estado_escena = "DIALOGO_3"

    elif estado_escena == "DIALOGO_3":
        if evento_activo is None:
            estado_escena = "LUCAS_SE_VA"
            tiempo_paso = tiempo_actual

    elif estado_escena == "LUCAS_SE_VA":
        lucas["direccion"] = "der"

        if tiempo_actual - tiempo_paso >= RETRASO_PASO:
            lucas["x"] += 1
            tiempo_paso = tiempo_actual

            if lucas["x"] > 20:
                lucas["visible"] = False
                sistema_mapa.eventos_completados.add(
                    "llegada_completada"
                )
                sistema_mapa.jugador_bloqueado = False
                estado_escena = "JUGABLE"