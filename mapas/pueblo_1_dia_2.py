from mapas import pueblo_1


FONDO_IMG = "recursos/sprites/fondos/fondo_pueblo_1_dia_2.png"
INICIO_X, INICIO_Y = 1, 7
DICCIONARIO_OBJETOS = pueblo_1.DICCIONARIO_OBJETOS
AMBIENTE = "miradas"
VOLUMEN_AMBIENTE = 0.4
BLOQUEOS = [
    bloqueo for bloqueo in pueblo_1.BLOQUEOS
    if bloqueo["id"] == "salida_inferior_izquierda"
]

PORTALES = {
    98: {"mapa": "llegada_dia_2", "spawn_x": 18, "spawn_y": 7},
    97: {"mapa": "pueblo_2_dia_2", "spawn_x": 1, "spawn_y": 7},
    96: {"mapa": "casa_dia2", "spawn_x": 3, "spawn_y": 1},
    95: {"mapa": "pueblo_2_dia_2", "spawn_x": 1, "spawn_y": 14},
    94: {"mapa": "pueblo_2_dia_2", "spawn_x": 1, "spawn_y": 22},
}

# Se mantienen los obstáculos y objetos del escenario, sin los diálogos del día 1.
colisiones = dict.fromkeys(range(2, 12), 1)
colisiones.update(dict.fromkeys(range(12, 18), 0))
MATRIZ = [[colisiones.get(casilla, casilla) for casilla in fila] for fila in pueblo_1.MATRIZ]

for y in (6, 7, 8):
    MATRIZ[y][0], MATRIZ[y][-1] = 98, 97
for y in (21, 22, 23):
    MATRIZ[y][-1] = 94
MATRIZ[-1][8:11] = [96] * 3

# Personas dibujadas en el fondo nuevo.
for x, y in ((5, 13), (24, 14), (37, 11)):
    MATRIZ[y][x] = 1
MATRIZ[10][6] = 1  # Extremo de la banca donde se sentaba un vecino el día 1.
