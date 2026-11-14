# funciones_mapas/funcion_pueblo_1.py

import sistema_mapa
import sistema_dialogo


CONVERSACIONES = {
    10: ("evento_fuente", "fuente_repetir"),
    12: ("evento_pers_1", "pers_1_repetir"),
    13: ("evento_pers_2", "pers_2_repetir"),
    14: ("evento_pers_3", "pers_3_repetir"),
    15: ("evento_pers_4", "pers_4_repetir"),
    16: ("evento_pers_5", "pers_5_repetir"),
    17: ("evento_pers_6", "pers_6_repetir"),
}


def iniciar():
    sistema_dialogo.cargar_json("datos/pueblo_1.json")

    for casilla, (evento, repeticion) in CONVERSACIONES.items():
        marca = f"pueblo_1:{evento}"

        sistema_mapa.interactuables_activos[casilla] = (
            repeticion
            if marca in sistema_mapa.eventos_completados
            else evento
        )


def actualizar():
    # Sin movimientos ni cinemáticas en este director por ahora.
    pass


def al_elegir_opcion(nombre_evento):
    """Registrar la primera elección de cada conversación."""
    for casilla, (evento, repeticion) in CONVERSACIONES.items():
        if nombre_evento == evento:
            sistema_mapa.eventos_completados.add(
                f"pueblo_1:{evento}"
            )
            sistema_mapa.interactuables_activos[casilla] = repeticion
            return