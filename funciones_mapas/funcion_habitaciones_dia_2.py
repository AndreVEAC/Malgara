import sistema_dialogo as dialogo
import sistema_mapa as mapa

from mapas import habitaciones_dia_2


CENTRAR_FONDO = True


def iniciar():
    dialogo.cargar_json("datos/habitaciones_dia_2.json")
    if (mapa.mateo_x, mapa.mateo_y) == (
        habitaciones_dia_2.INICIO_X,
        habitaciones_dia_2.INICIO_Y,
    ):
        mapa.direccion_mateo = "der"
