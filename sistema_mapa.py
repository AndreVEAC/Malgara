import pygame
import importlib
from pygame.locals import K_UP, K_DOWN, K_LEFT, K_RIGHT
from configuracion import ANCHO_PANTALLA, ALTO_PANTALLA, TAMANO_CASILLA, VERDE_MATEO
import sistema_dialogo

matriz_activa = []
fondo_actual = None
columnas_mapa, filas_mapa = 0, 0
imagenes_objetos = {}

sprites_mateo = {}
sprites_lucas = {}
sprite_lucas_foto = None
tiene_sprite_foto = False

direccion_mateo = "abajo"
direccion_lucas = "der"

mateo_x, mateo_y = 0, 0
lucas_x, lucas_y = 0, 0

mateo_px_x, mateo_px_y = 0.0, 0.0
lucas_px_x, lucas_px_y = 0.0, 0.0

VELOCIDAD_SUAVIZADO = 0.25
tiempo_ultimo_paso_mateo = 0
tiempo_ultimo_paso_lucas = 0
RETRASO_MATEO = 250 
RETRASO_LUCAS = 250  

# [ABUELA] Variables globales nuevas
sprites_abuela = {}
abuela_x, abuela_y = 0, 0
abuela_px_x, abuela_px_y = 0.0, 0.0
direccion_abuela = "abajo"
abuela_visible = False

# NUEVAS VARIABLES PARA LA ARQUITECTURA
jugador_bloqueado = False
script_nivel_actual = None

# NUEVAS VARIABLES PARA LA TRANSICIÓN DE PANTALLA
transicion_activa = False
tipo_transicion = None
alpha_transicion = 0
mapa_pendiente = None


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


def cargar_nivel(nombre_modulo):
    """Inicia la transición en negro, o carga directo si es el inicio del juego"""
    global transicion_activa, tipo_transicion, mapa_pendiente, fondo_actual

    if fondo_actual is None:
        _ejecutar_carga_real(nombre_modulo)
    else:
        transicion_activa = True
        tipo_transicion = "fade_out"
        mapa_pendiente = nombre_modulo


