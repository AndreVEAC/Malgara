import sys

import pygame
from pygame.locals import QUIT
from configuracion import ANCHO_PANTALLA, ALTO_PANTALLA, TITULO_JUEGO, FPS
from estado import BUSQUEDA_DIA_2, EstadoJuego
import sistema_mapa
import sistema_dialogo
import sistema_guardado

pygame.init()
pantalla = pygame.display.set_mode((ANCHO_PANTALLA, ALTO_PANTALLA))
pygame.display.set_caption(TITULO_JUEGO)
reloj = pygame.time.Clock()

estado_jugador = EstadoJuego()
modo_juego = "EXPLORACION"

#if "--dia-2" in sys.argv:
#    sistema_mapa.cargar_nivel("habitaciones_dia_2")
#elif "--continuar" not in sys.argv or not sistema_guardado.continuar(estado_jugador):
sistema_mapa.cargar_nivel("habitaciones_dia_2")

ejecutando = True
while ejecutando:
    reloj.tick(FPS)
    sistema_guardado.actualizar(estado_jugador)
    # 1. GUARDAR LOS EVENTOS EN LA VARIABLE 'eventos'
    eventos = pygame.event.get()
    
    # Eventos globales (como cerrar la ventana)
    for evento in eventos:
        if evento.type == QUIT:
            ejecutando = False
            
        if evento.type == pygame.KEYDOWN:
            if evento.key == pygame.K_F11:
                pygame.display.toggle_fullscreen()

    pantalla.fill((0, 0, 0))

    # --- MÁQUINA DE ESTADOS ---
    if modo_juego == "EXPLORACION":
        # Todo el trabajo sucio lo hace sistema_mapa
        nuevo_modo = sistema_mapa.actualizar_y_dibujar(pantalla, estado_jugador)
        
        # Si sistema_mapa dice que pisamos un evento, cambiamos de modo
        if nuevo_modo != modo_juego:
            modo_juego = nuevo_modo

    elif modo_juego == "DIALOGO":
        
        sistema_mapa.solo_dibujar(pantalla)
        # 2. SE ELIMINÓ EL REGRESO FORZADO A EXPLORACIÓN
        # sistema_dialogo se encarga de devolver "EXPLORACION" por sí solo al terminar de leer el JSON
        modo_juego = sistema_dialogo.actualizar_y_dibujar(pantalla, eventos, estado_jugador)
        
    if BUSQUEDA_DIA_2 in sistema_mapa.eventos_completados:
        sistema_dialogo.dibujar_objetivo_global(pantalla, "Encuentra 3 pistas importantes")
    sistema_dialogo.dibujar_notificacion_global(pantalla)
    pygame.display.flip()
pygame.quit()
