from mapas import hogar
from mapas.habitaciones_dia_2 import ABRIR_PUERTA, CERRAR_PUERTA


FONDO_IMG = "recursos/sprites/fondos/fondo_hogar_dia2.png"
AMBIENTE = hogar.AMBIENTE
VOLUMEN_AMBIENTE = hogar.VOLUMEN_AMBIENTE
INICIO_X, INICIO_Y = 1, 2
DICCIONARIO_OBJETOS = hogar.DICCIONARIO_OBJETOS

INTERACTUABLES = {
    10: "hogar_flores_marchitas",
    15: "hogar_libreta",
}
PORTALES = {
    97: {
        "mapa": "habitaciones_dia_2",
        "spawn_x": 2,
        "spawn_y": 3,
        "sonido_entrada": ABRIR_PUERTA,
        "sonido_llegada": CERRAR_PUERTA,
    },
    98: {
        "mapa": "casa_dia2",
        "sonido_entrada": ABRIR_PUERTA,
        "sonido_llegada": CERRAR_PUERTA,
    },
}

# Mismos muebles y luces del hogar original. La puerta inferior pasa a ser portal.
MATRIZ = [
    [98 if casilla == 13 else 1 if casilla in (3, 4, 5, 6, 7, 8, 9, 11, 12)
     else casilla for casilla in fila]
    for fila in hogar.MATRIZ
]
