import pygame

import sistema_dialogo as dialogo
import sistema_mapa as mapa
from configuracion import TAMANO_CASILLA
from funciones_mapas.luces_noche_2 import dibujar_efectos, iniciar as iniciar_luces, obtener_zonas_iluminadas
from mapas.casa_noche_2 import GUARDIAS_CAMINO_NORTE, LIMITE_CAMINO_NORTE, POSTES, cerrar_camino
from mapas.geografia_noche_2 import marcar

DURACION_ENCUADRE = 760
AUMENTO = 1.45
inicio_encuadre = None
acercando = False
CAMARA_CINEMATICA = None
camara_origen = None
revision_camino = -1


def iniciar():
    global inicio_encuadre, acercando, CAMARA_CINEMATICA, camara_origen
    iniciar_luces()
    dialogo.datos_dialogo["n2_camino_norte_vigilado"] = {
        "lineas": [{"hablante": "Mateo", "texto": "Si me acerco más, me van a ver."}],
    }
    inicio_encuadre = None
    acercando = False
    CAMARA_CINEMATICA = camara_origen = None


def al_intentar_paso_bloqueado(x, y, estado):
    evento = "n2_camino_norte_vigilado"
    consumidos = estado.noche2["consumidos"]
    if y == LIMITE_CAMINO_NORTE and mapa.mateo_y > y and evento not in consumidos:
        consumidos.add(evento)
        dialogo.iniciar_dialogo(evento)
        return True
    return False


def actualizar_estado(estado):
    global revision_camino
    if revision_camino != mapa.revision_nivel:
        revision_camino = mapa.revision_nivel
        marcar(mapa.matriz_activa, POSTES, 20)
        cerrar_camino(mapa.matriz_activa)


def enfocar():
    global camara_origen
    camara_origen = mapa.calcular_camara()
    _iniciar_encuadre(True)


def desenfocar():
    _iniciar_encuadre(False)


def _iniciar_encuadre(entrada):
    global inicio_encuadre, acercando
    inicio_encuadre = pygame.time.get_ticks()
    acercando = entrada


def intensidad_encuadre():
    if inicio_encuadre is None:
        return 0
    avance = min(1, (pygame.time.get_ticks() - inicio_encuadre) / DURACION_ENCUADRE)
    avance = avance * avance * (3 - 2 * avance)
    return avance if acercando else 1 - avance


def actualizar():
    global CAMARA_CINEMATICA
    intensidad = intensidad_encuadre()
    if camara_origen is None or intensidad <= 0:
        CAMARA_CINEMATICA = None
    else:
        x, y = camara_origen
        CAMARA_CINEMATICA = (x, y * (1 - intensidad))


def aplicar_encuadre(pantalla, camara_x, camara_y):
    intensidad = intensidad_encuadre()
    if intensidad <= 0:
        return
    vista = pantalla.get_rect()
    escala = 1 + (AUMENTO - 1) * intensidad
    x = (sum(x for x, _ in GUARDIAS_CAMINO_NORTE) / len(GUARDIAS_CAMINO_NORTE) + .5) * TAMANO_CASILLA
    y = (GUARDIAS_CAMINO_NORTE[0][1] + .5) * TAMANO_CASILLA
    centro = pygame.Vector2(vista.center).lerp((x - camara_x, y - camara_y), intensidad)
    recorte = pygame.Rect(0, 0, round(vista.width / escala), round(vista.height / escala))
    recorte.center = centro
    recorte.clamp_ip(vista)
    pantalla.blit(pygame.transform.scale(pantalla.subsurface(recorte), vista.size), (0, 0))
