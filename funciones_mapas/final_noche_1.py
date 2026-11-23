"""Conversación con Morales y cierre provisional de la primera noche."""
import pygame
import sistema_mapa as mapa
import sistema_dialogo as dialogo
import sistema_audio as audio
import sistema_escondites as escondites
import sistema_guardado
from funciones_mapas.escena_morales import (
    Director, Recorrido, crear_npc, colocar, mirar, sonido,
    MARCA_HOGAR, MARCA_TENSION,
)

MORALES_SALIO = 'morales_noche_1:salio_de_hogar'
HOGAR_COMPLETADO = 'noche_1:conversacion_hogar_completada'
HABITACION_PENDIENTE = 'noche_1:conversacion_habitacion_pendiente'
FINAL_COMPLETADO = 'noche_1:conversacion_final_completada'

# La ventana está en (5,7); Morales se coloca enfrente y mira hacia abajo.
POSICION_MORALES = (5, 6)
POSICION_LUCAS = (7, 2)
POSICION_MATEO = (0, 4)
CAMA_MATEO = (0, 3)
CAMA_LUCAS = (4, 3)

en_curso = False
director = None
canal_puerta = None


def iniciar_hogar():
    global en_curso, director, canal_puerta
    en_curso = False
    director = None
    canal_puerta = None
    if MARCA_HOGAR not in mapa.eventos_completados:
        return False
    if HOGAR_COMPLETADO in mapa.eventos_completados:
        # Morales ya salió. Lucas permanece en su habitación al volver a hogar.
        return False

    mapa.jugador_bloqueado = True
    escondites.escondido = False
    en_curso = True
    colocar('mateo',8,6,'arriba')
    crear_npc('lucas','lucas',6,6,'arriba')
    crear_npc('morales','morales',5,5,'abajo')
    dialogo.cargar_json('datos/hogar_noche_1.json')
    if MORALES_SALIO in mapa.eventos_completados:
        # Reanudar tras una salida ya registrada, sin resucitar a Morales.
        mapa.npcs_activos['morales']['visible'] = False
        colocar('mateo',*POSICION_MATEO,'der')
        colocar('lucas',*POSICION_LUCAS,'abajo')
        director = Director(_despues_morales())
    else:
        director = Director(_secuencia_hogar())
    return True


def _orientar_conversacion():
    mirar('morales','abajo')
    mirar('lucas','abajo')
    mirar('mateo','der')


def _abrir():
    global canal_puerta
    canal_puerta = sonido('open_door')


def _cerrar():
    global canal_puerta
    canal_puerta = sonido('close_door')


def _esperar_sonido():
    # Esperas breves no bloqueantes: la ventana sigue procesando eventos.
    while canal_puerta is not None and canal_puerta.get_busy():
        yield 'pausa', 50


def _ocultar_morales():
    mapa.npcs_activos['morales']['visible'] = False
    mapa.eventos_completados.add(MORALES_SALIO)


def _secuencia_hogar():
    yield 'pausa', 400
    # Lucas rodea la mesa por la izquierda hasta el espacio bajo la cocina.
    yield 'mover', [Recorrido('lucas',[(6,5),(5,5),(5,2),POSICION_LUCAS])]
    yield 'hacer', lambda: mirar('lucas','abajo')
    # Mateo alcanza el sillón desde su lado derecho; Morales queda en la ventana.
    yield 'mover', [
        Recorrido('morales',[POSICION_MORALES]),
        Recorrido('mateo',[(6,6),(6,5),(4,5),(1,5),(1,4),POSICION_MATEO]),
    ]
    yield 'hacer', _orientar_conversacion
    yield 'pausa', 500
    yield 'dialogo', 'evento_casa_regreso_morales'
    # "Lo tendremos": termina la conversación y Morales se dirige a la puerta.
    yield 'mover', [Recorrido('morales',[(8,6)])]
    yield 'hacer', _abrir
    yield 'mover', [Recorrido('morales',[(8,7)])]
    yield 'hacer', _ocultar_morales
    yield from _esperar_sonido()
    yield 'hacer', _cerrar
    yield from _esperar_sonido()
    yield from _despues_morales()


def _despues_morales():
    yield 'pausa', 2000
    yield 'dialogo', 'evento_hogar_despues_morales'
    # Lucas va primero. Ambos atraviesan la puerta superior, sin pisar muebles.
    yield 'mover', [
        Recorrido('lucas',[(1,2)]),
        Recorrido('mateo',[(1,4),(1,3)],250,1900),
    ]
    # Evitar superponerlos al entrar: uno cruza, el otro espera detrás.
    yield 'hacer', _abrir
    yield 'mover', [Recorrido('lucas',[(1,1)])]
    yield 'hacer', lambda: mapa.npcs_activos['lucas'].update(visible=False)
    yield 'mover', [Recorrido('mateo',[(1,1)])]
    yield from _esperar_sonido()
    yield 'hacer', _cambiar_a_habitacion


def _cambiar_a_habitacion():
    mapa.eventos_completados.add(HOGAR_COMPLETADO)
    mapa.eventos_completados.add(HABITACION_PENDIENTE)
    # Aunque se pruebe la escena sin jugar la alarma, no volver a activarla.
    mapa.eventos_completados.add('habitaciones_noche_1:inicio_completado')
    mapa.cargar_nivel('habitaciones_noche_1',2,3)


def iniciar_habitaciones():
    global en_curso, director, canal_puerta
    en_curso = False
    director = None
    canal_puerta = None
    pendiente = HABITACION_PENDIENTE in mapa.eventos_completados
    terminada = FINAL_COMPLETADO in mapa.eventos_completados
    if not pendiente and not terminada:
        return False  # Se conserva la escena original de alarma y salida de Lucas.

    escondites.escondido = False
    mapa.eventos_completados.add('habitaciones_noche_1:inicio_completado')
    if MARCA_TENSION in mapa.eventos_completados:
        audio.reproducir_ambiente('tension', .4)
    crear_npc('lucas','lucas',*CAMA_LUCAS,'izq')
    if not sistema_guardado.cargando:
        canal_puerta = sonido('close_door')

    if terminada:
        mapa.jugador_bloqueado = False
        return True

    en_curso = True
    mapa.jugador_bloqueado = True
    colocar('mateo',2,3,'arriba')
    colocar('lucas',2,4,'arriba')
    dialogo.cargar_json('datos/habitaciones_noche_1_final.json')
    director = Director(_secuencia_habitacion())
    return True


def _secuencia_habitacion():
    yield from _esperar_sonido()
    yield 'mover', [
        Recorrido('mateo',[CAMA_MATEO]),
        Recorrido('lucas',[(3,4),(3,3),CAMA_LUCAS]),
    ]
    yield 'hacer', lambda: mirar('mateo','der')
    yield 'hacer', lambda: mirar('lucas','izq')
    yield 'pausa', 500
    yield 'dialogo', 'evento_habitaciones_duda_morales'
    yield 'hacer', _terminar


def _terminar():
    global en_curso
    mapa.eventos_completados.discard(HABITACION_PENDIENTE)
    mapa.eventos_completados.add(FINAL_COMPLETADO)
    mapa.jugador_bloqueado = False
    en_curso = False
    # Cierre provisional: no dormir automáticamente ni cargar el día 2.


def actualizar():
    if en_curso and director is not None:
        director.actualizar()
