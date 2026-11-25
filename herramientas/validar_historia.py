import json
import os
import sys

RUTA_DATOS = os.path.join(os.path.dirname(__file__), "..", "datos")

def cargar_todos_los_nodos():
    todos_los_nodos = {}
    archivos_json = [f for f in os.listdir(RUTA_DATOS) if f.endswith('.json')]
    
    for nombre_archivo in archivos_json:
        ruta = os.path.join(RUTA_DATOS, nombre_archivo)
        with open(ruta, 'r', encoding='utf-8-sig') as f:
            datos = json.load(f)
            declarativo = "formato" in datos and isinstance(datos.get("eventos"), dict)
            if declarativo:
                datos = datos["eventos"]
            for id_nodo, contenido in datos.items():
                if declarativo:
                    id_nodo = f"{nombre_archivo}::{id_nodo}"
                if id_nodo in todos_los_nodos:
                    print(f"⚠️ ADVERTENCIA: Nodo duplicado '{id_nodo}' en {nombre_archivo}")
                todos_los_nodos[id_nodo] = (nombre_archivo, contenido)
    return todos_los_nodos

def validar_arbol():
    nodos = cargar_todos_los_nodos()
    errores = 0
    total_opciones = 0

    print(f"🔍 Validando {len(nodos)} nodos narrativos en {RUTA_DATOS}...\n")

    for id_nodo, (archivo_origen, contenido) in nodos.items():
        opciones = contenido.get("opciones", [])
        referencias = [(f"Opción {i+1}", opcion.get("siguiente") or opcion.get("siguiente_evento"))
                       for i, opcion in enumerate(opciones)]
        referencias.append(("Continuación", contenido.get("siguiente") or contenido.get("siguiente_evento")))
        total_opciones += len(opciones)
        for origen, destino in referencias:
            if destino and "::" in id_nodo:
                destino = f"{archivo_origen}::{destino}"
            
            # Si el destino no es especial (como cambiar de estado a mapa) y no existe:
            if destino and destino not in nodos and not destino.startswith("MODO_MAPA:"):
                print(f"❌ ERROR [Enlace Roto]: Nodo '{id_nodo}' ({archivo_origen}) -> {origen} apunta a '{destino}', que no existe.")
                errores += 1

    print("\n" + "="*50)
    print(f"Resultados: {total_opciones} opciones revisadas.")
    if errores == 0:
        print("✅ ¡Validación exitosa! Todos los enlaces de la historia están correctos.")
    else:
        print(f"🚨 Se encontraron {errores} errores en el árbol de decisiones.")
    print("="*50)

if __name__ == "__main__":
    validar_arbol()
