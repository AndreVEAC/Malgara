import pygame

pista_actual = None

def inicializar():
    pygame.mixer.init()

def reproducir_ambiente(nombre_pista, volumen=0.4, fade_ms=1000):
    global pista_actual
    
    if pista_actual == nombre_pista:
        return  # Si ya está sonando esta misma pista, no la reiniciamos

    ruta = f"recursos/musica/ambiente_desierto.wav"
    try:
        pygame.mixer.music.fadeout(fade_ms)
        pygame.mixer.music.load(ruta)
        pygame.mixer.music.set_volume(volumen)
        pygame.mixer.music.play(-1, fade_ms=fade_ms)
        pista_actual = nombre_pista
    except pygame.error:
        print(f"Aviso Audio: No se encontró la pista '{nombre_pista}' en recursos/sonidos/")

def detener_musica(fade_ms=1000):
    global pista_actual
    pygame.mixer.music.fadeout(fade_ms)
    pista_actual = None