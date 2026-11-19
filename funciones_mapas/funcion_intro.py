import pygame
import sistema_mapa
import sistema_dialogo

from configuracion import TAMANO_CASILLA, ANCHO_PANTALLA


estado_escena = "INICIO"

tiempo_inicio = 0
tiempo_ultimo_paso = 0

RETRASO_PASO = 200


def iniciar():
    global estado_escena
    global tiempo_inicio, tiempo_ultimo_paso

    sistema_dialogo.cargar_json("datos/intro.json")

    lucas = sistema_mapa.npcs_activos.get("lucas")

    if lucas:
        # El director controla esta salida.
        # Evita que la patrulla intente consultar
        # casillas fuera de la matriz.
        lucas["comportamiento"] = "estatico"
        lucas["pausado"] = True

    # Al regresar, la cinemática no se repite.
    if "intro_completada" in sistema_mapa.eventos_completados:
        sistema_mapa.jugador_bloqueado = False

        if lucas:
            lucas["visible"] = False

        estado_escena = "JUGABLE"
        return

    sistema_mapa.jugador_bloqueado = True
    sistema_mapa.direccion_mateo = "der"

    if lucas:
        lucas["visible"] = True
        lucas["direccion"] = "izq"

    tiempo_inicio = pygame.time.get_ticks()
    tiempo_ultimo_paso = tiempo_inicio

    estado_escena = "ESPERA_INICIAL"


def actualizar():
    global estado_escena, tiempo_ultimo_paso

    if estado_escena == "JUGABLE":
        return

    if sistema_mapa.transicion_activa:
        return

    ahora = pygame.time.get_ticks()
    lucas = sistema_mapa.npcs_activos.get("lucas")

    if estado_escena == "ESPERA_INICIAL":
        if ahora - tiempo_inicio >= 1500:
            sistema_dialogo.iniciar_dialogo(
                "evento_intro_1"
            )

            estado_escena = "ESPERANDO_DIALOGO"

    elif estado_escena == "ESPERANDO_DIALOGO":
        if sistema_dialogo.obtener_evento_activo() is not None:
            return

        if lucas:
            lucas["direccion"] = "der"

        tiempo_ultimo_paso = ahora
        estado_escena = "LUCAS_SE_VA"

    elif estado_escena == "LUCAS_SE_VA":
        if lucas is None:
            _terminar_escena()
            return

        camara_x, _ = sistema_mapa.calcular_camara()

        # px_x es el borde izquierdo del sprite.
        # Cuando cruza el borde derecho de la pantalla,
        # Lucas ya está completamente fuera del encuadre.
        x_en_pantalla = lucas["px_x"] - camara_x

        if x_en_pantalla >= ANCHO_PANTALLA:
            lucas["visible"] = False
            lucas["pausado"] = True

            _terminar_escena()
            return

        objetivo_x = lucas["x"] * TAMANO_CASILLA
        objetivo_y = lucas["y"] * TAMANO_CASILLA

        paso_terminado = (
            abs(lucas["px_x"] - objetivo_x) < 0.5
            and abs(lucas["px_y"] - objetivo_y) < 0.5
        )

        if (
            paso_terminado
            and ahora - tiempo_ultimo_paso >= RETRASO_PASO
        ):
            lucas["direccion"] = "der"

            # Salida guionizada por la fila despejada.
            # Puede avanzar fuera de la matriz sin leerla.
            lucas["x"] += 1

            tiempo_ultimo_paso = ahora


def _terminar_escena():
    global estado_escena

    sistema_mapa.eventos_completados.add(
        "intro_completada"
    )

    sistema_mapa.jugador_bloqueado = False
    estado_escena = "JUGABLE"