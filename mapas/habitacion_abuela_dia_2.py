FONDO_IMG = "recursos/sprites/fondos/fondo_habitacion_abuela.png"
CENTRAR_FONDO = True
AMBIENTE = "miradas"
INICIO_X, INICIO_Y = 4, 1

MATRIZ = [
    [1, 1, 1, 1, 98],
    [11, 11, 12, 0, 0],
    [10, 10, 12, 0, 0],
    [0, 0, 12, 0, 0],
    [13, 0, 0, 0, 0],
]
INTERACTUABLES = {
    10: "cajon_inventario",
    11: "foto_cuarto",
    12: "cama_cuarto",
    13: "planta_cuarto",
    98: "salida_cuarto",
}
