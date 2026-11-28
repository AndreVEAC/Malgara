import pygame
import importlib
from types import SimpleNamespace
from pygame.locals import K_UP, K_DOWN, K_LEFT, K_RIGHT
from configuracion import ANCHO_PANTALLA, ALTO_PANTALLA, TAMANO_CASILLA, VERDE_MATEO
import sistema_dialogo
import sistema_npc
import sistema_audio
import sistema_escondites
import sistema_vigilancia
from collections import deque

matriz_activa = []
fondo_actual = None
columnas_mapa, filas_mapa = 0, 0
imagenes_objetos = {}

sprites_mateo = {}
direccion_mateo = "abajo"
mateo_x, mateo_y = 0, 0
mateo_px_x, mateo_px_y = 0.0, 0.0

VELOCIDAD_SUAVIZADO = 0.25
tiempo_ultimo_paso_mateo = 0
tiempo_ultima_interaccion = 0  
RETRASO_MATEO = 250 
espacio_presionado = False

# --- SISTEMAS GENÉRICOS ORIENTADOS A DATOS ---
npcs_activos = {}
interactuables_activos = {}
triggers_pisar_activos = {}
portales_activos = {}

jugador_bloqueado = False
script_nivel_actual = None

transicion_activa = False
tipo_transicion = None
alpha_transicion = 0
mapa_pendiente = None
spawn_pendiente = None
sonido_llegada_pendiente = None

eventos_completados = set()
estado_npcs_guardado = {}
bloqueos_activos = {}
nombre_mapa_actual = None
revision_nivel = 0
reinicio_entrada = None
pantalla_negra_en = None
ocultar_mateo = False
control_cinematico = False

RUTA_CAJA_BLOQUEO = (
    "recursos/sprites/objetos/caja_bloqueo.png"
)


def cargar_sprites_personaje(carpeta):
    direcciones = ["abajo", "arriba", "izq", "der"]
    anim = {}
    for d in direcciones:
        anim[d] = []
        for frame in [0, 1]:
            ruta = f"recursos/sprites/personajes/{carpeta}/{d}_{frame}.png"
            try:
                img = pygame.image.load(ruta).convert_alpha()
                anim[d].append(img)
            except pygame.error:
                surf = pygame.Surface((TAMANO_CASILLA, TAMANO_CASILLA), pygame.SRCALPHA)
                anim[d].append(surf)
    return anim


def cargar_nivel(nombre_modulo, spawn_x=None, spawn_y=None, *, sonido_llegada=None):
    global transicion_activa, tipo_transicion, mapa_pendiente, spawn_pendiente, fondo_actual
    global sonido_llegada_pendiente

    
    spawn_pendiente = (spawn_x, spawn_y) if (spawn_x is not None and spawn_y is not None) else None

    sonido_llegada_pendiente = sonido_llegada
    if fondo_actual is None:
        _cargar_destino(nombre_modulo)
    else:
        transicion_activa = True
        tipo_transicion = "fade_out"
        mapa_pendiente = nombre_modulo


def _reproducir_sonido_portal(ruta):
    if not ruta:
        return

    try:
        pygame.mixer.Sound(ruta).play()
    except (pygame.error, FileNotFoundError) as error:
        print(f"[Portal] No se pudo reproducir el sonido: {error}")


def _cargar_destino(nombre_modulo):
    global sonido_llegada_pendiente

    sonido = sonido_llegada_pendiente
    sonido_llegada_pendiente = None
    _ejecutar_carga_real(nombre_modulo)
    _reproducir_sonido_portal(sonido)


def datos_nivel(nombre):
    from mapas.dia_3 import NIVELES

    if nombre in NIVELES:
        return NIVELES[nombre]
    return importlib.import_module(f"mapas.{nombre}")


