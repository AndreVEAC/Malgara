import sistema_audio as audio
import sistema_dialogo as dialogo
import sistema_mapa as mapa
from mapas import intro_dia_2 as intro


MARCA_RADIO = "intro_dia_2:radio_encendida"
notificacion_pendiente = False


def iniciar():
    global notificacion_pendiente

    dialogo.cargar_json("datos/intro_dia_2.json")
    notificacion_pendiente = False
    if MARCA_RADIO in mapa.eventos_completados:
        _desactivar_interaccion()


def obtener_ambiente():
    return "triste" if MARCA_RADIO in mapa.eventos_completados else intro.AMBIENTE


def actualizar():
    global notificacion_pendiente

    if notificacion_pendiente and dialogo.obtener_evento_activo() is None:
        dialogo.activar_notificacion("mateo cae en depresion")
        notificacion_pendiente = False


def al_elegir_opcion(evento):
    global notificacion_pendiente

    if evento != "evento_radio":
        return
    opcion = dialogo.opciones_actuales[dialogo.opcion_seleccionada]
    if opcion.get("accion") == "encender_radio":
        mapa.eventos_completados.add(MARCA_RADIO)
        _desactivar_interaccion()
        audio.reproducir_ambiente("triste", volumen=intro.VOLUMEN_AMBIENTE, fade_ms=0)
        notificacion_pendiente = True


def _desactivar_interaccion():
    for x, y in intro.RADIO:
        mapa.matriz_activa[y][x] = 1
