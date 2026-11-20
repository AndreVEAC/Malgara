import pygame
import sistema_mapa as mapa
import sistema_dialogo as dialogo
from configuracion import TAMANO_CASILLA as T

MARCA = "estatua_noche_1_completada"
conversando = False
imagen_luz = None
posiciones_luces = []


def iniciar():
    global conversando, imagen_luz, posiciones_luces
    dialogo.cargar_json("datos/pueblo_2_noche_1.json")
    conversando = False
    if MARCA in mapa.eventos_completados:
        mapa.interactuables_activos[3] = "evento_estatua_noche_repetir"
    imagen_luz = pygame.image.load("recursos/sprites/efectos/luz_2.png").convert_alpha()
    imagen_luz = pygame.transform.scale(imagen_luz, (160, 160))
    imagen_luz.set_alpha(140)
    posiciones_luces = [((x+.5)*T, (y-2.5)*T)
                       for y,fila in enumerate(mapa.matriz_activa)
                       for x,numero in enumerate(fila) if numero == 20]
    mapa.npcs_activos["lucas"]["comportamiento"] = "sigue_jugador"
    mapa.npcs_activos["lucas"]["visible"] = True


def al_iniciar_dialogo(nombre_evento):
    global conversando
    if nombre_evento == "evento_estatua_noche" and MARCA not in mapa.eventos_completados:
        conversando = True


def actualizar():
    global conversando
    if mapa.transicion_activa:
        return
    # El motor informa del inicio; al cerrarse la última línea registramos el hecho.
    if conversando and dialogo.obtener_evento_activo() is None:
        mapa.eventos_completados.add(MARCA)
        mapa.interactuables_activos[3] = "evento_estatua_noche_repetir"
        conversando = False


def obtener_zonas_iluminadas():
    if imagen_luz is None:
        return []
    return [imagen_luz.get_rect(center=(round(x),round(y))) for x,y in posiciones_luces]


def dibujar_efectos(pantalla, camara_x, camara_y):
    if imagen_luz is None:
        return
    for zona in obtener_zonas_iluminadas():
        rect = zona.move(-camara_x, -camara_y)
        if pantalla.get_rect().colliderect(rect):
            pantalla.blit(imagen_luz, rect)
