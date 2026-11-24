import pygame

import sistema_dialogo as dialogo
import sistema_guardado
from mapas import hogar


CENTRAR_FONDO = hogar.CENTRAR_FONDO
REGION_LIBRETA = pygame.Rect(332, 124, 16, 17)
libreta = None


def iniciar():
    global libreta

    dialogo.cargar_json("datos/hogar_dia2.json")
    if libreta is None:
        fondo_original = pygame.image.load(hogar.FONDO_IMG)
        libreta = fondo_original.subsurface(REGION_LIBRETA).convert()


def dibujar_efectos(pantalla, camara_x, camara_y):
    pantalla.blit(libreta, REGION_LIBRETA.move(-camara_x, -camara_y))


def al_elegir_opcion(nombre_evento):
    if nombre_evento != "hogar_libreta":
        return

    eleccion = dialogo.opciones_actuales[dialogo.opcion_seleccionada]
    if eleccion.get("accion") == "guardar_partida":
        sistema_guardado.solicitar("manual")
