from mapas.habitaciones_dia_2 import ABRIR_PUERTA, CERRAR_PUERTA


FONDO_IMG = "recursos/sprites/fondos/fondo_casa_abuela.png"
CENTRAR_FONDO = True
AMBIENTE = 'miradas'
INICIO_X, INICIO_Y = 8, 5
MATRIZ = [
    [1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
    [1, 12, 1, 1, 1, 1, 1, 1, 1, 1],
    [1, 12, 13, 1, 13, 1, 1, 11, 11, 1],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [10, 10, 10, 10, 10, 10, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 98, 0],
]
INTERACTUABLES = {
    10: "cocina_abuela", 11: "sillon_abuela", 12: "abuela_puerta_cerrada", 13: "mueble_abuela",
}
PORTALES = {98: {
    'mapa': 'llegada_dia_2', 'spawn_x': 15, 'spawn_y': 5,
    'sonido_entrada': ABRIR_PUERTA, 'sonido_llegada': CERRAR_PUERTA,
}}
NPCS = {'abuela': {'x': 4, 'y': 4, 'carpeta_sprite': 'abuela'}}
