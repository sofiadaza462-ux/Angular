from datetime import datetime
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
# VALIDACIONES DE ENTRADA Y FORMATOS
# ==============================================================================
def leer_texto(mensaje):
    """Solicita un texto no vacío."""
    while True:
        valor = input(mensaje).strip()
        if valor:
            return valor
        print("Error: El campo no puede estar vacío. Intente de nuevo.")


def leer_entero_positivo(mensaje):
    """Solicita un entero estricto mayor a cero (sin decimales)."""
    while True:
        valor = input(mensaje).strip()
        try:
            num = int(valor)
            if num > 0:
                return num
            print("Error: Debe ingresar un valor entero mayor a 0.")
        except ValueError:
            print("Error: Ingrese un valor entero válido (sin decimales).")


def leer_entero_no_negativo(mensaje):
    """Solicita un entero estricto mayor o igual a cero (sin decimales)."""
    while True:
        valor = input(mensaje).strip()
        try:
            num = int(valor)
            if num >= 0:
                return num
            print("Error: El valor no puede ser negativo.")
        except ValueError:
            print("Error: Ingrese un valor entero válido (sin decimales).")


def leer_numero_positivo(mensaje):
    """Solicita un número (float o int) positivo."""
    while True:
        valor = input(mensaje).strip()
        try:
            num = float(valor)
            if num > 0:
                return num
            print("Error: Debe ingresar un valor mayor a 0.")
        except ValueError:
            print("Error: Por favor ingrese un número válido.")


def leer_fecha_ddmmyyyy(mensaje):
    """Solicita una fecha con el formato estricto dd/mm/aaaa."""
    while True:
        fecha_str = input(mensaje).strip()
        try:
            fecha_dt = datetime.strptime(fecha_str, "%d/%m/%Y")
            return fecha_dt.strftime("%d/%m/%Y")
        except ValueError:
            print("Error: La fecha debe tener el formato dd/mm/aaaa (ejemplo: 15/08/2026).")


def generar_id_secuencial(coleccion, prefijo, campo_id):
    """Genera IDs secuenciales tipo M0001 o V0001 o L001."""
    if not coleccion:
        return f"{prefijo}001"
    
    max_num = 0
    for item in coleccion:
        id_str = item.get(campo_id, "")
        if id_str.startswith(prefijo):
            try:
                num = int(id_str[len(prefijo):])
                if num > max_num:
                    max_num = num
            except ValueError:
                continue
    return f"{prefijo}{max_num + 1:03d}"


# ==============================================================================
# MÓDULO: GESTIÓN DE PRODUCTOS
# ==============================================================================
def buscar_producto_por_codigo(productos, codigo):
    """Busca un producto por su código (exacto en mayúsculas)."""
    codigo_upper = codigo.upper()
    for prod in productos:
        if prod["codigo"].upper() == codigo_upper:
            return prod
    return None


def registrar_producto(productos):
    """RF01: Registrar un nuevo producto con código único, precio entero y stock mínimo sin decimales."""
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
    precio = leer_entero_positivo("Ingrese el precio unitario entero (> 0, sin decimales): ")
    stock_minimo = leer_entero_no_negativo("Ingrese el stock mínimo (>= 0, sin decimales): ")

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

    print("\n" + "="*85)
    print(f"{'CÓDIGO':<8} | {'NOMBRE':<22} | {'CATEGORÍA':<15} | {'UNIDAD':<8} | {'PRECIO':<12} | {'MÍNIMO':<8} | {'ESTADO'}")
    print("="*85)
    for p in resultados:
        estado = "Activo" if p.get("activo", True) else "Inactivo"
        precio_fmt = f"${p['precio']:,}".replace(",", ".")
        stock_min_fmt = f"{p['stock_minimo']:,}".replace(",", ".")
        print(f"{p['codigo']:<8} | {p['nombre']:<22} | {p['categoria']:<15} | {p['unidad']:<8} | {precio_fmt:<12} | {stock_min_fmt:<8} | {estado}")
    print("="*85)


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

    nuevo_precio = input(f"Precio actual [${producto['precio']:,}]: ").strip().replace(".", "")
    if nuevo_precio:
        try:
            val = int(nuevo_precio)
            if val > 0:
                producto["precio"] = val
            else:
                print("Precio inválido. Debe ser un entero positivo.")
        except ValueError:
            print("Entrada inválida. Debe ser un número entero.")

    nuevo_stock_min = input(f"Stock mínimo actual [{producto['stock_minimo']:,}]: ").strip().replace(".", "")
    if nuevo_stock_min:
        try:
            val = int(nuevo_stock_min)
            if val >= 0:
                producto["stock_minimo"] = val
            else:
                print("Stock mínimo inválido. Debe ser mayor o igual a 0.")
        except ValueError:
            print("Entrada inválida. Debe ser un número entero.")

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
# MÓDULO: GESTIÓN DE LOTES PRODUCTIVOS
# ==============================================================================
def buscar_lote_por_id(lotes, id_lote):
    """Busca un lote por su id_lote (exacto en mayúsculas)."""
    id_upper = id_lote.upper()
    for lote in lotes:
        if lote["id_lote"].upper() == id_upper:
            return lote
    return None


