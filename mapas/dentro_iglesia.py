from mapas.habitaciones_dia_2 import ABRIR_PUERTA, CERRAR_PUERTA
from mapas.iglesia_dia2 import REGRESO_INTERIOR


FONDO_IMG = "recursos/sprites/fondos/fondo_dentro_iglesia.png"
INICIO_X, INICIO_Y = 9, 13
REGRESO_TUNEL = (2, 1)
PUERTA_TUNEL = (2, 0)
PUERTA_PRINCIPAL = (9, 14)
MARCA_TUNEL_SUPERADO = "dia2:regreso_del_tunel"
AMBIENTE = "catedral"
VOLUMEN_AMBIENTE = 0.4

NPCS = {
    "morales": {
        "x": 9, "y": 11, "direccion": "abajo", "carpeta_sprite": "morales",
        "seguimiento": {"velocidad_ms": 225},
    },
    "lucas": {
        "x": 10, "y": 13, "direccion": "izq", "carpeta_sprite": "lucas",
        "seguimiento": {"velocidad_ms": 275},
    },
}

INTERACTUABLES = {
    2: "evento_banca",
    3: "evento_atril",
    4: "evento_puerta_izquierda",
    5: "evento_bano",
}
PORTALES = {
    97: {
        "mapa": "tunel",
        "sonido_entrada": ABRIR_PUERTA,
        "sonido_llegada": CERRAR_PUERTA,
    },
    98: {
        "mapa": "iglesia_dia2",
        "spawn_x": REGRESO_INTERIOR[0],
        "spawn_y": REGRESO_INTERIOR[1],
        "sonido_entrada": ABRIR_PUERTA,
        "sonido_llegada": CERRAR_PUERTA,
    },
}

MATRIZ = [[0] * 20 for _ in range(15)]
MATRIZ[0] = [1] * 20
MATRIZ[0][1:3] = [4, 4]
MATRIZ[0][17:19] = [5, 5]
MATRIZ[3][9:11] = [3, 3]
MATRIZ[5][:7] = MATRIZ[5][13:] = [1] * 7
for fila in (7, 9, 11, 13):
    MATRIZ[fila][2:6] = MATRIZ[fila][14:18] = [2] * 4
x, y = PUERTA_PRINCIPAL
MATRIZ[y][x] = 1
