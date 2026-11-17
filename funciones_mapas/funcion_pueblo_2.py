import sistema_mapa
import sistema_dialogo


CONVERSACIONES = {
    12: ("evento_pers_1_musico", "pers_1_repetir"),
    13: ("evento_pers_2_cocinera", "pers_2_repetir"),
    14: ("evento_pers_3_niño", "pers_3_repetir"),
    15: ("evento_pers_4_amargado", "pers_4_repetir"),
    16: ("evento_pers_5_borracho", "pers_5_repetir"),
    17: ("evento_pers_6_niña", "pers_6_repetir"),
}


def iniciar():
    sistema_dialogo.cargar_json("datos/pueblo_2.json")

    # Recuperar las conversaciones realizadas al volver al mapa.
    for casilla, (evento, repeticion) in CONVERSACIONES.items():
        marca = f"pueblo_2:{evento}"

        sistema_mapa.interactuables_activos[casilla] = (
            repeticion
            if marca in sistema_mapa.eventos_completados
            else evento
        )


def al_elegir_opcion(nombre_evento):
    for casilla, (evento, repeticion) in CONVERSACIONES.items():
        if nombre_evento == evento:
            sistema_mapa.eventos_completados.add(
                f"pueblo_2:{evento}"
            )

            sistema_mapa.interactuables_activos[casilla] = repeticion
            return


def actualizar():
    if not sistema_mapa.transicion_activa:
        sistema_mapa.jugador_bloqueado = False