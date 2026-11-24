import sistema_dialogo as dialogo
import sistema_guardado as guardado
import sistema_mapa as mapa
from estado import BUSQUEDA_DIA_2
from mapas import pueblo_2_dia_2 as pueblo


MARCA_ALTAR = "pueblo_2_dia_2:altar_ausente"
MARCA_VISITAR_ABUELA = "pueblo_2_dia_2:visitar_abuela"
visita_pendiente = False


def iniciar():
    global visita_pendiente

    dialogo.cargar_json("datos/pueblo_2_dia_2.json")
    visita_pendiente = (
        not guardado.cargando
        and BUSQUEDA_DIA_2 in mapa.eventos_completados
        and MARCA_VISITAR_ABUELA not in mapa.eventos_completados
        and (mapa.mateo_x, mapa.mateo_y) == (pueblo.INICIO_X, pueblo.INICIO_Y)
    )
    if MARCA_ALTAR in mapa.eventos_completados:
        _limpiar_altar()


def actualizar():
    global visita_pendiente

    if visita_pendiente and not mapa.transicion_activa:
        visita_pendiente = False
        mapa.eventos_completados.add(MARCA_VISITAR_ABUELA)
        dialogo.iniciar_dialogo("evento_visitar_abuela")


def al_iniciar_dialogo(evento):
    if evento == "evento_altar_ausente":
        mapa.eventos_completados.add(MARCA_ALTAR)
        _limpiar_altar()


def _limpiar_altar():
    for x, y in pueblo.ZONA_ALTAR:
        mapa.matriz_activa[y][x] = 0
