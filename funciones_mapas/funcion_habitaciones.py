import importlib.util

import pygame
import sistema_mapa
import sistema_dialogo


CENTRAR_FONDO = True

dormir_pendiente = False
sonido_cierre = None


def iniciar():
    global dormir_pendiente, sonido_cierre

    dormir_pendiente = False
    sonido_cierre = None

    sistema_dialogo.cargar_json("datos/habitaciones.json")

    sistema_mapa.jugador_bloqueado = False
    sistema_mapa.direccion_mateo = "arriba"

    # Se ejecuta cuando el motor carga habitaciones,
    # durante el cambio de mapa.
    try:
        sonido_cierre = pygame.mixer.Sound(
            "recursos/sonidos/efectos/close_door.wav"
        )
        sonido_cierre.play()

    except (pygame.error, FileNotFoundError) as error:
        print(
            "[Habitaciones] No se pudo reproducir "
            f"close_door.wav: {error}"
        )


def al_elegir_opcion(nombre_evento):
    global dormir_pendiente

    if nombre_evento != "evento_cama_mateo":
        return

    # El sistema llama a esta función antes de cerrar
    # el diálogo o cambiar al siguiente evento.
    eleccion = sistema_dialogo.opciones_actuales[
        sistema_dialogo.opcion_seleccionada
    ]

    dormir_pendiente = (
        eleccion.get("accion") == "dormir"
    )


def actualizar():
    global dormir_pendiente

    if not dormir_pendiente:
        return

    if sistema_mapa.transicion_activa:
        return

    if sistema_dialogo.obtener_evento_activo() is not None:
        return

    dormir_pendiente = False

    # Protección temporal: todavía no hemos creado
    # mapas/habitaciones_noche.py.
    if importlib.util.find_spec(
        "mapas.habitaciones_noche"
    ) is None:
        sistema_dialogo.iniciar_dialogo(
            "evento_noche_pendiente"
        )
        return

    sistema_mapa.eventos_completados.add(
        "primera_noche_iniciada"
    )

    sistema_mapa.jugador_bloqueado = True

    # Aprovecha el fade out/fade in del motor.
    sistema_mapa.cargar_nivel("habitaciones_noche")