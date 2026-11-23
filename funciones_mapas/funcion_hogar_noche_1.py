import sistema_escondites as escondites
import sistema_audio as audio
import sistema_mapa as mapa
import sistema_guardado
from funciones_mapas import final_noche_1 as final_noche
from funciones_mapas.escena_morales import MARCA_TENSION, sonido

CENTRAR_FONDO = True
CONTROL_CINEMATICO = False
sonido_cerrar = None


def iniciar():
    global CONTROL_CINEMATICO, sonido_cerrar
    mapa.jugador_bloqueado = False
    escondites.escondido = False
    CONTROL_CINEMATICO = final_noche.iniciar_hogar()

    if not CONTROL_CINEMATICO:
        mapa.direccion_mateo = (
            'abajo' if (mapa.mateo_x,mapa.mateo_y)==(1,2) else 'arriba'
        )

    if not sistema_guardado.cargando:
        sonido_cerrar = sonido('close_door')


def actualizar():
    global CONTROL_CINEMATICO
    if CONTROL_CINEMATICO:
        final_noche.actualizar()
        CONTROL_CINEMATICO = final_noche.en_curso


def obtener_ambiente():
    if MARCA_TENSION in mapa.eventos_completados:
        return 'tension'
    return audio.pista_actual
