"""Extensión del director de pueblo_1: no reemplaza tus luces ni tus NPCs."""
import json
import pygame
from reloj_juego import ahora_ms
import sistema_mapa as mapa
import sistema_dialogo as dialogo
import sistema_vigilancia as vigilancia
from configuracion import TAMANO_CASILLA as T

MARCA = "estatua_noche_1_completada"
MARCA_ESCENA = "pueblo_1_noche_1:regreso_cerrado_visto"
TRIGGER = {(31,14), (31,15)}  # Justo fuera de las vallas en pueblo_1.
GUARDIAS = ("custodio_casa_1", "custodio_casa_2", "custodio_casa_3")
estado = "INACTIVO"
inicio_pan = 0
origen_camara = (0,0)
destino_camara = (0,0)


def iniciar():
    global estado
    estado = "INACTIVO"
    
    print(
        "[DEBUG RETORNO] Estatua completada:",
        MARCA in mapa.eventos_completados,
    )
    
    if MARCA not in mapa.eventos_completados:
        return

    # Conservar los eventos actuales del director y añadir únicamente este diálogo.
    with open("datos/retorno_estatua_noche_1.json", encoding="utf-8") as archivo:
        dialogo.datos_dialogo.update(json.load(archivo))

    for nombre in ("loco_salida_arriba", "loco_salida_abajo", "loco_jardin"):
        if nombre in mapa.npcs_activos:
            mapa.npcs_activos[nombre]["visible"] = False

    # Recuperar el portal superior, eliminado cuando pusimos las primeras cajas.
    mapa.portales_activos[97] = {
        "mapa": "pueblo_2_noche_1", "spawn_x": 1, "spawn_y": 7,
    }
    for y in (6,7,8):
        mapa.matriz_activa[y][39] = 97
        mapa.bloqueos_activos.pop((39,y), None)

    # Cerrar de forma permanente la salida a casa. La caja hace visible el cierre.
    mapa.portales_activos.pop(96, None)
    mapa.matriz_activa[29][9] = 22

    molde = next(n for n in mapa.npcs_activos.values()
                 if n.get("comportamiento") == "vigilante")
    for nombre,x in zip(GUARDIAS,(8,9,10)):
        npc = molde.copy()
        npc.pop("_vigilancia", None)
        npc.update(x=x,y=28,px_x=float(x*T),px_y=float(28*T),
                   direccion="arriba",visible=True,congelado=True,pausado=True,
                   sprite_override=None,comportamiento="vigilante")
        npc["vigilancia"] = {"luz":"recursos/sprites/efectos/luz_3.png", "ruta":[]}
        mapa.npcs_activos[nombre] = npc

    estado = "JUGABLE" if MARCA_ESCENA in mapa.eventos_completados else "ESPERAR_SALIDA"


def _pan(ahora, desde, hasta):
    t = min(1.0, max(0.0, (ahora-inicio_pan)/1400))
    suave = t*t*(3-2*t)
    mapa.script_nivel_actual.CAMARA_CINEMATICA = tuple(
        a+(b-a)*suave for a,b in zip(desde,hasta))
    return t >= 1


def actualizar():
    """True: la escena consume el control y el director debe retornar."""
    global estado, inicio_pan, origen_camara, destino_camara
    if estado == "INACTIVO":
        return False
    director = mapa.script_nivel_actual
    if mapa.transicion_activa:
        return estado not in ("ESPERAR_SALIDA", "JUGABLE")
    ahora = ahora_ms()

    if estado == "ESPERAR_SALIDA":
        if (mapa.mateo_x,mapa.mateo_y) not in TRIGGER:
            return False
        if dialogo.obtener_evento_activo() is not None:
            return False
        origen_camara = mapa.calcular_camara()
        # Vista 800x600: mostrar la entrada situada en (9,29).
        destino_camara = (0, max(0,mapa.filas_mapa*T-600))
        director.CONTROL_CINEMATICO = True
        director.CAMARA_CINEMATICA = origen_camara
        mapa.jugador_bloqueado = True
        for npc in mapa.npcs_activos.values():
            npc["congelado"] = True
        inicio_pan = ahora
        estado = "PAN_IDA"

    elif estado == "PAN_IDA":
        if _pan(ahora,origen_camara,destino_camara):
            dialogo.iniciar_dialogo("evento_regreso_cerrado_noche1")
            if dialogo.obtener_evento_activo() is None:
                raise ValueError("Falta evento_regreso_cerrado_noche1")
            estado = "DIALOGO"

    elif estado == "DIALOGO":
        if dialogo.obtener_evento_activo() is None:
            inicio_pan = ahora
            estado = "PAN_VUELTA"

    elif estado == "PAN_VUELTA":
        if _pan(ahora,destino_camara,origen_camara):
            estado = "SOLTAR"

    elif estado == "SOLTAR":
        if not pygame.key.get_pressed()[pygame.K_SPACE]:
            director.CAMARA_CINEMATICA = None
            director.CONTROL_CINEMATICO = False
            mapa.jugador_bloqueado = False
            for nombre,npc in mapa.npcs_activos.items():
                npc["congelado"] = nombre in GUARDIAS
                npc["_tiempo_ultimo_paso"] = ahora
                if "_vigilancia" in npc:
                    npc["_vigilancia"]["ultimo_paso"] = ahora
            mapa.eventos_completados.add(MARCA_ESCENA)
            mapa.tiempo_ultima_interaccion = ahora
            mapa.tiempo_ultimo_paso_mateo = ahora
            estado = "JUGABLE"
        return True

    elif estado == "JUGABLE":
        # Permanecen en su puesto. Si Mateo entra en su visión, lo capturan.
        # No persiguen ni abandonan la entrada cuando otro loco da la alarma.
        if not mapa.jugador_bloqueado and dialogo.obtener_evento_activo() is None:
            for nombre in GUARDIAS:
                if vigilancia._ve_jugador(mapa,mapa.npcs_activos[nombre]):
                    mapa.jugador_bloqueado = True
                    mapa.cargar_nivel(mapa.nombre_mapa_actual)
                    return True
        return False
    return True
