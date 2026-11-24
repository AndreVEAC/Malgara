import sistema_dialogo as dialogo
import sistema_mapa as mapa
from estado import BUSQUEDA_DIA_2
from funciones_mapas.escena_morales import Director, Recorrido, mirar


MARCA = "casa_dia2:salida_completada"
director = None


def iniciar():
    global director

    dialogo.cargar_json("datos/casa_dia2.json")
    director = None
    if MARCA in mapa.eventos_completados or BUSQUEDA_DIA_2 in mapa.eventos_completados:
        mapa.npcs_activos["lucas"]["visible"] = False
        return

    mapa.jugador_bloqueado = True
    mirar("mateo", "izq")
    director = Director(_secuencia())


def actualizar():
    if director is not None:
        director.actualizar()


def _secuencia():
    yield "dialogo", "evento_lucas_casa"
    yield "mover", [
        Recorrido("lucas", [(16, 18), (19, 18)], intervalo=220),
        Recorrido("mateo", [(17, 17), (17, 18), (18, 18)], intervalo=220, retraso=375),
    ]
    yield "hacer", _ir_a_iglesia


def _ir_a_iglesia():
    mapa.eventos_completados.add(MARCA)
    mapa.cargar_nivel("iglesia_dia2")
