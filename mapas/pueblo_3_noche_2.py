from mapas import pueblo_3_dia_2
from mapas.geografia_noche_2 import marcar, matriz_desde, objetos, paso, vigilante

FONDO_IMG = "recursos/sprites/fondos/fondo_pueblo_3_noche_2.png"
AMBIENTE = "noche_calmada"
INICIO_X, INICIO_Y = 1, 18
DICCIONARIO_OBJETOS = objetos()
MATRIZ = matriz_desde(pueblo_3_dia_2)
marcar(MATRIZ, ((10, 5), (14, 12), (14, 24)), 20)
marcar(MATRIZ, ((11, 14), (12, 14), (13, 15), (8, 18)), 22)
marcar(MATRIZ, ((x, 0) for x in (11, 12, 13)), 98)
MATRIZ[18][0] = 97
MATRIZ[18][16] = MATRIZ[18][17] = 0
PORTALES = {98: paso("pueblo_2_noche_2", 31, 28), 97: paso("casa_noche_2", 18, 18)}
NPCS = {
    "loco_clinica": vigilante(14, 18, "der", [(20, 18), (14, 18)]),
    "loco_calle": vigilante(13, 8, "abajo", miradas=[("abajo", 1300), ("der", 1700)]),
    "loco_sur": vigilante(10, 24, "der", [(13, 24), (10, 24)]),
}
BARRILES = {(22, 16), (21, 3)}
