import json
import os

RUTAS_ARCHIVOS = {
    "productos": "data/productos.json",
    "lotes": "data/lotes.json",
    "movimientos": "data/movimientos.json",
    "ventas": "data/ventas.json",
}


def cargar_datos_json(ruta):
    """Carga los datos desde un archivo JSON. Retorna lista vacía si no existe o está corrupto."""
    if not os.path.exists(ruta):
        return []
    try:
        with open(ruta, "r", encoding="utf-8") as archivo:
            return json.load(archivo)
    except (json.JSONDecodeError, OSError):
        print(f"Advertencia: No se pudo leer {ruta}. Se iniciará con datos vacíos.")
        return []


def guardar_datos_json(ruta, datos):
    """Guarda una lista de datos en un archivo JSON."""
    os.makedirs(os.path.dirname(ruta), exist_ok=True)
    try:
        with open(ruta, "w", encoding="utf-8") as archivo:
            json.dump(datos, archivo, indent=4, ensure_ascii=False)
        return True
    except OSError as e:
        print(f"Error al guardar en {ruta}: {e}")
        return False


def guardar_todo(datos):
    """Guarda todas las colecciones en sus respectivos archivos JSON."""
    for clave, ruta in RUTAS_ARCHIVOS.items():
        guardar_datos_json(ruta, datos[clave])
    print("\n[✓] Todos los datos han sido guardados exitosamente en data/")


def mostrar_menu():
    print("\n==================== AGROCONTROL CBA ====================")
    print("1. Gestión de productos")
    print("2. Gestión de lotes productivos")
    print("3. Movimientos de inventario")
    print("4. Registrar venta")
    print("5. Consultar ventas")
    print("6. Alertas de stock")
    print("7. Reportes")
    print("8. Guardar datos")
    print("0. Salir")
    print("=========================================================")


def main():
    # Carga inicial de datos (RF17)
    datos = {
        "productos": cargar_datos_json(RUTAS_ARCHIVOS["productos"]),
        "lotes": cargar_datos_json(RUTAS_ARCHIVOS["lotes"]),
        "movimientos": cargar_datos_json(RUTAS_ARCHIVOS["movimientos"]),
        "ventas": cargar_datos_json(RUTAS_ARCHIVOS["ventas"]),
    }

    print("Carga inicial completada:")
    for clave, lista in datos.items():
        print(f" - {clave.capitalize()}: {len(lista)} registros cargados.")

    mantenimiento = True
    while mantenimiento:
        mostrar_menu()
        opcion = input("Seleccione una opción: ").strip()

        if opcion == "1":
            print("\n[Módulo en construcción: Gestión de productos]")
        elif opcion == "2":
            print("\n[Módulo en construcción: Gestión de lotes productivos]")
        elif opcion == "3":
            print("\n[Módulo en construcción: Movimientos de inventario]")
        elif opcion == "4":
            print("\n[Módulo en construcción: Registrar venta]")
        elif opcion == "5":
            print("\n[Módulo en construcción: Consultar ventas]")
        elif opcion == "6":
            print("\n[Módulo en construcción: Alertas de stock]")
        elif opcion == "7":
            print("\n[Módulo en construcción: Reportes]")
        elif opcion == "8":
            guardar_todo(datos)
        elif opcion == "0":
            guardar_todo(datos)
            print("\nSaliendo de AgroControl CBA. ¡Hasta luego!")
            mantenimiento = False
        else:
            print("\nOpción no válida. Intente nuevamente.")


if __name__ == "__main__":
    main()