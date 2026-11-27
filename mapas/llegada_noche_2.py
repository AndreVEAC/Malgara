from mapas.geografia_noche_2 import marcar

FONDO_IMG = "recursos/sprites/fondos/fondo_entrada_noche_2.png"
AMBIENTE = "noche_calmada"
INICIO_X, INICIO_Y = 18, 7
HACIA_BARDA = (10, 0)
MATRIZ = [[0] * 20 for _ in range(15)]
marcar(MATRIZ, ((x, y) for x in range(13, 18) for y in range(1, 4)), 1)
marcar(MATRIZ, ((10, 4), (11, 4), (10, 5), (11, 5)), 1)
