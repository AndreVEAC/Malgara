import pygame


pista_actual = None

_ambiente = None
_volumen_ambiente = 0.4
_persecucion = False


PISTAS = {
    "viento_desierto": "recursos/musica/ambiente_desierto.wav",
    "pueblo": "recursos/musica/Lanterns_at_Dusk.wav",
    "hogar": "recursos/musica/Refuge.wav",
    "noche_calmada": "recursos/musica/noche_calmada.wav",
    "persecucion": "recursos/musica/corre.wav",
    "tension": "recursos/musica/tension.wav",
    "miradas": "recursos/musica/miradas.wav",
    "catedral": "recursos/musica/catedral.wav",
    "triste": "recursos/musica/triste.wav",
    "ultima_cura": "recursos/musica/ultima cura.wav",
    "ultimo_paseo": "recursos/musica/un ultimo paseo.wav",
    "falta_uno": "recursos/musica/falta uno.wav",
}


def inicializar():
    if not pygame.mixer.get_init():
        pygame.mixer.init()


def _reproducir(nombre, volumen, fade_ms):
    global pista_actual

    inicializar()
    volumen = max(0.0, min(1.0, volumen))

    # Si ya suena esta pista, no reiniciarla.
    if (
        pista_actual == nombre
        and pygame.mixer.music.get_busy()
    ):
        pygame.mixer.music.set_volume(volumen)
        return

    try:
        pygame.mixer.music.load(PISTAS[nombre])
        pygame.mixer.music.set_volume(volumen)
        pygame.mixer.music.play(-1, fade_ms=fade_ms)

        pista_actual = nombre

    except (pygame.error, FileNotFoundError) as error:
        pista_actual = None
        print(
            f"[AUDIO] No se pudo reproducir "
            f"'{PISTAS[nombre]}': {error}"
        )


def reproducir_ambiente(
    nombre_pista,
    volumen=0.4,
    fade_ms=1000,
):
    global _ambiente, _volumen_ambiente

    if nombre_pista is not None and nombre_pista not in PISTAS:
        print(f"[AUDIO] Pista no registrada: {nombre_pista}")
        return

    # Recordar el ambiente que corresponde al mapa.
    _ambiente = nombre_pista
    _volumen_ambiente = volumen

    # Durante la persecución, guardar el ambiente sin interrumpir corre.
    if _persecucion:
        return

    if nombre_pista is None:
        _silenciar(fade_ms)
    else:
        _reproducir(nombre_pista, volumen, fade_ms)


def establecer_persecucion(activa):
    global _persecucion

    activa = bool(activa)

    # Evita reiniciar la música en cada actualización.
    if activa == _persecucion:
        return

    _persecucion = activa

    if activa:
        _reproducir("persecucion", 0.6, 250)

    elif _ambiente is not None:
        # Recuperar el ambiente desde el inicio.
        _reproducir(_ambiente, _volumen_ambiente, 1000)

    else:
        _silenciar(500)


def _silenciar(fade_ms):
    global pista_actual

    if pygame.mixer.get_init():
        if fade_ms > 0:
            pygame.mixer.music.fadeout(fade_ms)
        else:
            pygame.mixer.music.stop()

    pista_actual = None


def detener_musica(fade_ms=1000):
    global _ambiente, _persecucion

    _ambiente = None
    _persecucion = False
    _silenciar(fade_ms)
