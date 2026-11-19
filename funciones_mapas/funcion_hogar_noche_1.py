import pygame
import sistema_mapa as mapa
import sistema_guardado

CENTRAR_FONDO = True

sonido_cerrar = None


def iniciar():
    global sonido_cerrar

    mapa.jugador_bloqueado = False

    # Orientación según la puerta por la que entramos.
    if (mapa.mateo_x, mapa.mateo_y) == (1, 2):
        mapa.direccion_mateo = "abajo"
    else:
        mapa.direccion_mateo = "arriba"

    # Cargar una partida no cuenta como cruzar una puerta.
    if sistema_guardado.cargando:
        return

    try:
        sonido_cerrar = pygame.mixer.Sound(
            "recursos/sonidos/efectos/close_door.wav"
        )
        sonido_cerrar.play()
    except (pygame.error, FileNotFoundError) as error:
        print(f"[AUDIO] No se pudo reproducir close_door: {error}")


def actualizar():
    pass