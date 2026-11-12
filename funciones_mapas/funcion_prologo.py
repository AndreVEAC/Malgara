import sistema_mapa
import sistema_dialogo
from configuracion import TAMANO_CASILLA

esperas_desbloqueadas = set()


def iniciar():
    global esperas_desbloqueadas
    esperas_desbloqueadas.clear()
    sistema_dialogo.cargar_json("datos/prologo.json")

    # Garantiza que intro no se dispare al retroceder, incluso iniciando pruebas aquí
    sistema_mapa.eventos_completados.add("intro_completada")

    lucas = sistema_mapa.npcs_activos.get("lucas")

    # Si el prólogo ya se completó (ej. Mateo regresa desde 'llegada'):
    if "prologo_completado" in sistema_mapa.eventos_completados:
        # 1. Limpiar triggers de pisar (5, 6, 9) de la matriz para que no se repitan
        for fila in range(sistema_mapa.filas_mapa):
            for col in range(sistema_mapa.columnas_mapa):
                if sistema_mapa.matriz_activa[fila][col] in (5, 6, 9):
                    sistema_mapa.matriz_activa[fila][col] = 0

        # 2. Colocar a Lucas directamente al final del camino (x=37) y detener su patrulla
        if lucas:
            lucas["x"] = 37
            lucas["y"] = 15
            lucas["px_x"] = float(37 * TAMANO_CASILLA)
            lucas["px_y"] = float(15 * TAMANO_CASILLA)
            lucas["direccion"] = "der"
            lucas["pausado"] = True
            lucas["_esperas_resueltas"] = {9, 23, 37}


def actualizar():
    # Si el prólogo ya terminó en una visita anterior, no ejecutar lógica narrativa
    if "prologo_completado" in sistema_mapa.eventos_completados:
        return

    lucas = sistema_mapa.npcs_activos.get("lucas")
    if not lucas:
        return

    evento_activo = sistema_dialogo.obtener_evento_activo()
    lucas_x = lucas["x"]

    # 1. GESTIÓN DE SPRITE: Cambiamos a la foto solo si el evento_6 está corriendo
    if evento_activo == "evento_6":
        lucas["sprite_override"] = "foto"
    else:
        lucas["sprite_override"] = None

    # 2. PAUSAR PATRULLA: Si hay CUALQUIER diálogo activo, Lucas se queda quieto
    lucas["pausado"] = (evento_activo is not None)

    # 3. RESOLVER PUNTOS DE ESPERA (x=9, x=23) Y MARCAR FIN DEL PRÓLOGO (x=37)
    if evento_activo is None:
        # Lucas esperaba en x=9 (relacionado al trigger 5)
        if lucas_x == 9 and 9 not in esperas_desbloqueadas:
            if sistema_mapa.matriz_activa[15][9] != 5:
                esperas_desbloqueadas.add(9)
                lucas.setdefault("_esperas_resueltas", set()).add(9)

        # Lucas esperaba en x=23 (relacionado al trigger 6)
        elif lucas_x == 23 and 23 not in esperas_desbloqueadas:
            if sistema_mapa.matriz_activa[15][23] != 6:
                esperas_desbloqueadas.add(23)
                lucas.setdefault("_esperas_resueltas", set()).add(23)

        # Lucas llegó al final (x=37) y el evento_9 ya se pisó y terminó
        elif lucas_x == 37:
            if sistema_mapa.matriz_activa[15][38] != 9:
                sistema_mapa.eventos_completados.add("prologo_completado")