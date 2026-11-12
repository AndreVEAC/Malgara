import sistema_mapa
import sistema_dialogo

esperas_desbloqueadas = set()

def iniciar():
    global esperas_desbloqueadas
    esperas_desbloqueadas.clear()
    sistema_dialogo.cargar_json("datos/prologo.json")


def actualizar():
    # Obtenemos al NPC "lucas" del sistema genérico de mapas
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

    # 3. RESOLVER PUNTOS DE ESPERA (x=9, x=23)
    # Cuando Mateo pisa el trigger, el evento de diálogo inicia y el número 5, 6 o 9 
    # desaparece de la matriz (se borra en sistema_mapa al pisarlo).
    # Cuando el evento termina (evento_activo is None), revisamos si ya pasó el trigger
    # y agregamos esa X a "_esperas_resueltas", lo que permite a sistema_npc continuar.
    if evento_activo is None:
        
        # Lucas esperaba en x=9 (relacionado al trigger 5)
        if lucas_x == 9 and 9 not in esperas_desbloqueadas:
            if sistema_mapa.matriz_activa[15][9] != 5: # Si ya no está el trigger en el suelo
                esperas_desbloqueadas.add(9)
                lucas.setdefault("_esperas_resueltas", set()).add(9)

        # Lucas esperaba en x=23 (relacionado al trigger 6)
        elif lucas_x == 23 and 23 not in esperas_desbloqueadas:
            if sistema_mapa.matriz_activa[15][23] != 6: # Si ya no está el trigger en el suelo
                esperas_desbloqueadas.add(23)
                lucas.setdefault("_esperas_resueltas", set()).add(23)