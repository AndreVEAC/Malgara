from mapas import iglesia_dia2, pueblo_1, pueblo_2


FONDO_IMG = "recursos/sprites/fondos/fondo_pueblo_2_dia_2.png"
AMBIENTE = "miradas"
VOLUMEN_AMBIENTE = 0.4
INICIO_X, INICIO_Y = 38, 7
DICCIONARIO_OBJETOS = pueblo_2.DICCIONARIO_OBJETOS

ALTAR_AUSENTE = 30
ZONA_ALTAR = tuple((x, y) for y in (1, 2) for x in range(35, 39))
TRIGGERS_PISAR = {ALTAR_AUSENTE: "evento_altar_ausente"}
PORTALES = {
    98: {"mapa": "pueblo_1_dia_2", "spawn_x": 38, "spawn_y": 7},
    97: {"mapa": "pueblo_1_dia_2", "spawn_x": 38, "spawn_y": 14},
    96: {"mapa": "pueblo_1_dia_2", "spawn_x": 38, "spawn_y": 21},
    95: {"mapa": "iglesia_dia2", "spawn_x": iglesia_dia2.REGRESO_PUEBLO[0],
         "spawn_y": iglesia_dia2.REGRESO_PUEBLO[1]},
    94: {"mapa": "pueblo_3_dia_2", "spawn_x": 12, "spawn_y": 1},
}

colisiones = dict.fromkeys((2, 3, 4, 6, 7, 8, 9), 1)
colisiones.update(dict.fromkeys((5, 12, 13, 14, 15, 16, 17), 0))
MATRIZ = [[colisiones.get(casilla, casilla) for casilla in fila] for fila in pueblo_2.MATRIZ]

for y in (6, 7, 8):
    MATRIZ[y][0], MATRIZ[y][-1] = 98, 95
for y in (21, 22, 23):
    MATRIZ[y][0] = 96
MATRIZ[-1][31:33] = [94, 94]

for x, y in ((3, 4), (20, 14), (37, 14), (38, 14), (31, 24)):
    MATRIZ[y][x] = 1
for x, y in ZONA_ALTAR:
    MATRIZ[y][x] = ALTAR_AUSENTE
