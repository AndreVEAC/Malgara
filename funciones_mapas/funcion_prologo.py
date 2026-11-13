import sistema_mapa
import sistema_dialogo
from configuracion import TAMANO_CASILLA

esperas_desbloqueadas = set()

# MEMORIA PERSISTENTE DEL PRÓLOGO (Sobrevive al cambio de mapa)
progreso_lucas_guardado = {
    "x": None,
    "y": None,
    "direccion": "der",
    "pausado": False,
    "esperas": set()
}

def iniciar():
    global esperas_desbloqueadas

    sistema_dialogo.cargar_json("datos/prologo.json")
    sistema_mapa.eventos_completados.add("intro_completada")

    lucas = sistema_mapa.npcs_activos.get("lucas")

    if "prologo_completado" in sistema_mapa.eventos_completados:
        # Al regresar después de completarlo, Lucas ya no está.
        esperas_desbloqueadas = {9, 23, 37}

        if lucas:
            lucas["visible"] = False
            lucas["pausado"] = True
            lucas["_esperas_resueltas"] = esperas_desbloqueadas

        # Eliminar todos los triggers de conversaciones del prólogo.
        for fila in sistema_mapa.matriz_activa:
            for col, casilla in enumerate(fila):
                if casilla in (5, 6, 9):
                    fila[col] = 0

    elif progreso_lucas_guardado["x"] is not None:
        # Si regresa antes de completarlo, restaurar su progreso.
        esperas_desbloqueadas = set(
            progreso_lucas_guardado["esperas"]
        )

        if lucas:
            lx = progreso_lucas_guardado["x"]
            ly = progreso_lucas_guardado["y"]

            lucas["x"] = lx
            lucas["y"] = ly
            lucas["px_x"] = float(lx * TAMANO_CASILLA)
            lucas["px_y"] = float(ly * TAMANO_CASILLA)
            lucas["direccion"] = progreso_lucas_guardado["direccion"]
            lucas["pausado"] = progreso_lucas_guardado["pausado"]
            lucas["_esperas_resueltas"] = esperas_desbloqueadas

        # Quitar los triggers de encuentros ya resueltos.
        for fila in sistema_mapa.matriz_activa:
            if 9 in esperas_desbloqueadas and fila[9] == 5:
                fila[9] = 0

            if 23 in esperas_desbloqueadas and fila[23] == 6:
                fila[23] = 0

    else:
        # Primera entrada al prólogo.
        esperas_desbloqueadas.clear()


def actualizar():
    if "prologo_completado" in sistema_mapa.eventos_completados:
        return

    lucas = sistema_mapa.npcs_activos.get("lucas")
    if not lucas:
        return

    evento_activo = sistema_dialogo.obtener_evento_activo()
    lucas_x = lucas["x"]

    # Registrar el estado en tiempo real para que, si sale del mapa, se guarde aquí
    progreso_lucas_guardado["x"] = lucas["x"]
    progreso_lucas_guardado["y"] = lucas["y"]
    progreso_lucas_guardado["direccion"] = lucas["direccion"]
    progreso_lucas_guardado["pausado"] = lucas.get("pausado", False)
    progreso_lucas_guardado["esperas"] = set(esperas_desbloqueadas)

    if evento_activo == "evento_6":
        lucas["sprite_override"] = "foto"
    else:
        lucas["sprite_override"] = None

    lucas["pausado"] = (evento_activo is not None)

    if evento_activo is None:
        if lucas_x == 9 and 9 not in esperas_desbloqueadas:
            if sistema_mapa.matriz_activa[15][9] != 5:
                esperas_desbloqueadas.add(9)
                lucas.setdefault("_esperas_resueltas", set()).add(9)

        elif lucas_x == 23 and 23 not in esperas_desbloqueadas:
            if sistema_mapa.matriz_activa[15][23] != 6:
                esperas_desbloqueadas.add(23)
                lucas.setdefault("_esperas_resueltas", set()).add(23)

        elif lucas_x == 37:
            if sistema_mapa.matriz_activa[15][38] != 9:
                sistema_mapa.eventos_completados.add("prologo_completado")