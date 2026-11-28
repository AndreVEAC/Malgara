FONDO_IMG = "recursos/sprites/fondos/fondo_prision.png"
CENTRAR_FONDO = True
AMBIENTE = None
INICIO_X, INICIO_Y = 3, 4
FILA_BARROTES = 5
HUECO = 4
ORIGEN_BARROTES = (0, 120)

MATRIZ = [
    [1] * 10 if fila < 3 or fila == FILA_BARROTES
    else [1] + [0] * 8 + [1]
    for fila in range(8)
]
