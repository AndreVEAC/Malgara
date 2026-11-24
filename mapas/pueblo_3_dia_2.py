from mapas import pueblo_1


FONDO_IMG = "recursos/sprites/fondos/fondo_pueblo_3_dia_2.png"
INICIO_X, INICIO_Y = 12, 1
AMBIENTE = "miradas"
VOLUMEN_AMBIENTE = 0.4
DICCIONARIO_OBJETOS = pueblo_1.DICCIONARIO_OBJETOS
PORTALES = {
    98: {"mapa": "pueblo_2_dia_2", "spawn_x": 31, "spawn_y": 28},
    97: {"mapa": "casa_dia2", "spawn_x": 18, "spawn_y": 18},
}

MATRIZ = [[0] * 25 for _ in range(30)]
MATRIZ[0][11:14] = [98] * 3

# Casas, clínica y objetos que ya están dibujados en el fondo.
for izquierda, arriba, derecha, abajo in (
    (0, 0, 1, 3), (3, 0, 8, 3), (15, 0, 20, 3), (22, 0, 24, 3),
    (0, 7, 1, 10), (3, 7, 8, 10), (15, 7, 20, 10), (22, 7, 24, 10),
    (0, 13, 1, 16), (3, 13, 8, 16), (15, 13, 23, 16),
    (0, 20, 1, 23), (3, 20, 8, 23),
    (6, 11, 7, 11), (16, 11, 17, 11), (16, 18, 17, 18),
    (21, 18, 22, 18), (6, 24, 7, 24),
):
    for y in range(arriba, abajo + 1):
        MATRIZ[y][izquierda:derecha + 1] = [1] * (derecha - izquierda + 1)
for x, y in ((2, 3), (21, 3), (18, 6), (2, 10), (21, 10), (2, 16), (2, 23)):
    MATRIZ[y][x] = 1
for x, y in ((10, 5), (14, 12), (10, 18), (14, 24)):
    MATRIZ[y][x] = 20
for x, y in ((0, 6), (24, 5), (0, 12), (24, 20), (1, 26), (8, 28), (20, 29)):
    MATRIZ[y][x] = 21

# El arbolado cierra el fondo y deja libre la vereda de piedra.
for x in range(0, 25, 2):
    MATRIZ[29][x] = 21
for x in (0, 3, 5, 7, 9, 15, 17, 19, 21, 23, 24):
    MATRIZ[27][x] = 21
MATRIZ[18][0] = 97
