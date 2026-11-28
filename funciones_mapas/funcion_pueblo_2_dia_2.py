import sistema_dialogo as dialogo
import sistema_mapa as mapa
from mapas import pueblo_2_dia_2 as pueblo


MARCA_ALTAR = "pueblo_2_dia_2:altar_ausente"


def iniciar():
    dialogo.cargar_json("datos/pueblo_2_dia_2.json")
    if MARCA_ALTAR in mapa.eventos_completados:
        _limpiar_altar()


def al_iniciar_dialogo(evento):
    if evento == "evento_altar_ausente":
        mapa.eventos_completados.add(MARCA_ALTAR)
        _limpiar_altar()


def _limpiar_altar():
    for x, y in pueblo.ZONA_ALTAR:
        mapa.matriz_activa[y][x] = 0
