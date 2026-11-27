"""Datos compartidos por los mapas de la segunda noche."""
from copy import deepcopy

from mapas.pueblo_1_noche_1 import DICCIONARIO_OBJETOS as OBJETOS_NOCHE


def matriz_desde(origen, *, conservar_postes=False):
    reemplazos = dict.fromkeys(range(90, 100), 1)
    if not conservar_postes:
        reemplazos[20] = 0
    return [[reemplazos.get(celda, celda) for celda in fila] for fila in origen.MATRIZ]


def objetos():
    return deepcopy(OBJETOS_NOCHE)


def marcar(matriz, casillas, valor):
    for x, y in casillas:
        matriz[y][x] = valor


def paso(destino, x, y):
    return {"mapa": destino, "spawn_x": x, "spawn_y": y}


def vigilante(x, y, direccion, ruta=(), miradas=()):
    return {
        "x": x, "y": y, "direccion": direccion, "carpeta_sprite": "loco",
        "comportamiento": "vigilante",
        "vigilancia": {"luz": "recursos/sprites/efectos/luz_3.png",
                       "ruta": list(ruta), "miradas": list(miradas)},
    }
