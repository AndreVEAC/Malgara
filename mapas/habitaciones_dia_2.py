FONDO_IMG = "recursos/sprites/fondos/fondo_habitaciones_dia2.png"
INICIO_X, INICIO_Y = 0, 3  # Cama de Mateo, donde terminó la noche.

ABRIR_PUERTA = "recursos/sonidos/efectos/open_door.wav"
CERRAR_PUERTA = "recursos/sonidos/efectos/close_door.wav"

INTERACTUABLES = {2: "evento_cama_lucas"}
PORTALES = {
    98: {
        "mapa": "hogar_dia2",
        "spawn_x": 1,
        "spawn_y": 2,
        "sonido_entrada": ABRIR_PUERTA,
        "sonido_llegada": CERRAR_PUERTA,
    },
}

# 1 = pared o mueble, 2 = cama de Lucas, 98 = puerta inferior.
MATRIZ = [
    [1, 1, 1, 1, 1],
    [1, 1, 1, 1, 1],
    [1, 1, 0, 1, 2],
    [1, 0, 0, 0, 2],
    [0, 0, 98, 0, 0],
]
