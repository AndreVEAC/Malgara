from mapas import hogar_dia2

FONDO_IMG = "recursos/sprites/fondos/fondo_hogar_noche_2.png"
CENTRAR_FONDO = True
AMBIENTE = "noche_calmada"
INICIO_X, INICIO_Y = 4, 5
MATRIZ = [[1 if celda in (97, 98, 14, 15, 10) else celda for celda in fila]
          for fila in hogar_dia2.MATRIZ]
