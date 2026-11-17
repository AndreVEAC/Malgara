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
    
    # Tras la bienvenida, entrar directamente al pueblo explorable.
    if "bienvenida_pueblo_completada" in sistema_mapa.eventos_completados:
        for numero, portal in list(sistema_mapa.portales_activos.items()):
            if portal["mapa"] == "pueblo_2_cinematica":
                sistema_mapa.portales_activos[numero] = {
                    **portal,
                    "mapa": "pueblo_2",
            }
    
    if (
        "bienvenida_pueblo_completada"
        in sistema_mapa.eventos_completados
    ):
        comentarios = {
            "evento_casa": "Son muy hogareñas",
            "evento_flores": "Quizá podamos volver a comprar algo después.",
            "evento_botica": "Por suerte, ahora no necesitamos nada.",
            "evento_panaderia": "Podemos volver cuando nos dé hambre.",
            "evento_sastreria": "De momento no necesito ropa nueva.",
        }

        for nombre_evento, comentario in comentarios.items():
            evento = sistema_dialogo.datos_dialogo.get(nombre_evento)

            if evento and evento.get("lineas"):
                # Conservar la descripción inicial del edificio.
                descripcion = evento["lineas"][0]

                evento["lineas"] = [
                    descripcion,
                    {
                        "hablante": "Mateo",
                        "texto": comentario
                    }
                ]

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