def _ejecutar_carga_real(nombre_modulo):
    """Esta era tu función cargar_nivel original, ahora se ejecuta oculta tras la pantalla negra"""
    global matriz_activa, fondo_actual, mateo_x, mateo_y, lucas_x, lucas_y
    global columnas_mapa, filas_mapa, imagenes_objetos
    global mateo_px_x, mateo_px_y, lucas_px_x, lucas_px_y
    global sprites_mateo, sprites_lucas, sprite_lucas_foto, tiene_sprite_foto
    global direccion_mateo, direccion_lucas
    global jugador_bloqueado, script_nivel_actual
    # [ABUELA] Globals nuevos
    global sprites_abuela, abuela_x, abuela_y, abuela_px_x, abuela_px_y
    global direccion_abuela, abuela_visible
    
    # 1. Cargamos el mapa (los ladrillos) de forma dinámica
    mapa_datos = importlib.import_module(f"mapas.{nombre_modulo}")

    matriz_activa = mapa_datos.MATRIZ
    mateo_x, mateo_y = mapa_datos.INICIO_X, mapa_datos.INICIO_Y
    
    # Valores por defecto que el script puede sobreescribir
    lucas_x, lucas_y = 1, 15
    direccion_mateo = "abajo"
    direccion_lucas = "der"
    jugador_bloqueado = False

    # [ABUELA] Valores por defecto al cargar un nivel
    abuela_x, abuela_y = 0, 0
    abuela_px_x, abuela_px_y = 0.0, 0.0
    direccion_abuela = "abajo"
    abuela_visible = False
    
    # 2. Cargamos el Script del Nivel si existe (el Director)
    try:
        script_nivel_actual = importlib.import_module(f"funciones_mapas.funcion_{nombre_modulo}")
        if hasattr(script_nivel_actual, "iniciar"):
            script_nivel_actual.iniciar()
    except ImportError:
        script_nivel_actual = None
        if nombre_modulo == "prologo":
            sistema_dialogo.cargar_json("datos/prologo.json")
    
    mateo_px_x = float(mateo_x * TAMANO_CASILLA)
    mateo_px_y = float(mateo_y * TAMANO_CASILLA)
    lucas_px_x = float(lucas_x * TAMANO_CASILLA)
    lucas_px_y = float(lucas_y * TAMANO_CASILLA)
    # [ABUELA] Sincronizar pixel con casilla
    abuela_px_x = float(abuela_x * TAMANO_CASILLA)
    abuela_px_y = float(abuela_y * TAMANO_CASILLA)
    
    filas_mapa = len(matriz_activa)
    columnas_mapa = len(matriz_activa[0])
    
    try:
        fondo_actual = pygame.image.load(mapa_datos.FONDO_IMG).convert()
    except (pygame.error, AttributeError, FileNotFoundError):
        fondo_actual = pygame.Surface((columnas_mapa * TAMANO_CASILLA, filas_mapa * TAMANO_CASILLA))
        fondo_actual.fill((30, 80, 40))
        
    imagenes_objetos.clear()
    if hasattr(mapa_datos, 'DICCIONARIO_OBJETOS'):
        for numero, datos in mapa_datos.DICCIONARIO_OBJETOS.items():
            try:
                img = pygame.image.load(datos["ruta"]).convert_alpha()
                imagenes_objetos[numero] = {
                    "img": img,
                    "colision": datos["colision"]
                }
            except (pygame.error, FileNotFoundError):
                print(f"Error: No se encontró la imagen {datos['ruta']}")

    sprites_mateo = cargar_sprites_personaje("mateo")
    sprites_lucas = cargar_sprites_personaje("lucas")
    # [ABUELA] Cargar sprites de la abuela
    sprites_abuela = cargar_sprites_personaje("abuela")

    try:
        img_foto = pygame.image.load("recursos/sprites/personajes/lucas/foto.png").convert_alpha()
        sprite_lucas_foto = pygame.transform.scale(img_foto, (TAMANO_CASILLA, TAMANO_CASILLA))
        tiene_sprite_foto = True
    except (pygame.error, FileNotFoundError):
        sprite_lucas_foto = None
        tiene_sprite_foto = False


