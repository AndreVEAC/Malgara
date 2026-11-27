FONDO_IMG = "recursos/sprites/fondos/fondo_barda_noche_2.png"
AMBIENTE = "noche_calmada"
INICIO_X, INICIO_Y = 10, 23
PASO_CERCA = 10
MATRIZ = [[0] * 20 for _ in range(25)]
for fila in (5, 6, 7):
    MATRIZ[fila] = [0 if x == PASO_CERCA else 1 for x in range(20)]
