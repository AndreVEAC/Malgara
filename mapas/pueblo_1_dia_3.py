from copy import deepcopy

from mapas import pueblo_1_dia_2, pueblo_1_noche_2
from mapas.geografia_noche_2 import marcar, matriz_desde, objetos

FONDO_IMG = "recursos/sprites/fondos/fondo_pueblo_1_dia_3.png"
AMBIENTE = "ultimo_paseo"
INICIO_X, INICIO_Y = pueblo_1_noche_2.JUNTO_BARRIL
BARRILES = set(pueblo_1_noche_2.BARRILES)
DICCIONARIO_OBJETOS = objetos()
DICCIONARIO_OBJETOS.update(deepcopy(pueblo_1_dia_2.DICCIONARIO_OBJETOS))
DICCIONARIO_OBJETOS[22]["ruta"] = "recursos/sprites/objetos/caja_bloqueo.png"
MATRIZ = matriz_desde(pueblo_1_dia_2, conservar_postes=True)
marcar(MATRIZ, ((5, 13), (24, 14), (37, 11)), 0)
marcar(MATRIZ, ((0, y) for y in range(20, 25)), 22)
INTERACTUABLES = {89: "dia3_camino_pendiente"}
for x, y in ((0, 7), (39, 7), (39, 14), (39, 22), (9, 29)):
    MATRIZ[y][x] = 89

