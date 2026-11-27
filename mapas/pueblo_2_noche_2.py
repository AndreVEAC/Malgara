from mapas import pueblo_2_dia_2
from mapas.geografia_noche_2 import marcar, matriz_desde, objetos, paso, vigilante

FONDO_IMG = "recursos/sprites/fondos/fondo_pueblo_2_noche_2.png"
AMBIENTE = "noche_calmada"
INICIO_X, INICIO_Y = 31, 28
DICCIONARIO_OBJETOS = objetos()
MATRIZ = matriz_desde(pueblo_2_dia_2, conservar_postes=True)
marcar(MATRIZ, ((17, 21), (18, 21), (24, 23), (24, 24), (10, 20)), 22)
MATRIZ[14][20] = 0
MATRIZ[24][31] = 0
marcar(MATRIZ, ((x, 29) for x in (31, 32)), 98)
marcar(MATRIZ, ((0, y) for y in (21, 22, 23)), 97)
marcar(MATRIZ, ((0, y) for y in (6, 7, 8)), 96)
PORTALES = {98: paso("pueblo_3_noche_2", 12, 1), 97: paso("pueblo_1_noche_2", 38, 22),
            96: paso("pueblo_1_noche_2", 38, 7)}
NPCS = {
    "loco_norte": vigilante(21, 7, "izq", [(14, 7), (23, 7)]),
    "loco_jardin": vigilante(8, 14, "der", miradas=[("der", 1500), ("abajo", 1900)]),
    "loco_centro": vigilante(25, 15, "izq", [(18, 15), (28, 15)]),
    "loco_sur": vigilante(16, 24, "arriba", miradas=[("arriba", 1600), ("der", 1300)]),
}
BARRILES = {(15, 5), (20, 22)}