def _ejecutar_carga_real(nombre_modulo):
    global matriz_activa, fondo_actual, mateo_x, mateo_y
    global columnas_mapa, filas_mapa, imagenes_objetos
    global mateo_px_x, mateo_px_y
    global sprites_mateo, direccion_mateo
    global jugador_bloqueado, script_nivel_actual
    global npcs_activos, interactuables_activos, triggers_pisar_activos, portales_activos
    global spawn_pendiente
    global nombre_mapa_actual, revision_nivel, reinicio_entrada
    
    mapa_datos = datos_nivel(nombre_modulo)
    nombre_mapa_actual = nombre_modulo
    revision_nivel += 1
    reinicio_entrada = None
    bloqueos_activos.clear()

    matriz_activa = [fila[:] for fila in mapa_datos.MATRIZ]
    
    filas_mapa = len(matriz_activa)
    columnas_mapa = len(matriz_activa[0])
    sistema_escondites.configurar(mapa_datos)
    
    if spawn_pendiente is not None:
        mateo_x, mateo_y = spawn_pendiente
        spawn_pendiente = None
    else:
        mateo_x, mateo_y = mapa_datos.INICIO_X, mapa_datos.INICIO_Y

    direccion_mateo = "abajo"
    jugador_bloqueado = False
    
    # --- CARGAR NPCS GENÉRICOS DEL MAPA ---
    npcs_activos.clear()
    if hasattr(mapa_datos, 'NPCS'):
        for npc_id, datos in mapa_datos.NPCS.items():
            sprites_esp = {}
            for clave_esp, ruta_esp in datos.get("sprites_especiales", {}).items():
                try:
                    img_esp = pygame.image.load(ruta_esp).convert_alpha()
                    sprites_esp[clave_esp] = pygame.transform.scale(img_esp, (TAMANO_CASILLA, TAMANO_CASILLA))
                except (pygame.error, FileNotFoundError):
                    pass

            carpeta_sprite = datos.get("carpeta_sprite")
            sprite_override = datos.get("sprite_override")
            sprites = cargar_sprites_personaje(carpeta_sprite) if carpeta_sprite else {}
            npcs_activos[npc_id] = {
                "x": datos["x"],
                "y": datos["y"],
                "px_x": float(datos["x"] * TAMANO_CASILLA),
                "px_y": float(datos["y"] * TAMANO_CASILLA),
                "direccion": datos.get("direccion", "abajo"),
                "visible": datos.get("visible", True) and bool(
                    sprites or sprite_override in sprites_esp
                ),
                "sprites": sprites,
                "sprites_especiales": sprites_esp,
                "sprite_override": sprite_override,
                "comportamiento": datos.get("comportamiento", "estatico"),
                "patrulla": dict(datos.get("patrulla", {})),
                "seguimiento": dict(datos.get("seguimiento", {})),  
                "vigilancia": dict(datos.get("vigilancia", {})),        
            }
            
    # --- CARGAR INTERACTUABLES, TRIGGERS Y PORTALES ---
    interactuables_activos.clear()
    if hasattr(mapa_datos, 'INTERACTUABLES'):
        interactuables_activos.update(mapa_datos.INTERACTUABLES)

    triggers_pisar_activos.clear()
    if hasattr(mapa_datos, 'TRIGGERS_PISAR'):
        triggers_pisar_activos.update(mapa_datos.TRIGGERS_PISAR)

    portales_activos.clear()
    if hasattr(mapa_datos, 'PORTALES'):
        portales_activos.update(mapa_datos.PORTALES)

    if isinstance(mapa_datos, SimpleNamespace):
        script_nivel_actual = SimpleNamespace(CENTRAR_FONDO=getattr(mapa_datos, "CENTRAR_FONDO", False))
    else:
        try:
            script_nivel_actual = importlib.import_module(f"funciones_mapas.funcion_{nombre_modulo}")
            if hasattr(script_nivel_actual, "iniciar"):
                script_nivel_actual.iniciar()
        except ImportError:
            script_nivel_actual = None
    
    mateo_px_x = float(mateo_x * TAMANO_CASILLA)
    mateo_px_y = float(mateo_y * TAMANO_CASILLA)
    
    try:
        fondo_actual = pygame.image.load(mapa_datos.FONDO_IMG).convert()
    except (pygame.error, AttributeError, FileNotFoundError):
        fondo_actual = pygame.Surface((columnas_mapa * TAMANO_CASILLA, filas_mapa * TAMANO_CASILLA))
        fondo_actual.fill((30, 80, 40))
        
    imagenes_objetos.clear()

    for numero, datos in getattr(
        mapa_datos, "DICCIONARIO_OBJETOS", {}
    ).items():
        img = pygame.image.load(datos["ruta"]).convert_alpha()

        # El tamaño es opcional para conservar los objetos antiguos.
        if "ancho_casillas" in datos or "alto_casillas" in datos:
            ancho = int(
                datos.get(
                    "ancho_casillas",
                    img.get_width() / TAMANO_CASILLA
                ) * TAMANO_CASILLA
            )
            alto = int(
                datos.get(
                    "alto_casillas",
                    img.get_height() / TAMANO_CASILLA
                ) * TAMANO_CASILLA
            )
            img = pygame.transform.scale(img, (ancho, alto))

        imagenes_objetos[numero] = {
            "img": img,
            "colision": datos.get("colision", False),
            "profundidad": datos.get("profundidad", False)
        }

    sprites_mateo = cargar_sprites_personaje("mateo")
    
    cargar_bloqueos(mapa_datos)
    
    colocar_seguidores_cerca()
        # Si el mapa declara un ambiente, aplicarlo.
    # Si no lo declara, conservar el que ya está sonando.
    resolver_ambiente = getattr(script_nivel_actual, "obtener_ambiente", None)
    if callable(resolver_ambiente) or hasattr(mapa_datos, "AMBIENTE"):
        ambiente = (
            resolver_ambiente() if callable(resolver_ambiente)
            else mapa_datos.AMBIENTE
        )
        sistema_audio.reproducir_ambiente(
            ambiente,
            volumen=getattr(mapa_datos, "VOLUMEN_AMBIENTE", 0.4),
            fade_ms=1000
        )
    sistema_vigilancia.configurar()

