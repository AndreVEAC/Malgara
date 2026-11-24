from mapas import intro


FONDO_IMG = "recursos/sprites/fondos/fondo_intro_dia_2.png"
AMBIENTE = intro.AMBIENTE
VOLUMEN_AMBIENTE = intro.VOLUMEN_AMBIENTE
INICIO_X, INICIO_Y = 18, 7
RADIO = ((10, 7), (10, 8))
INTERACTUABLES = {30: "evento_radio"}
PORTALES = {99: dict(intro.PORTALES[99])}

MATRIZ = [[1] * 20 for _ in range(15)]
for y in range(5, 10):
    MATRIZ[y][5:19] = [0] * 14
for x, y in ((7, 5), (7, 6), (8, 8), (11, 8), (14, 7), (17, 7)):
    MATRIZ[y][x] = 1
for x, y in RADIO:
    MATRIZ[y][x] = 30
for y in (7, 8):
    MATRIZ[y][-1] = 99
