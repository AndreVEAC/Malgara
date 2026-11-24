from mapas import llegada


FONDO_IMG = "recursos/sprites/fondos/fondo_entrada_dia_2.png"
AMBIENTE = llegada.AMBIENTE
VOLUMEN_AMBIENTE = llegada.VOLUMEN_AMBIENTE
INICIO_X, INICIO_Y = llegada.INICIO_X, llegada.INICIO_Y

PORTALES = {
    98: dict(llegada.PORTALES[98]),
    99: {"mapa": "pueblo_1_dia_2", "spawn_x": 1, "spawn_y": 7},
}
DICCIONARIO_OBJETOS = {
    21: {
        "ruta": "recursos/sprites/edificios/casa_abuela.png",
        "colision": True,
        "profundidad": True,
    },
    22: {
        "ruta": "recursos/sprites/objetos/banca_1.png",
        "colision": True,
        "profundidad": True,
    },
}

MATRIZ = [[0] * 20 for _ in range(15)]
for y in (6, 7, 8):
    MATRIZ[y][0], MATRIZ[y][-1] = 98, 99
for y in (2, 3, 4):
    MATRIZ[y][13:18] = [1] * 5
MATRIZ[4][15] = 21
MATRIZ[5][17] = 22
MATRIZ[5][10:12] = [1, 1]
