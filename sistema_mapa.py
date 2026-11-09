import pygame
from pygame.locals import K_UP, K_DOWN, K_LEFT, K_RIGHT
from configuracion import ANCHO_PANTALLA, ALTO_PANTALLA, TAMANO_CASILLA, VERDE_MATEO

# Variables globales del módulo
matriz_activa = []
fondo_actual = None
columnas_mapa, filas_mapa = 0, 0

# Posiciones de los personajes
mateo_x, mateo_y = 0, 0
lucas_x, lucas_y = 0, 0

# Temporizadores independientes
tiempo_ultimo_paso_mateo = 0
tiempo_ultimo_paso_lucas = 0

RETRASO_MATEO = 120  # Velocidad normal de Mateo
RETRASO_LUCAS = 250  # Lucas camina más lento (Maleta de 30kg)

def cargar_nivel(nombre_modulo):
    global matriz_activa, fondo_actual, mateo_x, mateo_y, lucas_x, lucas_y, columnas_mapa, filas_mapa
    
    if nombre_modulo == "prologo":
        import mapas.prologo as mapa_datos

    matriz_activa = mapa_datos.MATRIZ
    mateo_x, mateo_y = mapa_datos.INICIO_X, mapa_datos.INICIO_Y
    
    # Lucas empieza cerca de Mateo, pero en su propia coordenada fija
    lucas_x, lucas_y = 1, 15
    
    filas_mapa = len(matriz_activa)
    columnas_mapa = len(matriz_activa[0])
    
    try:
        fondo_actual = pygame.image.load(mapa_datos.FONDO_IMG).convert()
    except pygame.error:
        fondo_actual = pygame.Surface((columnas_mapa * TAMANO_CASILLA, filas_mapa * TAMANO_CASILLA))
        fondo_actual.fill((30, 80, 40))
        

