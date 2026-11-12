import pygame
import sistema_mapa
import sistema_dialogo

estado_escena = "INICIO"
tiempo_inicio = 0


def iniciar():
    """Se ejecuta una sola vez cuando el nivel carga."""
    global estado_escena, tiempo_inicio

    lucas = sistema_mapa.npcs_activos.get("lucas")

    # Si Mateo ya pasó por aquí (o viene regresando desde prologo), modo exploración libre
    if "intro_completada" in sistema_mapa.eventos_completados:
        sistema_mapa.jugador_bloqueado = False
        if lucas:
            lucas["visible"] = False
            lucas["pausado"] = True
        estado_escena = "JUGABLE"
        return

    # Primera vez en intro: preparar cinemática
    sistema_dialogo.cargar_json("datos/intro.json")
    sistema_mapa.jugador_bloqueado = True
    sistema_mapa.direccion_mateo = "der"

    if lucas:
        lucas["pausado"] = True  # Esperar a que termine el diálogo para caminar

    estado_escena = "ESPERA_INICIAL"
    tiempo_inicio = pygame.time.get_ticks()


def actualizar():
    """Se ejecuta en cada fotograma mientras estés en este mapa."""
    global estado_escena
    if estado_escena == "JUGABLE":
        return

    tiempo_actual = pygame.time.get_ticks()
    lucas = sistema_mapa.npcs_activos.get("lucas")

    if estado_escena == "ESPERA_INICIAL":
        if tiempo_actual - tiempo_inicio > 1500:
            sistema_dialogo.iniciar_dialogo("evento_intro_1")
            estado_escena = "ESPERANDO_DIALOGO"

    elif estado_escena == "ESPERANDO_DIALOGO":
        if sistema_dialogo.obtener_evento_activo() is None:
            if lucas:
                lucas["pausado"] = False  # Sistema NPC toma el control y lo mueve a la derecha
            estado_escena = "LUCAS_SE_VA"

    elif estado_escena == "LUCAS_SE_VA":
        # Cuando Lucas alcanza la columna 19 (borde derecho), desaparece y libera a Mateo
        if not lucas or lucas["x"] >= 19:
            if lucas:
                lucas["visible"] = False
                lucas["pausado"] = True
            sistema_mapa.jugador_bloqueado = False
            sistema_mapa.eventos_completados.add("intro_completada")
            estado_escena = "JUGABLE"