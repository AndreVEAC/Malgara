from mapas.dentro_iglesia import REGRESO_TUNEL
from mapas.habitaciones_dia_2 import ABRIR_PUERTA, CERRAR_PUERTA


FONDO_IMG = "recursos/sprites/fondos/fondo_tunel.png"
INICIO_X, INICIO_Y = 1, 1
SALIDA = (0, 1)
PUERTA_HIERRO = (18, 0)
FRENTE_A_PUERTA = (18, 1)
RAMAS = (3, 9, 15)

NPCS = {
    "morales": {
        "x": 2, "y": 1, "direccion": "izq", "carpeta_sprite": "morales",
        "seguimiento": {"velocidad_ms": 225},
    },
    "lucas": {
        "x": 0, "y": 1, "direccion": "der", "carpeta_sprite": "lucas",
        "seguimiento": {"velocidad_ms": 150},
    },
}
for indice, (x, miradas) in enumerate(zip(RAMAS, (
    (("arriba", 3400), ("abajo", 2400)),
    (("abajo", 1300), ("arriba", 4100), ("abajo", 2500)),
    (("arriba", 2500), ("abajo", 1750)),
)), 1):
    NPCS[f"vigilante_{indice}"] = {
        "x": x,
        "y": 3,
        "direccion": miradas[0][0],
        "carpeta_sprite": "loco",
        "comportamiento": "vigilante",
        "vigilancia": {
            "luz": "recursos/sprites/efectos/luz_3.png",
            "miradas": miradas,
            "anclajes_luz": {"arriba": (20, 18), "abajo": (20, 24),
                             "izq": (3, 23), "der": (37, 23)},
        },
    }

INTERACTUABLES = {2: "evento_puerta_hierro"}
PORTALES = {
    97: {
        "mapa": "dentro_iglesia",
        "spawn_x": REGRESO_TUNEL[0],
        "spawn_y": REGRESO_TUNEL[1],
        "sonido_entrada": ABRIR_PUERTA,
        "sonido_llegada": CERRAR_PUERTA,
    },
}
MATRIZ = [[1] * 20 for _ in range(4)]
MATRIZ[1] = [0] * 20
for x in RAMAS:
    MATRIZ[2][x] = MATRIZ[3][x] = 0
x, y = PUERTA_HIERRO
MATRIZ[y][x] = 2
