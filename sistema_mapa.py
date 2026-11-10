import pygame
from pygame.locals import K_UP, K_DOWN, K_LEFT, K_RIGHT
from configuracion import ANCHO_PANTALLA, ALTO_PANTALLA, TAMANO_CASILLA, VERDE_MATEO

# ==========================================
# VARIABLES GLOBALES DEL MÓDULO
# ==========================================
matriz_activa = []
fondo_actual = None
columnas_mapa, filas_mapa = 0, 0
imagenes_objetos = {}

# Diccionarios de sprites para los personajes
sprites_mateo = {}
sprites_lucas = {}
direccion_mateo = "abajo"
direccion_lucas = "der"

# Posiciones lógicas en la matriz (Casillas)
mateo_x, mateo_y = 0, 0
lucas_x, lucas_y = 0, 0

# Posiciones visuales en píxeles (Para la animación fluida / LERP)
mateo_px_x, mateo_px_y = 0.0, 0.0
lucas_px_x, lucas_px_y = 0.0, 0.0

VELOCIDAD_SUAVIZADO = 0.25  # Factor de interpolación (0.1 muy suave, 0.5 más rápido)

# Temporizadores independientes de paso
tiempo_ultimo_paso_mateo = 0
tiempo_ultimo_paso_lucas = 0

RETRASO_MATEO = 120  # Intervalo de movimiento de Mateo
RETRASO_LUCAS = 250  # Lucas camina más lento (Maleta de 30kg)


def cargar_sprites_personaje(carpeta):
    """Carga los PNGs de 4 direcciones (0 y 1) o crea superficies vacías si no existen."""
    direcciones = ["abajo", "arriba", "izq", "der"]
    anim = {}
    for d in direcciones:
        anim[d] = []
        for frame in [0, 1]:
            ruta = f"recursos/personajes/{carpeta}/{d}_{frame}.png"
            try:
                img = pygame.image.load(ruta).convert_alpha()
                anim[d].append(img)
            except pygame.error:
                # Si el archivo aún no existe, genera un marco temporal sin romper la ejecución
                surf = pygame.Surface((TAMANO_CASILLA, TAMANO_CASILLA), pygame.SRCALPHA)
                anim[d].append(surf)
    return anim


def cargar_nivel(nombre_modulo):
    global matriz_activa, fondo_actual, mateo_x, mateo_y, lucas_x, lucas_y
    global columnas_mapa, filas_mapa, imagenes_objetos
    global mateo_px_x, mateo_px_y, lucas_px_x, lucas_px_y
    global sprites_mateo, sprites_lucas, direccion_mateo, direccion_lucas
    
    if nombre_modulo == "prologo":
        import mapas.prologo as mapa_datos

    matriz_activa = mapa_datos.MATRIZ
    mateo_x, mateo_y = mapa_datos.INICIO_X, mapa_datos.INICIO_Y
    
    # Lucas inicia en su posición fija
    lucas_x, lucas_y = 1, 15
    direccion_mateo = "abajo"
    direccion_lucas = "der"
    
    # Inicialización de coordenadas de renderizado en píxeles
    mateo_px_x = float(mateo_x * TAMANO_CASILLA)
    mateo_px_y = float(mateo_y * TAMANO_CASILLA)
    lucas_px_x = float(lucas_x * TAMANO_CASILLA)
    lucas_px_y = float(lucas_y * TAMANO_CASILLA)
    
    filas_mapa = len(matriz_activa)
    columnas_mapa = len(matriz_activa[0])
    
    try:
        fondo_actual = pygame.image.load(mapa_datos.FONDO_IMG).convert()
    except pygame.error:
        fondo_actual = pygame.Surface((columnas_mapa * TAMANO_CASILLA, filas_mapa * TAMANO_CASILLA))
        fondo_actual.fill((30, 80, 40))
        
    # Cargar sprites del mapa según el DICCIONARIO_OBJETOS
    imagenes_objetos.clear()
    if hasattr(mapa_datos, 'DICCIONARIO_OBJETOS'):
        for numero, datos in mapa_datos.DICCIONARIO_OBJETOS.items():
            try:
                img = pygame.image.load(datos["ruta"]).convert_alpha()
                imagenes_objetos[numero] = {
                    "img": img,
                    "colision": datos["colision"]
                }
            except pygame.error:
                print(f"Error: No se encontró la imagen {datos['ruta']}")

    # Cargar los sets de animación de los personajes
    sprites_mateo = cargar_sprites_personaje("mateo")
    sprites_lucas = cargar_sprites_personaje("lucas")


