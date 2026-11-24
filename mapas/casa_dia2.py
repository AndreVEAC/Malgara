from mapas import casa
from mapas.habitaciones_dia_2 import ABRIR_PUERTA, CERRAR_PUERTA


FONDO_IMG = "recursos/sprites/fondos/fondo_casa_dia_2.png"
AMBIENTE = "miradas"
VOLUMEN_AMBIENTE = 0.4
INICIO_X, INICIO_Y = casa.PUERTA_X, casa.PUERTA_Y + 1
DICCIONARIO_OBJETOS = casa.DICCIONARIO_OBJETOS

NPCS = {
    "lucas": {
        "x": 16,
        "y": 17,
        "direccion": "der",
        "carpeta_sprite": "lucas",
        "comportamiento": "estatico",
    },
}
PORTALES = {
    98: {"mapa": "pueblo_1_dia_2", "spawn_x": 9, "spawn_y": 28},
    96: {"mapa": "pueblo_3_dia_2", "spawn_x": 1, "spawn_y": 18},
    97: {
        "mapa": "hogar_dia2",
        "spawn_x": 8,
        "spawn_y": 6,
        "sonido_entrada": ABRIR_PUERTA,
        "sonido_llegada": CERRAR_PUERTA,
    },
}

# Se mantienen las posiciones de árboles, postes, macetas y tronco.
# Se liberan las antiguas casillas de los vecinos y las bancas retiradas.
MATRIZ = [
    [0 if casilla in (9, 12, 13, 14, 98) else
     1 if casilla in (2, 3, 7, 8, 15, 16) else casilla
     for casilla in fila]
    for fila in casa.MATRIZ
]

# Los muros llegan hasta la base de las fachadas dibujadas en el fondo.
for fila in (3, 10, 16, 23):
    MATRIZ[fila][7:13] = [1] * 6
    MATRIZ[fila][14:20] = [1] * 6
MATRIZ[casa.PUERTA_Y][casa.PUERTA_X] = 97
MATRIZ[0][2:5] = [98] * 3
MATRIZ[18][19] = 96
