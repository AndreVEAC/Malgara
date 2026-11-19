# funciones_mapas/funcion_viaje.py

import pygame

import sistema_mapa as mapa
import sistema_dialogo as dialogo
import sistema_audio


PANTALLA_NEGRA = True

RUTA_INICIO = (
    "recursos/sonidos/efectos/inicio_camion.wav"
)

RUTA_MOTOR = (
    "recursos/sonidos/efectos/sonido_camion.wav"
)

estado_escena = "INICIO"

sonido_inicio = None
sonido_motor = None
canal_camion = None

espera_hasta = 0


def iniciar():
    global estado_escena
    global sonido_inicio, sonido_motor, canal_camion
    global espera_hasta

    if canal_camion is not None:
        canal_camion.stop()

    canal_camion = None
    sonido_inicio = None
    sonido_motor = None

    dialogo.cargar_json("datos/viaje.json")
    mapa.jugador_bloqueado = True

    sistema_audio.detener_musica(fade_ms=0)

    sonido_inicio = _cargar_sonido(RUTA_INICIO)
    sonido_motor = _cargar_sonido(RUTA_MOTOR)

    if pygame.mixer.get_init() is not None:
        canal_camion = pygame.mixer.find_channel(True)

        if canal_camion is not None:
            canal_camion.set_volume(0.5)

    # El camión ya está avanzando cuando comienza la escena.
    _reproducir(sonido_motor, repetir=True)

    estado_escena = "ESPERA_INICIAL"
    espera_hasta = pygame.time.get_ticks() + 300


def actualizar():
    global estado_escena

    if estado_escena == "TERMINADO":
        return

    # No abrir diálogos durante un cambio de mapa.
    if mapa.transicion_activa:
        return

    ahora = pygame.time.get_ticks()

    if estado_escena == "ESPERA_INICIAL":
        if ahora < espera_hasta:
            return

        _iniciar_dialogo("evento_viaje")
        estado_escena = "CONVERSACION"

    elif estado_escena == "CONVERSACION":
        # Incluye la elección y su diálogo de respuesta.
        # El motor sigue sonando durante toda la conversación.
        if dialogo.obtener_evento_activo() is not None:
            return

        if canal_camion is not None:
            canal_camion.stop()

        # Volver a usar el efecto corto como parada.
        _reproducir(sonido_inicio)
        estado_escena = "FRENANDO"

    elif estado_escena == "FRENANDO":
        if _sonando():
            return

        _iniciar_dialogo("viaje_final")
        estado_escena = "LLEGADA"

    elif estado_escena == "LLEGADA":
        if dialogo.obtener_evento_activo() is not None:
            return

        if canal_camion is not None:
            canal_camion.stop()

        mapa.eventos_completados.add("viaje_completado")

        # Marcar antes de cargar para no repetir la solicitud.
        estado_escena = "TERMINADO"

        # Usa el fundido existente del motor.
        # Como viaje ya es negro, se revelará intro desde negro.
        mapa.cargar_nivel("intro")


def _cargar_sonido(ruta):
    try:
        return pygame.mixer.Sound(ruta)

    except (pygame.error, FileNotFoundError) as error:
        print(
            f"[Viaje] No se pudo cargar '{ruta}': {error}"
        )
        return None


def _reproducir(sonido, repetir=False):
    if canal_camion is None or sonido is None:
        return

    canal_camion.play(
        sonido,
        loops=-1 if repetir else 0
    )


def _sonando():
    return (
        canal_camion is not None
        and canal_camion.get_busy()
    )


def _iniciar_dialogo(nombre):
    dialogo.iniciar_dialogo(nombre)

    if dialogo.obtener_evento_activo() is None:
        raise ValueError(
            f"Falta el evento '{nombre}' "
            "en datos/viaje.json"
        )