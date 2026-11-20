# funciones_mapas/funcion_pueblo_1_noche_1.py
import importlib.util
import pygame
import sistema_mapa as mapa
import sistema_dialogo as dialogo
from funciones_mapas import retorno_estatua_noche_1 as retorno_estatua
from mapas import pueblo_1_noche_1 as datos
from configuracion import TAMANO_CASILLA as T

MARCA_INICIO = "pueblo_1_noche_1:introduccion_completada"
CONTROL_CINEMATICO = False
estado_escena = "INICIO"
imagen_luz = None
imagen_barril = None
posiciones_luces = []
TAMANO_LUZ = (160, 160)
OPACIDAD_LUZ = 140


def iniciar():
    global CONTROL_CINEMATICO, estado_escena
    global imagen_luz, imagen_barril, posiciones_luces

    dialogo.cargar_json("datos/pueblo_1_noche_1.json")
    posiciones_luces = [
        ((x + 0.5) * T, (y - 3 + 0.5) * T)
        for y, fila in enumerate(mapa.matriz_activa)
        for x, numero in enumerate(fila) if numero == 20
    ]
    imagen_luz = pygame.image.load(
        "recursos/sprites/efectos/luz_2.png"
    ).convert_alpha()
    imagen_luz = pygame.transform.scale(imagen_luz, TAMANO_LUZ)
    imagen_luz.set_alpha(OPACIDAD_LUZ)

    # El motor todavía no ha cargado el nuevo fondo cuando llama iniciar().
    # Cargarlo aquí para copiar un barril existente sin necesitar otro sprite.
    fondo = pygame.image.load(datos.FONDO_IMG).convert()
    imagen_barril = fondo.subsurface(datos.RECORTE_BARRIL).copy()

    # Bloquear visualmente las salidas cuyos destinos todavía no existen.
    # Solo modificar las copias activas, nunca datos.MATRIZ ni datos.PORTALES.
    for numero, portal in list(mapa.portales_activos.items()):
        if importlib.util.find_spec(f"mapas.{portal['mapa']}") is None:
            for fila in mapa.matriz_activa:
                for x, valor in enumerate(fila):
                    if valor == numero:
                        fila[x] = 22
            del mapa.portales_activos[numero]
            print(f"[MAPA] Salida cerrada: falta mapas/{portal['mapa']}.py")

    lucas = mapa.npcs_activos["lucas"]
    lucas["visible"] = True
    lucas["sprite_override"] = None
    lucas["comportamiento"] = "sigue_jugador"

    CONTROL_CINEMATICO = MARCA_INICIO not in mapa.eventos_completados
    mapa.jugador_bloqueado = CONTROL_CINEMATICO
    estado_escena = "ESPERAR_ENTRADA" if CONTROL_CINEMATICO else "JUGABLE"

    if CONTROL_CINEMATICO:
        mapa.direccion_mateo = "arriba"
        lucas["direccion"] = "arriba"
        for npc in mapa.npcs_activos.values():
            if npc.get("comportamiento") == "vigilante":
                npc["congelado"] = True
                
    retorno_estatua.iniciar()


def actualizar():
    global CONTROL_CINEMATICO, estado_escena
    
    if retorno_estatua.actualizar():
        return

    if mapa.transicion_activa or estado_escena == "JUGABLE":
        return

    if estado_escena == "ESPERAR_ENTRADA":
        # Esperar a que termine el fundido antes de abrir el diálogo.
        dialogo.iniciar_dialogo("evento_pueblo1_noche_inicio")
        if dialogo.obtener_evento_activo() is None:
            raise ValueError("Falta evento_pueblo1_noche_inicio en el JSON")
        estado_escena = "DIALOGO"

    elif estado_escena == "DIALOGO":
        if dialogo.obtener_evento_activo() is not None:
            return
        estado_escena = "SOLTAR_ESPACIO"

    elif estado_escena == "SOLTAR_ESPACIO":
        if pygame.key.get_pressed()[pygame.K_SPACE]:
            return
        ahora = pygame.time.get_ticks()
        mapa.eventos_completados.add(MARCA_INICIO)
        mapa.tiempo_ultima_interaccion = ahora
        mapa.tiempo_ultimo_paso_mateo = ahora
        mapa.npcs_activos["lucas"]["_tiempo_ultimo_paso"] = ahora
        for npc in mapa.npcs_activos.values():
            if npc.get("comportamiento") == "vigilante":
                npc["congelado"] = False
                if "_vigilancia" in npc:
                    npc["_vigilancia"]["ultimo_paso"] = ahora
        CONTROL_CINEMATICO = False
        mapa.jugador_bloqueado = False
        estado_escena = "JUGABLE"


def obtener_zonas_iluminadas():
    if imagen_luz is None:
        return []
    return [
        imagen_luz.get_rect(center=(round(x), round(y)))
        for x, y in posiciones_luces
    ]


def dibujar_efectos(pantalla, camara_x, camara_y):
    # Es una casilla completa y sólida: los personajes no la atraviesan.
    if imagen_barril is not None:
        x, y = datos.BARRIL_ADICIONAL
        pantalla.blit(imagen_barril, (x * T - camara_x, y * T - camara_y))
    if imagen_luz is None:
        return
    for zona in obtener_zonas_iluminadas():
        rect = zona.move(-camara_x, -camara_y)
        if pantalla.get_rect().colliderect(rect):
            pantalla.blit(imagen_luz, rect)
