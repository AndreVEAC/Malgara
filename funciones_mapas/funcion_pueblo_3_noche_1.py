import pygame
import sistema_mapa as mapa
import sistema_dialogo as dialogo
import sistema_audio as audio
import sistema_escondites as escondites
from funciones_mapas.escena_morales import (
    Director, Recorrido, colocar, mirar, cargar_linternas, linterna,
    MARCA_TENSION, MARCA_REGRESO)
from configuracion import TAMANO_CASILLA as T, ANCHO_PANTALLA, ALTO_PANTALLA

CONTROL_CINEMATICO = True
CAMARA_CINEMATICA = (0, 0)
director = None
luces = None
luz_poste = None
camara_sigue = False
revelado = False


def iniciar():
    global director, luces, luz_poste, camara_sigue, CAMARA_CINEMATICA, revelado
    mapa.jugador_bloqueado = True
    escondites.escondido = False
    audio.establecer_persecucion(False)
    dialogo.cargar_json('datos/pueblo_3_noche_1.json')
    CAMARA_CINEMATICA = (0, 0)
    camara_sigue = False
    revelado = False
    colocar('mateo',12,1,'abajo')
    colocar('lucas',13,1,'abajo')
    colocar('morales',12,-2,'abajo')
    mapa.npcs_activos['morales']['visible'] = False
    luces = cargar_linternas()
    luz_poste = pygame.image.load('recursos/sprites/efectos/luz_2.png').convert_alpha()
    luz_poste = pygame.transform.scale(luz_poste,(160,160))
    luz_poste.set_alpha(140)
    director = Director(_secuencia())


def _luz_aparece():
    # El cuerpo queda fuera del fondo; sólo entra el haz de luz desde arriba.
    colocar('morales',12,-1,'abajo')
    mapa.npcs_activos['morales']['visible'] = True
    mirar('mateo','der')
    mirar('lucas','der')


def _revelar():
    mapa.eventos_completados.add(MARCA_TENSION)
    audio.reproducir_ambiente('tension', .4, 600)


def _seguir():
    global camara_sigue
    camara_sigue = True


def _salir():
    mapa.eventos_completados.add(MARCA_REGRESO)
    mapa.eventos_completados.add('pueblo_3_noche_1:completado')
    mapa.cargar_nivel('casa_noche_1', 18, 18)


def _secuencia():
    global CAMARA_CINEMATICA
    yield 'mover', [Recorrido('mateo',[(12,5)]), Recorrido('lucas',[(13,5)])]
    yield 'pausa', 500
    yield 'dialogo', 'evento_morales_entrada'
    # Encuadre que incluye las cajas, la pareja y la entrada del mapa.
    CAMARA_CINEMATICA = (0,0)
    yield 'mover', [Recorrido('mateo',[(3,5)]), Recorrido('lucas',[(13,6),(3,6)])]
    yield 'pausa', 600
    yield 'dialogo', 'evento_morales_cajas'
    yield 'hacer', _luz_aparece
    yield 'pausa', 1400
    yield 'dialogo', 'evento_morales_luz'
    # Aproximación lenta. El cuerpo aparece antes de que se presente.
    yield 'mover', [Recorrido('morales',[(12,2)], 500)]
    yield 'pausa', 500
    yield 'dialogo', 'evento_morales_acercandose'
    yield 'mover', [Recorrido('morales',[(12,5),(5,5)], 350)]
    yield 'pausa', 650
    yield 'dialogo', 'evento_noche1_morales'
    yield 'hacer', _seguir
    # Morales va delante. Los otros toman el mismo recorrido con separación.
    yield 'mover', [
        Recorrido('morales',[(12,5),(12,18),(-3,18)],250),
        Recorrido('mateo',[(12,5),(12,18),(-2,18)],250,500),
        Recorrido('lucas',[(3,5),(12,5),(12,18),(-1,18)],250,1000),
    ]
    yield 'hacer', _salir


def actualizar():
    global CAMARA_CINEMATICA, revelado
    if mapa.transicion_activa: return
    morales = mapa.npcs_activos['morales']
    if not revelado and morales['visible'] and morales['px_y'] > -30:
        revelado = True
        _revelar()
    if camara_sigue:
        n = mapa.npcs_activos['morales']
        objetivo = (max(0,min(1000-ANCHO_PANTALLA,n['px_x']-ANCHO_PANTALLA/2)),
                    max(0,min(1200-ALTO_PANTALLA,mapa.mateo_px_y-ALTO_PANTALLA/2)))
        CAMARA_CINEMATICA = tuple(a+(b-a)*.08 for a,b in zip(CAMARA_CINEMATICA,objetivo))
    director.actualizar()


def dibujar_efectos(pantalla, camara_x, camara_y):
    if luz_poste is not None:
        for y, fila in enumerate(mapa.matriz_activa):
            for x, valor in enumerate(fila):
                if valor == 20:
                    pantalla.blit(luz_poste,luz_poste.get_rect(center=(round((x+.5)*T-camara_x),round((y-2.5)*T-camara_y))))
    if luces is not None: linterna(pantalla,luces,'morales',camara_x,camara_y)
