import sys

import pygame
from pygame.locals import QUIT
from configuracion import ANCHO_PANTALLA, ALTO_PANTALLA, TITULO_JUEGO, FPS
from estado import BUSQUEDA_DIA_2, EstadoJuego
import sistema_mapa
import sistema_dialogo
import sistema_guardado
from funciones_mapas.investigacion_dia_2 import Investigacion, objetivo

pygame.init()
pantalla = pygame.display.set_mode((ANCHO_PANTALLA, ALTO_PANTALLA))
pygame.display.set_caption(TITULO_JUEGO)
reloj = pygame.time.Clock()

estado_jugador = EstadoJuego()
modo_juego = "EXPLORACION"

investigacion = Investigacion(estado_jugador, autoguardar="--prueba-dia-2" not in sys.argv)
if "--prueba-dia-2" in sys.argv:
    sistema_mapa.eventos_completados.add(BUSQUEDA_DIA_2)
    if "--captura" in sys.argv or "--rescate" in sys.argv:
        estado_jugador.sospecha_pueblo = 99
        estado_jugador.confianza_morales = 65 if "--rescate" in sys.argv else 64
    sistema_mapa.cargar_nivel("pueblo_2_dia_2", 38, 15)
elif "--continuar" not in sys.argv or not sistema_guardado.continuar(estado_jugador):
    sistema_mapa.cargar_nivel("iglesia_dia2")

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
        nuevo_modo = sistema_mapa.actualizar_y_dibujar(pantalla, estado_jugador, investigacion)
        
        # Si sistema_mapa dice que pisamos un evento, cambiamos de modo
        if nuevo_modo != modo_juego:
            modo_juego = nuevo_modo

    elif modo_juego == "DIALOGO":
        
        sistema_mapa.solo_dibujar(pantalla)
        # 2. SE ELIMINÓ EL REGRESO FORZADO A EXPLORACIÓN
        # sistema_dialogo se encarga de devolver "EXPLORACION" por sí solo al terminar de leer el JSON
        modo_juego = sistema_dialogo.actualizar_y_dibujar(pantalla, eventos, estado_jugador)
        
    rotulo = objetivo(estado_jugador)
    if rotulo:
        sistema_dialogo.dibujar_objetivo_global(pantalla, rotulo)
    sistema_dialogo.dibujar_notificacion_global(pantalla)
    pygame.display.flip()
pygame.quit()
