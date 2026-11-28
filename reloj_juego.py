"""Reloj de la partida que se detiene durante la pausa."""
import pygame


inicio_pausa = None
tiempo_pausado = 0


def ahora_ms():
    instante = pygame.time.get_ticks() if inicio_pausa is None else inicio_pausa
    return instante - tiempo_pausado


def pausar():
    global inicio_pausa
    if inicio_pausa is None:
        inicio_pausa = pygame.time.get_ticks()


def reanudar():
    global inicio_pausa, tiempo_pausado
    if inicio_pausa is not None:
        tiempo_pausado += pygame.time.get_ticks() - inicio_pausa
        inicio_pausa = None