# ==========================================
# RENDERIZADO CONGELADO (DURANTE DIÁLOGOS)
# ==========================================
def solo_dibujar(pantalla):
    camara_x = int(mateo_px_x) - (ANCHO_PANTALLA // 2)
    camara_y = int(mateo_px_y) - (ALTO_PANTALLA // 2)
    
    limite_x = (columnas_mapa * TAMANO_CASILLA) - ANCHO_PANTALLA
    limite_y = (filas_mapa * TAMANO_CASILLA) - ALTO_PANTALLA
    
    camara_x = max(0, min(camara_x, max(0, limite_x)))
    camara_y = max(0, min(camara_y, max(0, limite_y)))

    # 1. Fondo
    pantalla.blit(fondo_actual, (-camara_x, -camara_y))

    # 2. Objetos del mapa
    for fila in range(filas_mapa):
        for col in range(columnas_mapa):
            casilla = matriz_activa[fila][col]
            if casilla in imagenes_objetos:
                x_obj = (col * TAMANO_CASILLA) - camara_x
                y_obj = (fila * TAMANO_CASILLA) - camara_y
                if -TAMANO_CASILLA <= x_obj <= ANCHO_PANTALLA and -TAMANO_CASILLA <= y_obj <= ALTO_PANTALLA:
                    pantalla.blit(imagenes_objetos[casilla]["img"], (x_obj, y_obj))

    # 3. Lucas (Congelado en el cuadro 0 de su dirección)
    x_lucas_pantalla = int(lucas_px_x) - camara_x
    y_lucas_pantalla = int(lucas_px_y) - camara_y
    img_lucas = sprites_lucas[direccion_lucas][0]
    if img_lucas.get_alpha() == 0:  # Respaldo si no existe la imagen PNG
        pygame.draw.rect(pantalla, (255, 165, 0), (x_lucas_pantalla + 6, y_lucas_pantalla + 6, TAMANO_CASILLA - 12, TAMANO_CASILLA - 12))
    else:
        pantalla.blit(img_lucas, (x_lucas_pantalla, y_lucas_pantalla))

    # 4. Mateo (Congelado en el cuadro 0 de su dirección)
    x_mateo_pantalla = int(mateo_px_x) - camara_x
    y_mateo_pantalla = int(mateo_px_y) - camara_y
    img_mateo = sprites_mateo[direccion_mateo][0]
    if img_mateo.get_alpha() == 0:  # Respaldo si no existe la imagen PNG
        pygame.draw.rect(pantalla, VERDE_MATEO, (x_mateo_pantalla + 4, y_mateo_pantalla + 4, TAMANO_CASILLA - 8, TAMANO_CASILLA - 8))
    else:
        pantalla.blit(img_mateo, (x_mateo_pantalla, y_mateo_pantalla))


# ==========================================
# BUCLE PRINCIPAL DE MOVIMIENTO Y LÓGICA
# ==========================================
def actualizar_y_dibujar(pantalla, estado_jugador):
    global mateo_x, mateo_y, lucas_x, lucas_y, tiempo_ultimo_paso_mateo, tiempo_ultimo_paso_lucas
    global mateo_px_x, mateo_px_y, lucas_px_x, lucas_px_y
    global direccion_mateo, direccion_lucas
    
    tiempo_actual = pygame.time.get_ticks()
    nuevo_estado_juego = "EXPLORACION"
    
    # ----------------------------------------------------
    # 1. CONTROL DE MATEO
    # ----------------------------------------------------
    if tiempo_actual - tiempo_ultimo_paso_mateo > RETRASO_MATEO:
        teclas = pygame.key.get_pressed()
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
                
                if not es_muro and (nx, ny) != (lucas_x, lucas_y):
                    mateo_x, mateo_y = nx, ny
                    tiempo_ultimo_paso_mateo = tiempo_actual
                    
                    if casilla_destino in [5, 6, 9]:
                        import sistema_dialogo
                        sistema_dialogo.iniciar_dialogo(f"evento_{casilla_destino}")
                        
                        for fila in range(filas_mapa):
                            if matriz_activa[fila][nx] == casilla_destino:
                                matriz_activa[fila][nx] = 0
                                
                        nuevo_estado_juego = "DIALOGO"

    # ----------------------------------------------------
    # 2. IA Y RUTA DE LUCAS
    # ----------------------------------------------------
    if tiempo_actual - tiempo_ultimo_paso_lucas > RETRASO_LUCAS:
        if lucas_x < 37:
            nx_lucas = lucas_x + 1
            ny_lucas = lucas_y
            direccion_lucas = "der"
            
            # Mateo bloquea el paso de Lucas -> Empujón
            if nx_lucas == mateo_x and ny_lucas == mateo_y:
                for dx, dy in [(0, -1), (0, 1), (1, 0)]:
                    mx_nuevo = mateo_x + dx
                    my_nuevo = mateo_y + dy
                    
                    if 0 <= mx_nuevo < columnas_mapa and 0 <= my_nuevo < filas_mapa:
                        casilla_empuje = matriz_activa[my_nuevo][mx_nuevo]
                        
                        muro_empuje = (casilla_empuje == 1)
                        if casilla_empuje in imagenes_objetos and imagenes_objetos[casilla_empuje]["colision"]:
                            muro_empuje = True
                            
                        if not muro_empuje and (mx_nuevo, my_nuevo) != (lucas_x, lucas_y):
                            mateo_x, mateo_y = mx_nuevo, my_nuevo
                            lucas_x, lucas_y = nx_lucas, ny_lucas
                            break
            else:
                casilla_frente_lucas = matriz_activa[ny_lucas][nx_lucas]
                
                muro_lucas = (casilla_frente_lucas == 1)
                if casilla_frente_lucas in imagenes_objetos and imagenes_objetos[casilla_frente_lucas]["colision"]:
                    muro_lucas = True
                    
                # Lucas avanza solo si no hay muro ni evento bloqueante
                if not muro_lucas and casilla_frente_lucas not in [5, 6, 9]:
                    lucas_x, lucas_y = nx_lucas, ny_lucas
            
            tiempo_ultimo_paso_lucas = tiempo_actual

    # ----------------------------------------------------
    # 3. INTERPOLACIÓN DE MOVIMIENTO (LERP PÍXELES)
    # ----------------------------------------------------
    mateo_obj_x = float(mateo_x * TAMANO_CASILLA)
    mateo_obj_y = float(mateo_y * TAMANO_CASILLA)
    mateo_px_x += (mateo_obj_x - mateo_px_x) * VELOCIDAD_SUAVIZADO
    mateo_px_y += (mateo_obj_y - mateo_px_y) * VELOCIDAD_SUAVIZADO

    lucas_obj_x = float(lucas_x * TAMANO_CASILLA)
    lucas_obj_y = float(lucas_y * TAMANO_CASILLA)
    lucas_px_x += (lucas_obj_x - lucas_px_x) * VELOCIDAD_SUAVIZADO
    lucas_px_y += (lucas_obj_y - lucas_px_y) * VELOCIDAD_SUAVIZADO

    # ----------------------------------------------------
    # 4. CÁLCULO DE CÁMARA VIRTUAL
    # ----------------------------------------------------
    camara_x = int(mateo_px_x) - (ANCHO_PANTALLA // 2)
    camara_y = int(mateo_px_y) - (ALTO_PANTALLA // 2)
    
    limite_x = (columnas_mapa * TAMANO_CASILLA) - ANCHO_PANTALLA
    limite_y = (filas_mapa * TAMANO_CASILLA) - ALTO_PANTALLA
    
    camara_x = max(0, min(camara_x, max(0, limite_x)))
    camara_y = max(0, min(camara_y, max(0, limite_y)))

    # ----------------------------------------------------
    # 5. RENDERIZADO VISUAL CON SPRITES ANIMADOS
    # ----------------------------------------------------
    pantalla.blit(fondo_actual, (-camara_x, -camara_y))

    # Objetos en el mapa
    for fila in range(filas_mapa):
        for col in range(columnas_mapa):
            casilla = matriz_activa[fila][col]
            if casilla in imagenes_objetos:
                x_obj = (col * TAMANO_CASILLA) - camara_x
                y_obj = (fila * TAMANO_CASILLA) - camara_y
                if -TAMANO_CASILLA <= x_obj <= ANCHO_PANTALLA and -TAMANO_CASILLA <= y_obj <= ALTO_PANTALLA:
                    pantalla.blit(imagenes_objetos[casilla]["img"], (x_obj, y_obj))

    # Renderizado de Lucas (Conmutación de fotogramas al caminar)
    x_lucas_pantalla = int(lucas_px_x) - camara_x
    y_lucas_pantalla = int(lucas_px_y) - camara_y
    esta_caminando_lucas = abs(lucas_px_x - lucas_obj_x) > 0.5 or abs(lucas_px_y - lucas_obj_y) > 0.5
    frame_lucas = (pygame.time.get_ticks() // 200) % 2 if esta_caminando_lucas else 0
    img_lucas = sprites_lucas[direccion_lucas][frame_lucas]
    
    if img_lucas.get_alpha() == 0:
        pygame.draw.rect(pantalla, (255, 165, 0), (x_lucas_pantalla + 6, y_lucas_pantalla + 6, TAMANO_CASILLA - 12, TAMANO_CASILLA - 12))
    else:
        pantalla.blit(img_lucas, (x_lucas_pantalla, y_lucas_pantalla))

    # Renderizado de Mateo (Conmutación de fotogramas al caminar)
    x_mateo_pantalla = int(mateo_px_x) - camara_x
    y_mateo_pantalla = int(mateo_px_y) - camara_y
    esta_caminando_mateo = abs(mateo_px_x - mateo_obj_x) > 0.5 or abs(mateo_px_y - mateo_obj_y) > 0.5
    frame_mateo = (pygame.time.get_ticks() // 150) % 2 if esta_caminando_mateo else 0
    img_mateo = sprites_mateo[direccion_mateo][frame_mateo]
    
    if img_mateo.get_alpha() == 0:
        pygame.draw.rect(pantalla, VERDE_MATEO, (x_mateo_pantalla + 4, y_mateo_pantalla + 4, TAMANO_CASILLA - 8, TAMANO_CASILLA - 8))
    else:
        pantalla.blit(img_mateo, (x_mateo_pantalla, y_mateo_pantalla))

    return nuevo_estado_juego