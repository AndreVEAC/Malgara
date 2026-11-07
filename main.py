import pygame
from pygame.locals import QUIT, KEYDOWN, K_UP, K_DOWN, K_LEFT, K_RIGHT

pygame.init()

TAMANO_CASILLA = 40
FILAS, COLUMNAS = 12, 15  # Ventana de 600x480 píxeles
pantalla = pygame.display.set_mode((COLUMNAS * TAMANO_CASILLA, FILAS * TAMANO_CASILLA))
pygame.display.set_caption("Malgara - Enemigos en Patrulla y Visión Dinámica")

# Mapa Base: 1 = Pared, 0 = Suelo libre
MAPA_BASE = [
    [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
    [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
    [1, 0, 1, 1, 1, 0, 1, 1, 1, 0, 1, 1, 1, 0, 1],
    [1, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 1],
    [1, 0, 1, 0, 1, 1, 0, 1, 1, 0, 1, 0, 1, 0, 1],
    [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
    [1, 0, 1, 0, 1, 1, 0, 1, 1, 0, 1, 0, 1, 0, 1],
    [1, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 1],
    [1, 0, 1, 1, 1, 0, 1, 1, 1, 0, 1, 1, 1, 0, 1],
    [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
    [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
    [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1]
]

mateo_x, mateo_y = 1, 1

# --- CLASE PARA MANEJAR ENEMIGOS ---
class Enemigo:
    def __init__(self, ruta, direccion_inicial):
        self.ruta = ruta  # Lista de coordenadas por las que camina: [(x1,y1), (x2,y2)...]
        self.indice_ruta = 0
        self.x, self.y = self.ruta[0]
        self.direccion = direccion_inicial  # "DERECHA", "IZQUIERDA", "ARRIBA", "ABAJO"
        self.rango_vision = 3  # Cuántas casillas al frente alcanza a ver

    def mover(self):
        # Avanzar al siguiente punto de la ruta
        self.indice_ruta = (self.indice_ruta + 1) % len(self.ruta)
        siguiente_x, siguiente_y = self.ruta[self.indice_ruta]

        # Actualizar dirección según hacia dónde camina
        if siguiente_x > self.x: self.direccion = "DERECHA"
        elif siguiente_x < self.x: self.direccion = "IZQUIERDA"
        elif siguiente_y > self.y: self.direccion = "ABAJO"
        elif siguiente_y < self.y: self.direccion = "ARRIBA"

        self.x, self.y = siguiente_x, siguiente_y

    def obtener_casillas_vision(self):
        """Calcula las casillas que está mirando en tiempo real"""
        casillas_vistas = []
        for i in range(1, self.rango_vision + 1):
            vx, vy = self.x, self.y
            if self.direccion == "DERECHA":   vx += i
            elif self.direccion == "IZQUIERDA": vx -= i
            elif self.direccion == "ABAJO":    vy += i
            elif self.direccion == "ARRIBA":   vy -= i
            
            # Si choca con una pared (1), la visión no traspasa el muro
            if 0 <= vy < FILAS and 0 <= vx < COLUMNAS:
                if MAPA_BASE[vy][vx] == 1:
                    break
                casillas_vistas.append((vx, vy))
        return casillas_vistas

# Crear un habitante/guardia de Malgara con su ruta de patrulla
# Ejemplo: Camina de (2,5) a (12,5) y de regreso
ruta_enemigo = [(col, 5) for col in range(2, 13)] + [(col, 5) for col in range(11, 2, -1)]
guardia = Enemigo(ruta_enemigo, "DERECHA")

# Evento de temporizador para mover al enemigo cada 400 milisegundos
EVENTO_MOVER_ENEMIGO = pygame.USEREVENT + 1
pygame.time.set_timer(EVENTO_MOVER_ENEMIGO, 400)

reloj = pygame.time.Clock()
ejecutando = True

while ejecutando:
    reloj.tick(30)

    for evento in pygame.event.get():
        if evento.type == QUIT:
            ejecutando = False
            
        elif evento.type == EVENTO_MOVER_ENEMIGO:
            guardia.mover()
            
        elif evento.type == KEYDOWN:
            nx, ny = mateo_x, mateo_y
            if evento.key == K_UP:    ny -= 1
            if evento.key == K_DOWN:  ny += 1
            if evento.key == K_LEFT:  nx -= 1
            if evento.key == K_RIGHT: nx += 1
            
            if MAPA_BASE[ny][nx] != 1:
                mateo_x, mateo_y = nx, ny

    # Comprobar si Mateo fue visto por el guardia
    vision_guardia = guardia.obtener_casillas_vision()
    if (mateo_x, mateo_y) in vision_guardia or (mateo_x, mateo_y) == (guardia.x, guardia.y):
        print("🚨 ¡TE VIERON! Mateo entró en el campo de visión del habitante.")

    # --- RENDERIZADO ---
    pantalla.fill((15, 15, 20))

    # 1. Dibujar el Mapa Base
    for fila in range(FILAS):
        for col in range(COLUMNAS):
            rect = (col * TAMANO_CASILLA, fila * TAMANO_CASILLA, TAMANO_CASILLA, TAMANO_CASILLA)
            if MAPA_BASE[fila][col] == 1:
                pygame.draw.rect(pantalla, (50, 50, 65), rect)
                pygame.draw.rect(pantalla, (35, 35, 45), rect, 1)
            else:
                pygame.draw.rect(pantalla, (20, 20, 25), rect, 1)

    # 2. Dibujar el Campo de Visión del Enemigo (Rojo traslúcido)
    for (vx, vy) in vision_guardia:
        rect_vis = (vx * TAMANO_CASILLA, vy * TAMANO_CASILLA, TAMANO_CASILLA, TAMANO_CASILLA)
        s = pygame.Surface((TAMANO_CASILLA, TAMANO_CASILLA))
        s.set_alpha(100)  # Transparencia
        s.fill((220, 40, 40))
        pantalla.blit(s, rect_vis)

    # 3. Dibujar al Guardia (Cuadro rojo fuerte)
    rect_guardia = (guardia.x * TAMANO_CASILLA + 4, guardia.y * TAMANO_CASILLA + 4, TAMANO_CASILLA - 8, TAMANO_CASILLA - 8)
    pygame.draw.rect(pantalla, (200, 30, 30), rect_guardia)

    # 4. Dibujar a Mateo (Cuadro cian)
    rect_mateo = (mateo_x * TAMANO_CASILLA + 4, mateo_y * TAMANO_CASILLA + 4, TAMANO_CASILLA - 8, TAMANO_CASILLA - 8)
    pygame.draw.rect(pantalla, (0, 220, 180), rect_mateo)

    pygame.display.flip()

pygame.quit()