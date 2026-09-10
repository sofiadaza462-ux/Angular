import os


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
    # Asegurar existencia de la carpeta de datos
    os.makedirs("data", exist_ok=True)

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
            print("\n[Módulo en construcción: Guardar datos]")
        elif opcion == "0":
            print("\nSaliendo de AgroControl CBA. ¡Hasta luego!")
            mantenimiento = False
        else:
            print("\nOpción no válida. Intente nuevamente.")


if __name__ == "__main__":
    main()