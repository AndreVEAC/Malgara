# mapas/prologo.py

FONDO_IMG = "recursos/fondos/desierto_prologo.png"  # Tu imagen de 1600x1200 px

# Posición inicial de Mateo (pegado a la izquierda, en el centro vertical)
INICIO_X, INICIO_Y = 2, 15

# Matriz de 30 filas x 40 columnas (1200x1600 px)
# 1 = Bloqueado (Muros/Cielo), 0 = Caminable, 9 = Puerta/Evento al final
MATRIZ = [
    # Filas 0 a 11: Cielo y montañas de fondo (Bloqueado)
    [1]*40, [1]*40, [1]*40, [1]*40, [1]*40, [1]*40, [1]*40, [1]*40, [1]*40, [1]*40, [1]*40, [1]*40,
    
    # Filas 12 a 18: Camino del desierto (Caminable). Al final de la fila hay '9' para activar diálogo.
    [1, 0, 0, 0, 0, 0, 0, 0, 0, 5, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 6, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 9, 1],
    [1, 0, 0, 0, 0, 0, 0, 0, 0, 5, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 6, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 9, 1],
    [1, 0, 0, 0, 0, 0, 0, 0, 0, 5, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 6, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 9, 1],
    [1, 0, 0, 0, 0, 0, 0, 0, 0, 5, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 6, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 9, 1],
    [1, 0, 0, 0, 0, 0, 0, 0, 0, 5, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 6, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 9, 1],
    [1, 0, 0, 0, 0, 0, 0, 0, 0, 5, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 6, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 9, 1],
    [1, 0, 0, 0, 0, 0, 0, 0, 0, 5, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 6, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 9, 1],

    # Filas 19 a 29: Rocas o precipicio en primer plano (Bloqueado)
    [1]*40, [1]*40, [1]*40, [1]*40, [1]*40, [1]*40, [1]*40, [1]*40, [1]*40, [1]*40, [1]*40
]