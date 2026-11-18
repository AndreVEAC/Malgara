# funciones_mapas/funcion_casa.py

import sistema_mapa
import sistema_dialogo
from mapas import casa


CONVERSACIONES = {
    12: ("evento_niña_aro", "niña_repetir"),
    13: ("evento_banca_rayada", "banca_repetir"),
    14: ("evento_vecino", "vecino_repetir"),
    15: ("evento_tronco_zapatos", "tronco_repetir"),
}

EVENTO_PUERTA = "evento_casa_puerta"
MARCA_PUERTA = "casa:puerta_habilitada"

conversacion_pendiente = None


def iniciar():
    global conversacion_pendiente

    conversacion_pendiente = None
    sistema_dialogo.cargar_json("datos/casa.json")

    # Recuperar conversaciones realizadas en visitas anteriores.
    for casilla, (evento, repeticion) in CONVERSACIONES.items():
        marca = f"casa:{evento}"

        sistema_mapa.interactuables_activos[casilla] = (
            repeticion
            if marca in sistema_mapa.eventos_completados
            else evento
        )

    # Recuperar el estado de la puerta.
    if MARCA_PUERTA in sistema_mapa.eventos_completados:
        _habilitar_puerta()


def al_iniciar_dialogo(nombre_evento):
    """Recordar qué conversación comenzó mediante la interacción."""
    global conversacion_pendiente

    if nombre_evento == EVENTO_PUERTA:
        conversacion_pendiente = nombre_evento
        return

    for evento, repeticion in CONVERSACIONES.values():
        if nombre_evento == evento:
            conversacion_pendiente = nombre_evento
            return


def actualizar():
    global conversacion_pendiente

    if conversacion_pendiente is None:
        return

    # Esperar a que termine el diálogo, incluidas sus respuestas.
    if sistema_dialogo.obtener_evento_activo() is not None:
        return

    evento_terminado = conversacion_pendiente
    conversacion_pendiente = None

    if evento_terminado == EVENTO_PUERTA:
        sistema_mapa.eventos_completados.add(MARCA_PUERTA)
        _habilitar_puerta()
        return

    for casilla, (evento, repeticion) in CONVERSACIONES.items():
        if evento_terminado == evento:
            sistema_mapa.eventos_completados.add(
                f"casa:{evento}"
            )
            sistema_mapa.interactuables_activos[casilla] = (
                repeticion
            )
            return


def _habilitar_puerta():
    # Cambiar la casilla interactuable por el portal.
    sistema_mapa.matriz_activa[casa.PUERTA_Y][casa.PUERTA_X] = 97