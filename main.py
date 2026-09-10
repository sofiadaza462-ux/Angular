import json
import os

RUTAS_ARCHIVOS = {
    "productos": "data/productos.json",
    "lotes": "data/lotes.json",
    "movimientos": "data/movimientos.json",
    "ventas": "data/ventas.json",
}


# ==============================================================================
# PERSISTENCIA Y CARGA DE DATOS (JSON)
# ==============================================================================
def cargar_datos_json(ruta):
    """Carga datos desde un archivo JSON. Retorna lista vacía si no existe o falla."""
    if not os.path.exists(ruta):
        return []
    try:
        with open(ruta, "r", encoding="utf-8") as archivo:
            return json.load(archivo)
    except (json.JSONDecodeError, OSError):
        print(f"Advertencia: No se pudo leer {ruta}. Se iniciará con lista vacía.")
        return []


def guardar_datos_json(ruta, datos):
    """Guarda una colección en su correspondiente archivo JSON."""
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


# ==============================================================================
# VALIDACIONES DE ENTRADA
# ==============================================================================
def leer_texto(mensaje):
    """Solicita un texto no vacío."""
    while True:
        valor = input(mensaje).strip()
        if valor:
            return valor
        print("Error: El campo no puede estar vacío. Intente de nuevo.")


def leer_numero_positivo(mensaje, es_entero=False):
    """Solicita un número mayor a cero."""
    while True:
        valor = input(mensaje).strip()
        try:
            num = int(valor) if es_entero else float(valor)
            if num > 0:
                return num
            print("Error: Debe ingresar un valor mayor a 0.")
        except ValueError:
            print("Error: Por favor ingrese un número válido.")


def leer_numero_no_negativo(mensaje, es_entero=False):
    """Solicita un número mayor o igual a cero."""
    while True:
        valor = input(mensaje).strip()
        try:
            num = int(valor) if es_entero else float(valor)
            if num >= 0:
                return num
            print("Error: El valor no puede ser negativo.")
        except ValueError:
            print("Error: Por favor ingrese un número válido.")


# ==============================================================================
# MÓDULO: GESTIÓN DE PRODUCTOS
# ==============================================================================
def buscar_producto_por_codigo(productos, codigo):
    """Busca un producto por su código (exacto)."""
    codigo_upper = codigo.upper()
    for prod in productos:
        if prod["codigo"].upper() == codigo_upper:
            return prod
    return None


def registrar_producto(productos):
    """RF01: Registrar un nuevo producto con código único y validaciones."""
    print("\n--- Registrar Nuevo Producto ---")
    
    while True:
        codigo = leer_texto("Ingrese el código del producto (ej. P001): ").upper()
        if buscar_producto_por_codigo(productos, codigo):
            print(f"Error: El código '{codigo}' ya está registrado (PF001). Intente con otro.")
        else:
            break

    nombre = leer_texto("Ingrese el nombre del producto: ")
    categoria = leer_texto("Ingrese la categoría (ej. Hortalizas, Frutas): ")
    unidad = leer_texto("Ingrese la unidad de medida (ej. kg, unidad, manojo): ")
    precio = leer_numero_positivo("Ingrese el precio unitario (> 0): ")
    stock_minimo = leer_numero_no_negativo("Ingrese el stock mínimo (>= 0): ", es_entero=True)

    nuevo_producto = {
        "codigo": codigo,
        "nombre": nombre,
        "categoria": categoria,
        "unidad": unidad,
        "precio": precio,
        "stock_minimo": stock_minimo,
        "activo": True
    }

    productos.append(nuevo_producto)
    guardar_datos_json(RUTAS_ARCHIVOS["productos"], productos)
    print(f"\n[✓] Producto '{nombre}' ({codigo}) registrado correctamente.")


def listar_productos(productos):
    """RF02: Listar productos activos o buscar por código / parte del nombre."""
    if not productos:
        print("\nNo hay productos registrados en el sistema.")
        return

    print("\n--- Opciones de Consulta ---")
    print("1. Ver todos los productos activos")
    print("2. Buscar producto por código o nombre")
    print("3. Ver todos los productos (incluye inactivos)")
    opcion = input("Seleccione una opción: ").strip()

    filtro = ""
    solo_activos = True

    if opcion == "2":
        filtro = input("Ingrese texto a buscar (código o parte del nombre): ").strip().lower()
    elif opcion == "3":
        solo_activos = False

    resultados = []
    for p in productos:
        if solo_activos and not p.get("activo", True):
            continue
        if filtro:
            codigo_match = filtro in p["codigo"].lower()
            nombre_match = filtro in p["nombre"].lower()
            if not (codigo_match or nombre_match):
                continue
        resultados.append(p)

    if not resultados:
        print("\nNo se encontraron productos con los criterios especificados.")
        return

    print("\n" + "="*80)
    print(f"{'CÓDIGO':<8} | {'NOMBRE':<22} | {'CATEGORÍA':<15} | {'UNIDAD':<8} | {'PRECIO':<10} | {'MÍN.':<5} | {'ESTADO'}")
    print("="*80)
    for p in resultados:
        estado = "Activo" if p.get("activo", True) else "Inactivo"
        precio_fmt = f"${p['precio']:,.0f}"
        print(f"{p['codigo']:<8} | {p['nombre']:<22} | {p['categoria']:<15} | {p['unidad']:<8} | {precio_fmt:<10} | {p['stock_minimo']:<5} | {estado}")
    print("="*80)