# ==========================================
# FUNCIÓN PARA DIBUJAR EL MAPA CONGELADO
# ==========================================
def solo_dibujar(pantalla):
    # Calcula la cámara igual que siempre
    camara_x = (mateo_x * TAMANO_CASILLA) - (ANCHO_PANTALLA // 2)
    camara_y = (mateo_y * TAMANO_CASILLA) - (ALTO_PANTALLA // 2)
    
    limite_x = (columnas_mapa * TAMANO_CASILLA) - ANCHO_PANTALLA
    limite_y = (filas_mapa * TAMANO_CASILLA) - ALTO_PANTALLA
    
    camara_x = max(0, min(camara_x, max(0, limite_x)))
    camara_y = max(0, min(camara_y, max(0, limite_y)))

    # Dibuja el fondo
    pantalla.blit(fondo_actual, (-camara_x, -camara_y))

    # Dibuja a Lucas congelado
    x_lucas_pantalla = (lucas_x * TAMANO_CASILLA) - camara_x
    y_lucas_pantalla = (lucas_y * TAMANO_CASILLA) - camara_y
    pygame.draw.rect(pantalla, (255, 165, 0), (x_lucas_pantalla + 6, y_lucas_pantalla + 6, TAMANO_CASILLA - 12, TAMANO_CASILLA - 12))

    # Dibuja a Mateo congelado
    x_mateo_pantalla = (mateo_x * TAMANO_CASILLA) - camara_x
    y_mateo_pantalla = (mateo_y * TAMANO_CASILLA) - camara_y
    pygame.draw.rect(pantalla, VERDE_MATEO, (x_mateo_pantalla + 4, y_mateo_pantalla + 4, TAMANO_CASILLA - 8, TAMANO_CASILLA - 8))


def actualizar_y_dibujar(pantalla, estado_jugador):
    global mateo_x, mateo_y, lucas_x, lucas_y, tiempo_ultimo_paso_mateo, tiempo_ultimo_paso_lucas
    
    tiempo_actual = pygame.time.get_ticks()
    nuevo_estado_juego = "EXPLORACION"
    
    # ==========================================
    # 1. MOVIMIENTO DE MATEO (Controlado por ti)
    # ==========================================
    if tiempo_actual - tiempo_ultimo_paso_mateo > RETRASO_MATEO:
        teclas = pygame.key.get_pressed()
        nx, ny = mateo_x, mateo_y
        
        if teclas[K_UP]:      ny -= 1
        elif teclas[K_DOWN]:  ny += 1
        elif teclas[K_LEFT]:  nx -= 1
        elif teclas[K_RIGHT]: nx += 1
        
        if (nx, ny) != (mateo_x, mateo_y):
            if 0 <= nx < columnas_mapa and 0 <= ny < filas_mapa:
                casilla_destino = matriz_activa[ny][nx]
                
                # Comprobar que no choca con paredes ni con Lucas
                if casilla_destino != 1 and (nx, ny) != (lucas_x, lucas_y):
                    mateo_x, mateo_y = nx, ny
                    tiempo_ultimo_paso_mateo = tiempo_actual
                    
                    # Trigger de diálogo al pisar casillas especiales
                    if casilla_destino in [5, 6, 9]:
                        import sistema_dialogo
                        sistema_dialogo.iniciar_dialogo(f"evento_{casilla_destino}")
                        
                        # Borrar la columna entera de eventos para no repetirlos
                        for fila in range(filas_mapa):
                            if matriz_activa[fila][nx] == casilla_destino:
                                matriz_activa[fila][nx] = 0
                                
                        nuevo_estado_juego = "DIALOGO"

    # ==========================================
    # 2. MOVIMIENTO AUTÓNOMO DE LUCAS (La Ruta y el Empujón)
    # ==========================================
    if tiempo_actual - tiempo_ultimo_paso_lucas > RETRASO_LUCAS:
        # Definir la ruta de Lucas: Caminar hacia la derecha hasta la columna 37 (Esperando a Mateo en el evento)
        if lucas_x < 37:
            nx_lucas = lucas_x + 1
            ny_lucas = lucas_y
            
            # ¿Mateo está bloqueando la casilla a la que Lucas quiere ir?
            if nx_lucas == mateo_x and ny_lucas == mateo_y:
                # Lucas avienta a Mateo buscando una casilla libre adyacente (Arriba, Abajo o Derecha)
                empujado = False
                for dx, dy in [(0, -1), (0, 1), (1, 0)]:
                    mx_nuevo = mateo_x + dx
                    my_nuevo = mateo_y + dy
                    
                    # Si esa casilla extra está dentro del mapa, no es pared y no es donde está Lucas
                    if 0 <= mx_nuevo < columnas_mapa and 0 <= my_nuevo < filas_mapa:
                        if matriz_activa[my_nuevo][mx_nuevo] != 1 and (mx_nuevo, my_nuevo) != (lucas_x, lucas_y):
                            mateo_x, mateo_y = mx_nuevo, my_nuevo  # Se desplaza a Mateo
                            lucas_x, lucas_y = nx_lucas, ny_lucas  # Lucas toma su ruta
                            empujado = True
                            break
                
                # Si Mateo estaba acorralado y no pudo ser empujado, Lucas espera un turno.
            else:
                casilla_frente_lucas = matriz_activa[ny_lucas][nx_lucas]
                # Si Mateo no estorba, Lucas verifica muros y avanza
                if casilla_frente_lucas != 1 and casilla_frente_lucas not in [5, 6, 9]:
                    lucas_x, lucas_y = nx_lucas, ny_lucas
            
            tiempo_ultimo_paso_lucas = tiempo_actual

    # ==========================================
    # 3. CÁLCULO DE LA CÁMARA
    # ==========================================
    camara_x = (mateo_x * TAMANO_CASILLA) - (ANCHO_PANTALLA // 2)
    camara_y = (mateo_y * TAMANO_CASILLA) - (ALTO_PANTALLA // 2)
    
    limite_x = (columnas_mapa * TAMANO_CASILLA) - ANCHO_PANTALLA
    limite_y = (filas_mapa * TAMANO_CASILLA) - ALTO_PANTALLA
    
    camara_x = max(0, min(camara_x, max(0, limite_x)))
    camara_y = max(0, min(camara_y, max(0, limite_y)))

    # ==========================================
    # 4. RENDERIZADO
    # ==========================================
    pantalla.blit(fondo_actual, (-camara_x, -camara_y))

    # Dibujar a Lucas (Naranja)
    x_lucas_pantalla = (lucas_x * TAMANO_CASILLA) - camara_x
    y_lucas_pantalla = (lucas_y * TAMANO_CASILLA) - camara_y
    pygame.draw.rect(pantalla, (255, 165, 0), (x_lucas_pantalla + 6, y_lucas_pantalla + 6, TAMANO_CASILLA - 12, TAMANO_CASILLA - 12))

    # Dibujar a Mateo (Verde)
    x_mateo_pantalla = (mateo_x * TAMANO_CASILLA) - camara_x
    y_mateo_pantalla = (mateo_y * TAMANO_CASILLA) - camara_y
    pygame.draw.rect(pantalla, VERDE_MATEO, (x_mateo_pantalla + 4, y_mateo_pantalla + 4, TAMANO_CASILLA - 8, TAMANO_CASILLA - 8))

    return nuevo_estado_juego