def _dibujar_npcs(pantalla, camara_x, camara_y, animar=True):
    for npc_id, npc in npcs_activos.items():
        if not npc["visible"]:
            continue

        x_pantalla = int(npc["px_x"]) - camara_x
        y_pantalla = int(npc["px_y"]) - camara_y

        override = npc.get("sprite_override")
        if override and override in npc.get("sprites_especiales", {}):
            pantalla.blit(npc["sprites_especiales"][override], (x_pantalla, y_pantalla))
            continue

        frame = 0
        if animar:
            obj_x = float(npc["x"] * TAMANO_CASILLA)
            obj_y = float(npc["y"] * TAMANO_CASILLA)
            esta_caminando = abs(npc["px_x"] - obj_x) > 0.5 or abs(npc["px_y"] - obj_y) > 0.5
            frame = (pygame.time.get_ticks() // 200) % 2 if esta_caminando else 0

        img = npc["sprites"][npc["direccion"]][frame]
        if img.get_alpha() == 0:
            pygame.draw.rect(pantalla, (200, 100, 200), (x_pantalla + 6, y_pantalla + 6, TAMANO_CASILLA - 12, TAMANO_CASILLA - 12))
        else:
            pantalla.blit(img, (x_pantalla, y_pantalla))


def solo_dibujar(pantalla):
    _dibujar_escenario(pantalla, animar=False)


def actualizar_y_dibujar(pantalla, estado_jugador, investigacion=None):
    global espacio_presionado
    global mateo_x, mateo_y, tiempo_ultimo_paso_mateo, tiempo_ultima_interaccion
    global mateo_px_x, mateo_px_y, direccion_mateo
    global jugador_bloqueado, transicion_activa, tipo_transicion, alpha_transicion, mapa_pendiente
    
    tiempo_actual = pygame.time.get_ticks()
    nuevo_estado_juego = "EXPLORACION"
    
    if investigacion is not None:
        investigacion.actualizar()
    if (
        not estado_jugador.dia2["captura_pendiente"]
        and sistema_dialogo.obtener_evento_activo() is None
        and script_nivel_actual and hasattr(script_nivel_actual, "actualizar")
    ):
        script_nivel_actual.actualizar()
    actualizar_estado = getattr(script_nivel_actual, "actualizar_estado", None)
    if callable(actualizar_estado):
        actualizar_estado(estado_jugador)
        
    actualizar_bloqueos()
        
    if sistema_dialogo.obtener_evento_activo() is not None:
        nuevo_estado_juego = "DIALOGO"

    # Revisar Espacio incluso cuando el escondite bloquea al jugador.
    teclas = pygame.key.get_pressed()
    pulso_espacio = teclas[pygame.K_SPACE] and not espacio_presionado
    espacio_presionado = teclas[pygame.K_SPACE]
    control_escondite = sistema_escondites.actualizar(teclas)

    # 1. CONTROL DE MATEO
    if (
        not control_escondite
        and not control_cinematico
        and not jugador_bloqueado
        and not transicion_activa
        and sistema_dialogo.obtener_evento_activo() is None
    ):
        tiempo_desde_cierre = tiempo_actual - sistema_dialogo.obtener_tiempo_ultimo_cierre()
        if (pulso_espacio
                and (tiempo_actual - tiempo_ultima_interaccion > 500)
                and tiempo_desde_cierre > 300):
            tx, ty = mateo_x, mateo_y
            if direccion_mateo == "arriba": ty -= 1
            elif direccion_mateo == "abajo": ty += 1
            elif direccion_mateo == "izq": tx -= 1
            elif direccion_mateo == "der": tx += 1
            
            if 0 <= tx < columnas_mapa and 0 <= ty < filas_mapa:
                bloqueo = bloqueos_activos.get((tx, ty))

                if bloqueo is not None:
                    nombre_evento = bloqueo["dialogo"]
                else:
                    casilla_frente = matriz_activa[ty][tx]
                    nombre_evento = interactuables_activos.get(
                        casilla_frente
                    )

                if investigacion is not None and investigacion.interactuar(tx, ty, nombre_evento):
                    tiempo_ultima_interaccion = tiempo_actual
                    if sistema_dialogo.obtener_evento_activo() is not None:
                        nuevo_estado_juego = "DIALOGO"
                elif nombre_evento:
                    sistema_dialogo.iniciar_dialogo(nombre_evento)
                    tiempo_ultima_interaccion = tiempo_actual

                    if sistema_dialogo.obtener_evento_activo() is not None:
                        nuevo_estado_juego = "DIALOGO"

                        if (
                            script_nivel_actual
                            and hasattr(
                                script_nivel_actual,
                                "al_iniciar_dialogo"
                            )
                        ):
                            script_nivel_actual.al_iniciar_dialogo(
                                nombre_evento
                            )

        esta_corriendo = teclas[pygame.K_LSHIFT] or teclas[pygame.K_RSHIFT]
        retraso_actual = RETRASO_MATEO // 2 if esta_corriendo else RETRASO_MATEO

        if (
            sistema_dialogo.obtener_evento_activo() is None
            and not transicion_activa
            and estado_jugador.dia2["rama"] != "invitados_honor"
            and estado_jugador.noche2["fase"] != "honor"
            and tiempo_actual - tiempo_ultimo_paso_mateo > retraso_actual
        ):
            nx, ny = mateo_x, mateo_y
            
            if teclas[K_UP]:
                ny -= 1
                direccion_mateo = "arriba"
            elif teclas[K_DOWN]:
                ny += 1
                direccion_mateo = "abajo"
            elif teclas[K_LEFT]:
                nx -= 1
                direccion_mateo = "izq"
            elif teclas[K_RIGHT]:
                nx += 1
                direccion_mateo = "der"
            
            if (nx, ny) != (mateo_x, mateo_y):
                if 0 <= nx < columnas_mapa and 0 <= ny < filas_mapa:
                    casilla_destino = matriz_activa[ny][nx]
                    
                    es_muro = casilla_bloqueada(nx, ny)
                    if es_muro:
                        avisar = getattr(script_nivel_actual, "al_intentar_paso_bloqueado", None)
                        if avisar and avisar(nx, ny, estado_jugador):
                            nuevo_estado_juego = "DIALOGO"
                    
                    bloquea_npc = any(
                        npc["visible"]
                        and npc.get("comportamiento") != "sigue_jugador"
                        and (nx, ny) == (npc["x"], npc["y"])
                        for npc in npcs_activos.values()
                    )
                    
                    fin_de_segmento = (
                        estado_jugador.dia2["resultado"]
                        and not estado_jugador.noche2["fase"]
                        and casilla_destino in portales_activos
                    )
                    if not es_muro and not bloquea_npc and not fin_de_segmento:
                        origen = (mateo_x, mateo_y)
                        mateo_x, mateo_y = nx, ny
                        tiempo_ultimo_paso_mateo = tiempo_actual
                        
                        # Triggers dinámicos al pisar
                        if casilla_destino in triggers_pisar_activos:
                            nombre_evento = triggers_pisar_activos[
                                casilla_destino
                            ]

                            sistema_dialogo.iniciar_dialogo(
                                nombre_evento
                            )

                            # Avisar inmediatamente al director,
                            # antes de dibujar el primer diálogo.
                            if (
                                sistema_dialogo.obtener_evento_activo()
                                is not None
                            ):
                                if (
                                    script_nivel_actual
                                    and hasattr(
                                        script_nivel_actual,
                                        "al_iniciar_dialogo"
                                    )
                                ):
                                    script_nivel_actual.al_iniciar_dialogo(
                                        nombre_evento
                                    )

                            for fila in range(filas_mapa):
                                if matriz_activa[fila][nx] == casilla_destino:
                                    matriz_activa[fila][nx] = 0

                            nuevo_estado_juego = "DIALOGO"

                        # Portales bidireccionales al pisar
                        elif casilla_destino in portales_activos:
                            datos_portal = portales_activos[casilla_destino]
                            requisito = datos_portal.get("requiere_evento")

                            desbloqueado = (
                                requisito is None
                                or requisito in eventos_completados
                            )

                            if (investigacion is not None and investigacion.noche is not None
                                    and investigacion.noche.dia3.interceptar_portal(datos_portal["mapa"])):
                                mateo_x, mateo_y = origen
                                if sistema_dialogo.obtener_evento_activo() is not None:
                                    nuevo_estado_juego = "DIALOGO"
                            elif desbloqueado:
                                jugador_bloqueado = True

                                _reproducir_sonido_portal(
                                    datos_portal.get("sonido_entrada")
                                )

                                cargar_nivel(
                                    datos_portal["mapa"],
                                    datos_portal.get("spawn_x"),
                                    datos_portal.get("spawn_y"),
                                    sonido_llegada=datos_portal.get(
                                        "sonido_llegada"
                                    ),
                                )
                            else:
                                evento = datos_portal.get("evento_bloqueado")

                                if evento:
                                    sistema_dialogo.iniciar_dialogo(evento)
                                    nuevo_estado_juego = "DIALOGO"

    # 2. ACTUALIZACIÓN DE NPCS GENÉRICOS
    sistema_npc.actualizar_npcs(tiempo_actual)

    # 3. INTERPOLACIÓN LERP
    # Mantener también su posición visual mientras está escondido.
    if not sistema_escondites.escondido:
        mateo_obj_x = float(mateo_x * TAMANO_CASILLA)
        mateo_obj_y = float(mateo_y * TAMANO_CASILLA)

        mateo_px_x += (
            mateo_obj_x - mateo_px_x
        ) * VELOCIDAD_SUAVIZADO

        mateo_px_y += (
            mateo_obj_y - mateo_px_y
        ) * VELOCIDAD_SUAVIZADO

    for npc_id, npc in npcs_activos.items():
        if npc["visible"] and not npc.get("congelado", False):
            obj_x = float(npc["x"] * TAMANO_CASILLA)
            obj_y = float(npc["y"] * TAMANO_CASILLA)
            npc["px_x"] += (obj_x - npc["px_x"]) * VELOCIDAD_SUAVIZADO
            npc["px_y"] += (obj_y - npc["px_y"]) * VELOCIDAD_SUAVIZADO

    # 4. RENDERIZADO CON PROFUNDIDAD
    _dibujar_escenario(pantalla, animar=True)

    # 5. GESTIÓN DEL FUNDIDO A NEGRO
    if transicion_activa:
        if tipo_transicion == "fade_out":
            alpha_transicion += 15
            if alpha_transicion >= 255:
                alpha_transicion = 255
                _cargar_destino(mapa_pendiente)
                tipo_transicion = "fade_in"
        elif tipo_transicion == "fade_in":
            alpha_transicion -= 15
            if alpha_transicion <= 0:
                alpha_transicion = 0
                transicion_activa = False

    if alpha_transicion > 0:
        superficie_negra = pygame.Surface((ANCHO_PANTALLA, ALTO_PANTALLA))
        superficie_negra.fill((0, 0, 0))
        superficie_negra.set_alpha(alpha_transicion)
        pantalla.blit(superficie_negra, (0, 0))

    return nuevo_estado_juego


def calcular_camara():
    
    encuadre = getattr(
        script_nivel_actual,
        "CAMARA_CINEMATICA",
        None,
    )

    if encuadre is not None:
        limite_x = max(
            0,
            columnas_mapa * TAMANO_CASILLA - ANCHO_PANTALLA,
        )
        limite_y = max(
            0,
            filas_mapa * TAMANO_CASILLA - ALTO_PANTALLA,
        )

        return (
            int(max(0, min(encuadre[0], limite_x))),
            int(max(0, min(encuadre[1], limite_y))),
        )
        
    centrar = getattr(
        script_nivel_actual,
        "CENTRAR_FONDO",
        False
    )

    ancho_mapa = columnas_mapa * TAMANO_CASILLA
    alto_mapa = filas_mapa * TAMANO_CASILLA

    if centrar and fondo_actual is not None:
        # Usar los 400×300 reales, no los 400×320 de la matriz.
        ancho_mapa, alto_mapa = fondo_actual.get_size()

    if centrar and ancho_mapa < ANCHO_PANTALLA:
        camara_x = -((ANCHO_PANTALLA - ancho_mapa) // 2)
    else:
        camara_x = max(
            0,
            min(
                int(mateo_px_x) - ANCHO_PANTALLA // 2,
                max(0, ancho_mapa - ANCHO_PANTALLA)
            )
        )

    if centrar and alto_mapa < ALTO_PANTALLA:
        camara_y = -((ALTO_PANTALLA - alto_mapa) // 2)
    else:
        camara_y = max(
            0,
            min(
                int(mateo_px_y) - ALTO_PANTALLA // 2,
                max(0, alto_mapa - ALTO_PANTALLA)
            )
        )

    return camara_x, camara_y

def _dibujar_escenario(pantalla, animar=True):
    if (pantalla_negra_en == nombre_mapa_actual
            or getattr(script_nivel_actual, "PANTALLA_NEGRA", False)):
        pantalla.fill((0, 0, 0))
        return

    if getattr(script_nivel_actual, "CENTRAR_FONDO", False):
        pantalla.fill((0, 0, 0))

    camara_x, camara_y = calcular_camara()
    pantalla.blit(fondo_actual, (-camara_x, -camara_y))

    elementos = []
    tiempo = pygame.time.get_ticks()
    ventana = pantalla.get_rect()

    # 1. Objetos del mapa.
    for fila, casillas in enumerate(matriz_activa):
        for col, numero in enumerate(casillas):
            objeto = imagenes_objetos.get(numero)

            if objeto is None:
                continue

            img = objeto["img"]

            if objeto.get("profundidad", False):
                base_y = (fila + 1) * TAMANO_CASILLA
                centro_x = (col + 0.5) * TAMANO_CASILLA

                x = int(
                    centro_x - img.get_width() / 2
                ) - camara_x

                y = int(
                    base_y - img.get_height()
                ) - camara_y

                elementos.append((base_y, img, x, y))

            else:
                x = col * TAMANO_CASILLA - camara_x
                y = fila * TAMANO_CASILLA - camara_y

                if img.get_rect(topleft=(x, y)).colliderect(ventana):
                    pantalla.blit(img, (x, y))

    # 2. Cajas de bloqueo.
    for (col, fila), bloqueo in bloqueos_activos.items():
        elementos.append((
            (fila + 1) * TAMANO_CASILLA,
            bloqueo["img"],
            col * TAMANO_CASILLA - camara_x,
            fila * TAMANO_CASILLA - camara_y,
        ))

    # 3. NPC visibles.
    for npc in npcs_activos.values():
        if not npc["visible"]:
            continue

        override = npc.get("sprite_override")
        especiales = npc.get("sprites_especiales", {})

        if override and override in especiales:
            img = especiales[override]

        else:
            caminando = (
                abs(npc["px_x"] - npc["x"] * TAMANO_CASILLA) > 0.5
                or abs(npc["px_y"] - npc["y"] * TAMANO_CASILLA) > 0.5
            )

            frame = (
                (tiempo // 200) % 2
                if (
                    animar
                    and caminando
                    and not npc.get("congelado", False)
                )
                else 0
            )

            img = npc["sprites"][npc["direccion"]][frame]

        elementos.append((
            npc["px_y"] + TAMANO_CASILLA,
            img,
            int(npc["px_x"]) - camara_x,
            int(npc["px_y"]) - camara_y,
        ))

    # 4. Mateo: no dibujarlo mientras esté escondido.
    if not sistema_escondites.escondido and not ocultar_mateo:
        caminando = (
            abs(mateo_px_x - mateo_x * TAMANO_CASILLA) > 0.5
            or abs(mateo_px_y - mateo_y * TAMANO_CASILLA) > 0.5
        )

        frame = (
            (tiempo // 150) % 2
            if animar and caminando
            else 0
        )

        img = sprites_mateo[direccion_mateo][frame]

        elementos.append((
            mateo_px_y + TAMANO_CASILLA,
            img,
            int(mateo_px_x) - camara_x,
            int(mateo_px_y) - camara_y,
        ))

    # 5. Dibujar personajes y objetos ordenados por profundidad.
    capa = getattr(script_nivel_actual, "capa_profundidad", None)
    if capa:
        elementos.append(capa(camara_x, camara_y))
    elementos.sort(key=lambda elemento: elemento[0])

    for _, img, x, y in elementos:
        if img.get_rect(topleft=(x, y)).colliderect(ventana):
            pantalla.blit(img, (x, y))

    # 6. Luces de los postes y otros efectos del mapa.
    funcion_efectos = getattr(
        script_nivel_actual,
        "dibujar_efectos",
        None,
    )

    if callable(funcion_efectos):
        funcion_efectos(pantalla, camara_x, camara_y)

    # 7. Linternas de los vigilantes.
    sistema_vigilancia.dibujar_linternas(
        pantalla,
        camara_x,
        camara_y,
    )

    # 8. Aviso del barril por encima de las luces.
    sistema_escondites.dibujar_aviso(pantalla)
    encuadrar = getattr(script_nivel_actual, "aplicar_encuadre", None)
    if encuadrar:
        encuadrar(pantalla, camara_x, camara_y)
            
def casilla_bloqueada(x, y):
    if not (0 <= x < columnas_mapa and 0 <= y < filas_mapa):
        return True

    if (x, y) in sistema_escondites.barriles:
        return True

    if (x, y) in bloqueos_activos:
        return True

    casilla = matriz_activa[y][x]

    if casilla == 1 or casilla in interactuables_activos:
        return True

    objeto = imagenes_objetos.get(casilla)
    return bool(objeto and objeto["colision"])

def colocar_seguidores_cerca():
    """Colocar los seguidores cerca del punto de entrada de Mateo."""
    for npc in npcs_activos.values():
        if (
            not npc.get("visible", True)
            or npc.get("comportamiento") != "sigue_jugador"
        ):
            continue

        ocupadas = {
            (otro["x"], otro["y"])
            for otro in npcs_activos.values()
            if otro is not npc and otro.get("visible", True)
        }

        inicio = (mateo_x, mateo_y)
        pendientes = deque([inicio])
        visitadas = {inicio}
        destino = None

        while pendientes:
            x, y = pendientes.popleft()

            if (x, y) != inicio and (x, y) not in ocupadas:
                destino = (x, y)
                break

            # Preferir aparecer debajo o al lado de Mateo.
            for dx, dy in ((0, 1), (1, 0), (-1, 0), (0, -1)):
                nx, ny = x + dx, y + dy

                if (nx, ny) in visitadas:
                    continue

                visitadas.add((nx, ny))

                if casilla_bloqueada(nx, ny):
                    continue

                if (nx, ny) in ocupadas:
                    continue

                casilla = matriz_activa[ny][nx]

                # No colocar al acompañante sobre una salida o evento.
                if (
                    casilla in portales_activos
                    or casilla in triggers_pisar_activos
                ):
                    continue

                pendientes.append((nx, ny))

        if destino is None:
            continue

        npc["x"], npc["y"] = destino

        # Ajustar también los píxeles para evitar que se vea
        # desplazarse desde su antigua posición.
        npc["px_x"] = float(npc["x"] * TAMANO_CASILLA)
        npc["px_y"] = float(npc["y"] * TAMANO_CASILLA)
        npc["_tiempo_ultimo_paso"] = pygame.time.get_ticks()
        
def cargar_bloqueos(mapa_datos):
    bloqueos_activos.clear()
    imagenes_cajas = {}

    for bloqueo in getattr(mapa_datos, "BLOQUEOS", []):
        evento = bloqueo.get("desbloquear_con")

        if evento is not None and evento in eventos_completados:
            continue

        ruta = bloqueo.get("ruta", RUTA_CAJA_BLOQUEO)

        if ruta not in imagenes_cajas:
            imagen = pygame.image.load(ruta).convert_alpha()
            imagenes_cajas[ruta] = pygame.transform.scale(
                imagen,
                (TAMANO_CASILLA, TAMANO_CASILLA)
            )

        for x, y in bloqueo.get("casillas", []):
            if not (0 <= x < columnas_mapa and 0 <= y < filas_mapa):
                raise ValueError(
                    f"Bloqueo {bloqueo.get('id')}: "
                    f"casilla fuera del mapa ({x}, {y})"
                )

            if (x, y) in bloqueos_activos:
                raise ValueError(
                    f"Dos bloqueos ocupan la casilla ({x}, {y})"
                )

            bloqueos_activos[(x, y)] = {
                "img": imagenes_cajas[ruta],
                "dialogo": bloqueo.get(
                    "dialogo",
                    "evento_camino_bloqueado"
                ),
                "desbloquear_con": evento,
            }


def actualizar_bloqueos():
    for posicion, bloqueo in list(bloqueos_activos.items()):
        evento = bloqueo["desbloquear_con"]

        if evento is not None and evento in eventos_completados:
            del bloqueos_activos[posicion]
