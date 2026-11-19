"""Interior de 400x300; casillas de 40 px. MATRIZ[y][x]."""
FONDO_IMG = "recursos/sprites/fondos/fondo_hogar.png"
CENTRAR_FONDO = True
AMBIENTE = "hogar"
VOLUMEN_AMBIENTE = 0.1
INICIO_X, INICIO_Y = 8, 6

# Sin AMBIENTE: continúa la música del mapa anterior.
NPCS = {
    "lucas": {
        "x": 7, "y": 6, "direccion": "izq", "visible": True,
        "carpeta_sprite": "lucas", "comportamiento": "estatico",
    }
}
INTERACTUABLES = {
    2: "hogar_habitacion", 3: "hogar_bano", 4: "hogar_armarios",
    5: "hogar_estufa", 6: "hogar_fregadero", 7: "hogar_planta",
    8: "hogar_lampara", 9: "hogar_sofa", 10: "hogar_flores",
    11: "hogar_mesa", 12: "hogar_silla", 13: "hogar_salida",
    15: "hogar_libreta",
}
PORTALES = {
    97: {
        "mapa": "habitaciones",
        "spawn_x": 2,
        "spawn_y": 3,
        "sonido_entrada": (
            "recursos/sonidos/efectos/open_door.wav"
        ),
    },
}
TRIGGERS_PISAR = {}
DICCIONARIO_OBJETOS = {
        14: {
        "ruta": "recursos/sprites/efectos/Luz1.png",
        "colision": True,
        "profundidad": True,
        "ancho_casillas": 4,
        "alto_casillas": 4
    }
}  # Los muebles ya están dibujados en el fondo.
BLOQUEOS = []

# 0 libre; 1 muro; los otros números bloquean y permiten interactuar.
# La fila 7 solo tiene 20 píxeles visibles: está totalmente bloqueada.
MATRIZ = [
    # 0  1  2  3  4  5  6  7  8  9
    [1, 1, 1, 1, 1, 1, 1, 1, 1, 1],       # 0
    [1, 97, 1, 1, 8, 4, 4, 5, 6, 7],       # 1
    [3, 0, 0, 0, 0, 0, 0, 0, 0, 0],       # 2
    [0, 0, 9, 9, 0, 0, 0,11,15, 0],       # 3
    [9, 0, 0, 0, 0, 0,12,11,11,12],       # 4
    [9, 0, 0, 0, 0, 0, 0,10,11, 0],       # 5
    [0, 0, 9, 9, 0, 0, 0, 0, 0, 0],       # 6
    [1, 1, 14, 1, 1, 14, 1, 1,13, 1],       # 7
]

DESTINO_SOFA = {"lucas": (1, 4), "mateo": (2, 4)}
ASIENTOS = {"mateo": (6, 4), "lucas": (9, 4)}
PUERTA_HABITACION = (1, 1)