def solo_dibujar(pantalla):
    camara_x = int(mateo_px_x) - (ANCHO_PANTALLA // 2)
    camara_y = int(mateo_px_y) - (ALTO_PANTALLA // 2)
    
    limite_x = (columnas_mapa * TAMANO_CASILLA) - ANCHO_PANTALLA
    limite_y = (filas_mapa * TAMANO_CASILLA) - ALTO_PANTALLA
    camara_x = max(0, min(camara_x, max(0, limite_x)))
    camara_y = max(0, min(camara_y, max(0, limite_y)))

    pantalla.blit(fondo_actual, (-camara_x, -camara_y))

    for fila in range(filas_mapa):
        for col in range(columnas_mapa):
            casilla = matriz_activa[fila][col]
            if casilla in imagenes_objetos:
                x_obj = (col * TAMANO_CASILLA) - camara_x
                y_obj = (fila * TAMANO_CASILLA) - camara_y
                if -TAMANO_CASILLA <= x_obj <= ANCHO_PANTALLA and -TAMANO_CASILLA <= y_obj <= ALTO_PANTALLA:
                    pantalla.blit(imagenes_objetos[casilla]["img"], (x_obj, y_obj))

    # [ABUELA] Dibujo de respaldo en solo_dibujar (opcional pero consistente)
    if abuela_visible:
        x_abuela_pantalla = int(abuela_px_x) - camara_x
        y_abuela_pantalla = int(abuela_px_y) - camara_y
        img_abuela = sprites_abuela[direccion_abuela][0]
        if img_abuela.get_alpha() == 0:
            pygame.draw.rect(pantalla, (200, 100, 100), (x_abuela_pantalla + 6, y_abuela_pantalla + 6, TAMANO_CASILLA - 12, TAMANO_CASILLA - 12))
        else:
            pantalla.blit(img_abuela, (x_abuela_pantalla, y_abuela_pantalla))

    x_lucas_pantalla = int(lucas_px_x) - camara_x
    y_lucas_pantalla = int(lucas_px_y) - camara_y
    evento_en_curso = sistema_dialogo.obtener_evento_activo()
    if evento_en_curso == "evento_6" and tiene_sprite_foto:
        pantalla.blit(sprite_lucas_foto, (x_lucas_pantalla, y_lucas_pantalla))
    else:
        img_lucas = sprites_lucas[direccion_lucas][0]
        if img_lucas.get_alpha() == 0:
            pygame.draw.rect(pantalla, (255, 165, 0), (x_lucas_pantalla + 6, y_lucas_pantalla + 6, TAMANO_CASILLA - 12, TAMANO_CASILLA - 12))
        else:
            pantalla.blit(img_lucas, (x_lucas_pantalla, y_lucas_pantalla))

    x_mateo_pantalla = int(mateo_px_x) - camara_x
    y_mateo_pantalla = int(mateo_px_y) - camara_y
    img_mateo = sprites_mateo[direccion_mateo][0]
    if img_mateo.get_alpha() == 0:
        pygame.draw.rect(pantalla, VERDE_MATEO, (x_mateo_pantalla + 4, y_mateo_pantalla + 4, TAMANO_CASILLA - 8, TAMANO_CASILLA - 8))
    else:
        pantalla.blit(img_mateo, (x_mateo_pantalla, y_mateo_pantalla))


def actualizar_y_dibujar(pantalla, estado_jugador):
    global mateo_x, mateo_y, lucas_x, lucas_y, tiempo_ultimo_paso_mateo, tiempo_ultimo_paso_lucas
    global mateo_px_x, mateo_px_y, lucas_px_x, lucas_px_y
    global direccion_mateo, direccion_lucas
    global transicion_activa, tipo_transicion, alpha_transicion, mapa_pendiente
    # [ABUELA] Globals necesarios para actualizar/dibujar
    global abuela_px_x, abuela_px_y, abuela_x, abuela_y
    global direccion_abuela, abuela_visible
    
    tiempo_actual = pygame.time.get_ticks()
    nuevo_estado_juego = "EXPLORACION"
    
    if script_nivel_actual and hasattr(script_nivel_actual, "actualizar"):
        script_nivel_actual.actualizar()
        
    if sistema_dialogo.obtener_evento_activo() is not None:
        nuevo_estado_juego = "DIALOGO"

    # ----------------------------------------------------
    # 1. CONTROL DE MATEO
    # ----------------------------------------------------
    if not jugador_bloqueado:
        teclas = pygame.key.get_pressed()
        
        esta_corriendo = teclas[pygame.K_LSHIFT] or teclas[pygame.K_RSHIFT]
        retraso_actual = RETRASO_MATEO // 2 if esta_corriendo else RETRASO_MATEO

        if tiempo_actual - tiempo_ultimo_paso_mateo > retraso_actual:
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
                    
                    es_muro = (casilla_destino == 1)
                    if casilla_destino in imagenes_objetos and imagenes_objetos[casilla_destino]["colision"]:
                        es_muro = True
                    
                    # [ABUELA] No se puede pisar a la abuela si está visible
                    bloquea_abuela = abuela_visible and (nx, ny) == (abuela_x, abuela_y)
                    
                    if not es_muro and (nx, ny) != (lucas_x, lucas_y) and not bloquea_abuela:
                        mateo_x, mateo_y = nx, ny
                        tiempo_ultimo_paso_mateo = tiempo_actual
                        
                        if casilla_destino in [5, 6, 9]:
                            sistema_dialogo.iniciar_dialogo(f"evento_{casilla_destino}")
                            for fila in range(filas_mapa):
                                if matriz_activa[fila][nx] == casilla_destino:
                                    matriz_activa[fila][nx] = 0
                            nuevo_estado_juego = "DIALOGO"

    # ----------------------------------------------------
    # 2. IA DE LUCAS
    # ----------------------------------------------------
    if tiempo_actual - tiempo_ultimo_paso_lucas > RETRASO_LUCAS:
        if lucas_x < 37 and lucas_y == 15:
            nx_lucas = lucas_x + 1
            ny_lucas = lucas_y
            direccion_lucas = "der"
            
            if nx_lucas == mateo_x and ny_lucas == mateo_y:
                for dx, dy in [(0, -1), (0, 1), (1, 0)]:
                    mx_nuevo = mateo_x + dx
                    my_nuevo = mateo_y + dy
                    if 0 <= mx_nuevo < columnas_mapa and 0 <= my_nuevo < filas_mapa:
                        casilla_empuje = matriz_activa[my_nuevo][mx_nuevo]
                        muro_empuje = (casilla_empuje == 1)
                        if casilla_empuje in imagenes_objetos and imagenes_objetos[casilla_empuje]["colision"]:
                            muro_empuje = True
                        # [ABUELA] No empujar a Mateo sobre la abuela
                        bloquea_abuela = abuela_visible and (mx_nuevo, my_nuevo) == (abuela_x, abuela_y)
                        if not muro_empuje and (mx_nuevo, my_nuevo) != (lucas_x, lucas_y) and not bloquea_abuela:
                            mateo_x, mateo_y = mx_nuevo, my_nuevo
                            lucas_x, lucas_y = nx_lucas, ny_lucas
                            break
            else:
                casilla_frente_lucas = matriz_activa[ny_lucas][nx_lucas]
                muro_lucas = (casilla_frente_lucas == 1)
                if casilla_frente_lucas in imagenes_objetos and imagenes_objetos[casilla_frente_lucas]["colision"]:
                    muro_lucas = True
                if not muro_lucas and casilla_frente_lucas not in [5, 6, 9]:
                    lucas_x, lucas_y = nx_lucas, ny_lucas
            
            tiempo_ultimo_paso_lucas = tiempo_actual

    # ----------------------------------------------------
    # 3. INTERPOLACIÓN LERP
    # ----------------------------------------------------
    mateo_obj_x = float(mateo_x * TAMANO_CASILLA)
    mateo_obj_y = float(mateo_y * TAMANO_CASILLA)
    mateo_px_x += (mateo_obj_x - mateo_px_x) * VELOCIDAD_SUAVIZADO
    mateo_px_y += (mateo_obj_y - mateo_px_y) * VELOCIDAD_SUAVIZADO

    lucas_obj_x = float(lucas_x * TAMANO_CASILLA)
    lucas_obj_y = float(lucas_y * TAMANO_CASILLA)
    lucas_px_x += (lucas_obj_x - lucas_px_x) * VELOCIDAD_SUAVIZADO
    lucas_px_y += (lucas_obj_y - lucas_px_y) * VELOCIDAD_SUAVIZADO

    # [ABUELA] Interpolación LERP de la abuela
    abuela_obj_x = float(abuela_x * TAMANO_CASILLA)
    abuela_obj_y = float(abuela_y * TAMANO_CASILLA)
    abuela_px_x += (abuela_obj_x - abuela_px_x) * VELOCIDAD_SUAVIZADO
    abuela_px_y += (abuela_obj_y - abuela_px_y) * VELOCIDAD_SUAVIZADO

    camara_x, camara_y = calcular_camara()

    # ----------------------------------------------------
    # 4. RENDERIZADO VISUAL
    # ----------------------------------------------------
    pantalla.blit(fondo_actual, (-camara_x, -camara_y))

    for fila in range(filas_mapa):
        for col in range(columnas_mapa):
            casilla = matriz_activa[fila][col]
            if casilla in imagenes_objetos:
                x_obj = (col * TAMANO_CASILLA) - camara_x
                y_obj = (fila * TAMANO_CASILLA) - camara_y
                if -TAMANO_CASILLA <= x_obj <= ANCHO_PANTALLA and -TAMANO_CASILLA <= y_obj <= ALTO_PANTALLA:
                    pantalla.blit(imagenes_objetos[casilla]["img"], (x_obj, y_obj))

    # [ABUELA] Render de la abuela ANTES de Mateo y Lucas
    if abuela_visible:
        x_abuela_pantalla = int(abuela_px_x) - camara_x
        y_abuela_pantalla = int(abuela_px_y) - camara_y
        esta_caminando_abuela = abs(abuela_px_x - abuela_obj_x) > 0.5 or abs(abuela_px_y - abuela_obj_y) > 0.5
        frame_abuela = (pygame.time.get_ticks() // 200) % 2 if esta_caminando_abuela else 0
        img_abuela = sprites_abuela[direccion_abuela][frame_abuela]

        if img_abuela.get_alpha() == 0:
            pygame.draw.rect(pantalla, (200, 100, 100), (x_abuela_pantalla + 6, y_abuela_pantalla + 6, TAMANO_CASILLA - 12, TAMANO_CASILLA - 12))
        else:
            pantalla.blit(img_abuela, (x_abuela_pantalla, y_abuela_pantalla))

    x_lucas_pantalla = int(lucas_px_x) - camara_x
    y_lucas_pantalla = int(lucas_px_y) - camara_y
    
    evento_en_curso = sistema_dialogo.obtener_evento_activo()
    if evento_en_curso == "evento_6" and tiene_sprite_foto:
        pantalla.blit(sprite_lucas_foto, (x_lucas_pantalla, y_lucas_pantalla))
    else:
        esta_caminando_lucas = abs(lucas_px_x - lucas_obj_x) > 0.5 or abs(lucas_px_y - lucas_obj_y) > 0.5
        frame_lucas = (pygame.time.get_ticks() // 200) % 2 if esta_caminando_lucas else 0
        img_lucas = sprites_lucas[direccion_lucas][frame_lucas]
        
        if img_lucas.get_alpha() == 0:
            pygame.draw.rect(pantalla, (255, 165, 0), (x_lucas_pantalla + 6, y_lucas_pantalla + 6, TAMANO_CASILLA - 12, TAMANO_CASILLA - 12))
        else:
            pantalla.blit(img_lucas, (x_lucas_pantalla, y_lucas_pantalla))

    x_mateo_pantalla = int(mateo_px_x) - camara_x
    y_mateo_pantalla = int(mateo_px_y) - camara_y
    esta_caminando_mateo = abs(mateo_px_x - mateo_obj_x) > 0.5 or abs(mateo_px_y - mateo_obj_y) > 0.5
    frame_mateo = (pygame.time.get_ticks() // 150) % 2 if esta_caminando_mateo else 0
    img_mateo = sprites_mateo[direccion_mateo][frame_mateo]
    
    if img_mateo.get_alpha() == 0:
        pygame.draw.rect(pantalla, VERDE_MATEO, (x_mateo_pantalla + 4, y_mateo_pantalla + 4, TAMANO_CASILLA - 8, TAMANO_CASILLA - 8))
    else:
        pantalla.blit(img_mateo, (x_mateo_pantalla, y_mateo_pantalla))

    # ----------------------------------------------------
    # 5. GESTIÓN DEL FUNDIDO A NEGRO
    # ----------------------------------------------------
    if transicion_activa:
        if tipo_transicion == "fade_out":
            alpha_transicion += 15
            if alpha_transicion >= 255:
                alpha_transicion = 255
                _ejecutar_carga_real(mapa_pendiente)
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
    camara_x = int(mateo_px_x) - (ANCHO_PANTALLA // 2)
    camara_y = int(mateo_px_y) - (ALTO_PANTALLA // 2)
    limite_x = (columnas_mapa * TAMANO_CASILLA) - ANCHO_PANTALLA
    limite_y = (filas_mapa * TAMANO_CASILLA) - ALTO_PANTALLA
    camara_x = max(0, min(camara_x, max(0, limite_x)))
    camara_y = max(0, min(camara_y, max(0, limite_y)))
    return camara_x, camara_y