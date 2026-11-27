from mapas import pueblo_1_dia_2
from mapas.geografia_noche_2 import marcar, matriz_desde, objetos, paso, vigilante

FONDO_IMG = "recursos/sprites/fondos/fondo_pueblo_1_noche_2.png"
AMBIENTE = "noche_calmada"
INICIO_X, INICIO_Y = 38, 22
BARRIL_REGRESO = (9, 5)
JUNTO_BARRIL = (9, 6)
BARRILES = {BARRIL_REGRESO, (25, 5), (3, 20), (36, 20), (23, 23)}
DICCIONARIO_OBJETOS = objetos()
MATRIZ = matriz_desde(pueblo_1_dia_2)
marcar(MATRIZ, ((8, 11), (17, 10), (26, 17), (15, 26), (32, 25)), 20)
marcar(MATRIZ, ((0, y) for y in range(20, 25)), 22)
marcar(MATRIZ, ((16, 22), (17, 22), (27, 16), (27, 17), (10, 11)), 22)
marcar(MATRIZ, ((5, 13), (24, 14), (37, 11)), 0)
marcar(MATRIZ, ((39, y) for y in (21, 22, 23)), 98)
marcar(MATRIZ, ((39, y) for y in (6, 7, 8)), 96)
marcar(MATRIZ, ((0, y) for y in (6, 7, 8)), 97)
PORTALES = {98: paso("pueblo_2_noche_2", 1, 22), 97: paso("llegada_noche_2", 18, 7),
            96: paso("pueblo_2_noche_2", 1, 7)}
NPCS = {
    "loco_superior": vigilante(24, 7, "izq", [(19, 7), (29, 7)]),
    "loco_fuente": vigilante(7, 16, "der", miradas=[("der", 1800), ("abajo", 1450)]),
    "loco_centro": vigilante(20, 15, "abajo", [(20, 19), (20, 14)]),
    "loco_sur": vigilante(28, 23, "izq", [(21, 23), (29, 23)]),
}