def registrar_lote(datos):
    """RF05: Registrar lote asociado únicamente a productos existentes y activos."""
    print("\n--- Registrar Lote Productivo ---")
    
    id_lote = generar_id_secuencial(datos["lotes"], "L", "id_lote")
    print(f"ID del nuevo lote asignado automáticamente: {id_lote}")

    codigo_prod = leer_texto("Ingrese el código del producto asociado: ").upper()
    prod = buscar_producto_por_codigo(datos["productos"], codigo_prod)

    if not prod:
        print(f"Error: No existe el producto con código '{codigo_prod}'.")
        return

    if not prod.get("activo", True):
        print(f"Error: El producto '{codigo_prod}' está desactivado. No se pueden crear nuevos lotes.")
        return

    fecha_siembra = leer_fecha_ddmmyyyy("Ingrese la fecha de siembra (dd/mm/aaaa): ")
    area_m2 = leer_numero_positivo("Ingrese el área en m² (> 0): ")

    nuevo_lote = {
        "id_lote": id_lote,
        "producto_codigo": codigo_prod,
        "fecha_siembra": fecha_siembra,
        "area_m2": area_m2,
        "cantidad_producida": 0,
        "estado": "EN_PRODUCCION"
    }

    datos["lotes"].append(nuevo_lote)
    guardar_datos_json(RUTAS_ARCHIVOS["lotes"], datos["lotes"])
    print(f"\n[✓] Lote '{id_lote}' para el producto '{prod['nombre']}' registrado exitosamente.")


def cosechar_lote(datos):
    """RF07 y Regla 5: Cosechar lote, ingresar cantidad y generar movimiento automático de inventario."""
    print("\n--- Cosechar Lote Productivo ---")
    id_lote = input("Ingrese el ID del lote a cosechar (ej. L001): ").strip().upper()
    lote = buscar_lote_por_id(datos["lotes"], id_lote)

    if not lote:
        print(f"Error (PF003): El lote '{id_lote}' no existe.")
        return

    if lote["estado"] == "COSECHADO":
        print(f"Error (PF004): El lote '{id_lote}' ya fue cosechado previamente. No se permite doble cosecha.")
        return

    if lote["estado"] == "CANCELADO":
        print(f"Error: El lote '{id_lote}' está CANCELADO y no se puede cosechar.")
        return

    cantidad = leer_entero_positivo("Ingrese la cantidad producida cosechada (entero > 0): ")
    fecha_cosecha = datetime.now().strftime("%d/%m/%Y %H:%M")

    # Actualizar estado del lote
    lote["cantidad_producida"] = cantidad
    lote["estado"] = "COSECHADO"

    # Generar automáticamente movimiento de entrada en inventario
    id_mov = generar_id_secuencial(datos["movimientos"], "M", "id")
    nuevo_movimiento = {
        "id": id_mov,
        "producto_codigo": lote["producto_codigo"],
        "tipo": "ENTRADA",
        "cantidad": cantidad,
        "motivo": f"Cosecha lote {id_lote}",
        "fecha": fecha_cosecha
    }

    datos["movimientos"].append(nuevo_movimiento)
    
    guardar_datos_json(RUTAS_ARCHIVOS["lotes"], datos["lotes"])
    guardar_datos_json(RUTAS_ARCHIVOS["movimientos"], datos["movimientos"])
    
    print(f"\n[✓] Lote '{id_lote}' cosechado exitosamente.")
    print(f"[✓] Se generó automáticamente la entrada de inventario {id_mov} por {cantidad:,} unidades.")


def cambiar_estado_lote(lotes):
    """RF06: Cambiar estado del lote a EN_PRODUCCION o CANCELADO (la cosecha tiene su propia opción)."""
    print("\n--- Cambiar Estado de Lote ---")
    id_lote = input("Ingrese el ID del lote: ").strip().upper()
    lote = buscar_lote_por_id(lotes, id_lote)

    if not lote:
        print(f"Error: El lote '{id_lote}' no existe.")
        return

    print(f"Estado actual del lote '{id_lote}': {lote['estado']}")
    if lote["estado"] == "COSECHADO":
        print("Atención: Un lote COSECHADO no se puede cambiar a otros estados.")
        return

    print("Estados disponibles: [1] EN_PRODUCCION  [2] CANCELADO")
    opc = input("Seleccione nuevo estado: ").strip()

    if opc == "1":
        lote["estado"] = "EN_PRODUCCION"
    elif opc == "2":
        lote["estado"] = "CANCELADO"
    else:
        print("Opción inválida. Operación cancelada.")
        return

    guardar_datos_json(RUTAS_ARCHIVOS["lotes"], lotes)
    print(f"\n[✓] Estado del lote '{id_lote}' cambiado a '{lote['estado']}'.")


def listar_lotes(lotes):
    """Listar todos los lotes registrados."""
    if not lotes:
        print("\nNo hay lotes registrados.")
        return

    print("\n" + "="*75)
    print(f"{'ID LOTE':<8} | {'PROD. CÓD':<10} | {'FECHA SIEMBRA':<14} | {'ÁREA (m²)':<10} | {'CANT.':<8} | {'ESTADO'}")
    print("="*75)
    for l in lotes:
        cant_fmt = f"{l['cantidad_producida']:,}".replace(",", ".")
        area_fmt = f"{l['area_m2']:,.1f}"
        print(f"{l['id_lote']:<8} | {l['producto_codigo']:<10} | {l['fecha_siembra']:<14} | {area_fmt:<10} | {cant_fmt:<8} | {l['estado']}")
    print("="*75)


def menu_lotes(datos):
    """Submenú interactivo para el módulo de lotes."""
    while True:
        print("\n----- MÓDULO DE LOTES PRODUCTIVOS -----")
        print("1. Registrar lote")
        print("2. Cosechar lote")
        print("3. Cambiar estado de lote")
        print("4. Listar lotes")
        print("0. Volver al menú principal")
        opcion = input("Seleccione una opción: ").strip()

        if opcion == "1":
            registrar_lote(datos)
        elif opcion == "2":
            cosechar_lote(datos)
        elif opcion == "3":
            cambiar_estado_lote(datos["lotes"])
        elif opcion == "4":
            listar_lotes(datos["lotes"])
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
            menu_lotes(datos)
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