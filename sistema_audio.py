import pygame

pista_actual = None

# Nombres que usarán los mapas y sus archivos correspondientes.
PISTAS = {
    "viento_desierto": "recursos/musica/ambiente_desierto.wav",
    "pueblo": "recursos/musica/Lanterns_at_Dusk.wav",
}


def inicializar():
    if not pygame.mixer.get_init():
        pygame.mixer.init()


def reproducir_ambiente(nombre_pista, volumen=0.4, fade_ms=1000):
    global pista_actual

    inicializar()

    if nombre_pista is None:
        detener_musica(fade_ms)
        return

    volumen = max(0.0, min(1.0, volumen))

    # Misma pista: continuar exactamente donde iba.
    if (
        pista_actual == nombre_pista
        and pygame.mixer.music.get_busy()
    ):
        pygame.mixer.music.set_volume(volumen)
        return

    ruta = PISTAS.get(nombre_pista)

    if ruta is None:
        print(f"[AUDIO] Pista no registrada: {nombre_pista}")
        return

    try:
        pygame.mixer.music.load(ruta)
        pygame.mixer.music.set_volume(volumen)

        # Repetir indefinidamente, con entrada gradual.
        pygame.mixer.music.play(-1, fade_ms=fade_ms)

        pista_actual = nombre_pista

    except (pygame.error, FileNotFoundError) as error:
        pista_actual = None
        print(f"[AUDIO] No se pudo reproducir '{ruta}': {error}")


def detener_musica(fade_ms=1000):
    global pista_actual

    if pygame.mixer.get_init():
        pygame.mixer.music.fadeout(fade_ms)

    pista_actual = None