def actualizar_producto(productos):
    """RF03: Actualizar campos de un producto manteniendo el código original."""
    print("\n--- Actualizar Producto ---")
    codigo = input("Ingrese el código del producto a actualizar: ").strip().upper()
    producto = buscar_producto_por_codigo(productos, codigo)

    if not producto:
        print(f"Error: No se encontró ningún producto con el código '{codigo}'.")
        return

    print(f"\nActualizando información para [{producto['codigo']}] {producto['nombre']}")
    print("(Presione ENTER sin escribir nada para conservar el valor actual)\n")

    nuevo_nombre = input(f"Nombre actual [{producto['nombre']}]: ").strip()
    if nuevo_nombre:
        producto["nombre"] = nuevo_nombre

    nueva_cat = input(f"Categoría actual [{producto['categoria']}]: ").strip()
    if nueva_cat:
        producto["categoria"] = nueva_cat

    nueva_unidad = input(f"Unidad actual [{producto['unidad']}]: ").strip()
    if nueva_unidad:
        producto["unidad"] = nueva_unidad

    nuevo_precio = input(f"Precio actual [{producto['precio']}]: ").strip()
    if nuevo_precio:
        try:
            val = float(nuevo_precio)
            if val > 0:
                producto["precio"] = val
            else:
                print("Precio inválido. Se conserva el valor anterior.")
        except ValueError:
            print("Entrada no numérica. Se conserva el valor anterior.")

    nuevo_stock_min = input(f"Stock mínimo actual [{producto['stock_minimo']}]: ").strip()
    if nuevo_stock_min:
        try:
            val = int(nuevo_stock_min)
            if val >= 0:
                producto["stock_minimo"] = val
            else:
                print("Stock mínimo inválido. Se conserva el valor anterior.")
        except ValueError:
            print("Entrada no numérica. Se conserva el valor anterior.")

    guardar_datos_json(RUTAS_ARCHIVOS["productos"], productos)
    print(f"\n[✓] Producto '{codigo}' actualizado exitosamente.")


def desactivar_producto(productos):
    """RF04: Desactivar un producto (borrado lógico)."""
    print("\n--- Desactivar Producto ---")
    codigo = input("Ingrese el código del producto a desactivar: ").strip().upper()
    producto = buscar_producto_por_codigo(productos, codigo)

    if not producto:
        print(f"Error: No existe un producto con el código '{codigo}'.")
        return

    if not producto.get("activo", True):
        print(f"El producto '{codigo}' ya se encuentra desactivado.")
        return

    confirmar = input(f"¿Desea desactivar el producto '{producto['nombre']}'? (s/n): ").strip().lower()
    if confirmar == 's':
        producto["activo"] = False
        guardar_datos_json(RUTAS_ARCHIVOS["productos"], productos)
        print(f"\n[✓] Producto '{codigo}' desactivado correctamente.")
    else:
        print("\nOperación cancelada.")


def menu_productos(productos):
    """Submenú interactivo para el módulo de gestión de productos."""
    while True:
        print("\n----- MÓDULO DE PRODUCTOS -----")
        print("1. Registrar producto")
        print("2. Consultar / Listar productos")
        print("3. Actualizar producto")
        print("4. Desactivar producto")
        print("0. Volver al menú principal")
        opcion = input("Seleccione una opción: ").strip()

        if opcion == "1":
            registrar_producto(productos)
        elif opcion == "2":
            listar_productos(productos)
        elif opcion == "3":
            actualizar_producto(productos)
        elif opcion == "4":
            desactivar_producto(productos)
        elif opcion == "0":
            break
        else:
            print("Opción inválida. Intente de nuevo.")


# ==============================================================================
# MENÚ PRINCIPAL Y CONTROL DE FLUJO
# ==============================================================================
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
    datos = {
        "productos": cargar_datos_json(RUTAS_ARCHIVOS["productos"]),
        "lotes": cargar_datos_json(RUTAS_ARCHIVOS["lotes"]),
        "movimientos": cargar_datos_json(RUTAS_ARCHIVOS["movimientos"]),
        "ventas": cargar_datos_json(RUTAS_ARCHIVOS["ventas"]),
    }

    mantenimiento = True
    while mantenimiento:
        mostrar_menu()
        opcion = input("Seleccione una opción: ").strip()

        if opcion == "1":
            menu_productos(datos["productos"])
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