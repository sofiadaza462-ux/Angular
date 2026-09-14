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
# PERSISTENCIA Y CARGA DE DATOS (JSON) - RF16
# ==============================================================================
def cargar_datos_json(ruta):
    """Carga datos desde un archivo JSON. Retorna lista vacía si no existe o falla."""
    if not os.path.exists(ruta):
        return []
    try:
        with open(ruta, "r", encoding="utf-8") as archivo:
            return json.load(archivo)
    except (json.JSONDecodeError, OSError):
        print(f"No se pudo leer el archivo {ruta}. Se iniciará vacio.")
        return []


def guardar_datos_json(ruta, datos):
    """Guarda una colección en su correspondiente archivo JSON."""
    os.makedirs(os.path.dirname(ruta), exist_ok=True)
    try:
        with open(ruta, "w", encoding="utf-8") as archivo:
            json.dump(datos, archivo, indent=4, ensure_ascii=False)
        return True
    except OSError as e:
        print(f"Error al guardar la información: {e}")
        return False


def guardar_todo(datos):
    """Guarda todas las colecciones en sus respectivos archivos JSON."""
    for clave, ruta in RUTAS_ARCHIVOS.items():
        guardar_datos_json(ruta, datos[clave])
    print("\nInformación guardada correctamente.")


# ==============================================================================
# VALIDACIONES DE ENTRADA Y FORMATOS
# ==============================================================================
def leer_texto(mensaje):
    """Solicita un texto no vacío."""
    while True:
        valor = input(mensaje).strip()
        if valor:
            return valor
        print("El campo no puede estar vacío. Intente nuevamente.")


def leer_entero_positivo(mensaje):
    """Solicita un entero estricto mayor a cero."""
    while True:
        valor = input(mensaje).strip()
        try:
            num = int(valor)
            if num > 0:
                return num
            print("Debe ingresar un número mayor a cero.")
        except ValueError:
            print("Ingrese un número válido.")


def leer_entero_no_negativo(mensaje):
    """Solicita un entero estricto mayor o igual a cero."""
    while True:
        valor = input(mensaje).strip()
        try:
            num = int(valor)
            if num >= 0:
                return num
            print("El número no puede ser negativo.")
        except ValueError:
            print("Ingrese un número válido.")


def leer_numero_positivo(mensaje):
    """Solicita un número positivo."""
    while True:
        valor = input(mensaje).strip()
        try:
            num = float(valor)
            if num > 0:
                return num
            print("Debe ingresar un número mayor a cero.")
        except ValueError:
            print("Por favor ingrese un número válido.")


def leer_fecha_ddmmyyyy(mensaje):
    """Solicita una fecha con el formato dd/mm/aaaa."""
    while True:
        fecha_str = input(mensaje).strip()
        try:
            fecha_dt = datetime.strptime(fecha_str, "%d/%m/%Y")
            return fecha_dt.strftime("%d/%m/%Y")
        except ValueError:
            print("La fecha debe ingresarse en formato día/mes/año (ejemplo: 25/12/2026).")


def generar_id_secuencial(coleccion, prefijo, campo_id):
    """Genera identificadores secuenciales."""
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
# CÁLCULO DE STOCK
# ==============================================================================
def calcular_stock_producto(movimientos, codigo_producto):
    """Calcula la cantidad disponible actual."""
    codigo_upper = codigo_producto.upper()
    entradas = sum(m["cantidad"] for m in movimientos if m["producto_codigo"].upper() == codigo_upper and m["tipo"] == "ENTRADA")
    salidas = sum(m["cantidad"] for m in movimientos if m["producto_codigo"].upper() == codigo_upper and m["tipo"] == "SALIDA")
    return entradas - salidas


# ==============================================================================
# MÓDULO: GESTIÓN DE PRODUCTOS
# ==============================================================================
def buscar_producto_por_codigo(productos, codigo):
    """Busca un producto por su código."""
    codigo_upper = codigo.upper()
    for prod in productos:
        if prod["codigo"].upper() == codigo_upper:
            return prod
    return None


def registrar_producto(productos):
    """RF01: Registrar un nuevo producto."""
    print("\n--- Registrar Nuevo Producto ---")
    
    while True:
        codigo = leer_texto("Código del producto: ").upper()
        if buscar_producto_por_codigo(productos, codigo):
            print(f"El código '{codigo}' ya existe. Intente con otro.")
        else:
            break

    nombre = leer_texto("Nombre del producto: ")
    categoria = leer_texto("Categoría: ")
    unidad = leer_texto("Unidad de medida (ejemplo: kilo, unidad, bolsa): ")
    precio = leer_entero_positivo("Precio de venta: ")
    stock_minimo = leer_entero_no_negativo("Cantidad mínima permitida en inventario: ")

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
    print(f"\nProducto '{nombre}' ({codigo}) guardado correctamente.")


def listar_productos(datos):
    """RF02: Consultar lista de productos."""
    productos = datos["productos"]
    movimientos = datos["movimientos"]

    if not productos:
        print("\nNo hay productos registrados.")
        return

    print("\n--- Opciones de Consulta ---")
    print("1. Ver solo productos activos")
    print("2. Buscar producto por código o nombre")
    print("3. Ver todos los productos")
    opcion = input("Elija una opción: ").strip()

    filtro = ""
    solo_activos = True

    if opcion == "2":
        filtro = input("Ingrese texto a buscar: ").strip().lower()
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
        print("\nNo se encontraron productos.")
        return

    print("\n" + "="*95)
    print(f"{'CÓDIGO':<8} | {'NOMBRE':<20} | {'CATEGORÍA':<13} | {'PRECIO':<10} | {'STOCK ACT.':<10} | {'MÍN.':<6} | {'ESTADO'}")
    print("="*95)
    for p in resultados:
        estado = "Activo" if p.get("activo", True) else "Inactivo"
        precio_fmt = f"${p['precio']:,}".replace(",", ".")
        stock_actual = calcular_stock_producto(movimientos, p["codigo"])
        stock_act_fmt = f"{stock_actual:,}".replace(",", ".")
        stock_min_fmt = f"{p['stock_minimo']:,}".replace(",", ".")
        print(f"{p['codigo']:<8} | {p['nombre']:<20} | {p['categoria']:<13} | {precio_fmt:<10} | {stock_act_fmt:<10} | {stock_min_fmt:<6} | {estado}")
    print("="*95)


def actualizar_producto(productos):
    """RF03: Actualizar datos de un producto."""
    print("\n--- Actualizar Producto ---")
    codigo = input("Código del producto a modificar: ").strip().upper()
    producto = buscar_producto_por_codigo(productos, codigo)

    if not producto:
        print(f"No se encontró el producto con el código '{codigo}'.")
        return

    print(f"\nModificando: [{producto['codigo']}] {producto['nombre']}")
    print("(Deje la opción vacía y presione ENTER para mantener el dato actual)\n")

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
                print("El precio debe ser un número positivo.")
        except ValueError:
            print("Número inválido.")

    nuevo_stock_min = input(f"Cantidad mínima actual [{producto['stock_minimo']:,}]: ").strip().replace(".", "")
    if nuevo_stock_min:
        try:
            val = int(nuevo_stock_min)
            if val >= 0:
                producto["stock_minimo"] = val
            else:
                print("La cantidad mínima no puede ser negativa.")
        except ValueError:
            print("Número inválido.")

    guardar_datos_json(RUTAS_ARCHIVOS["productos"], productos)
    print(f"\nProducto '{codigo}' actualizado correctamente.")


def desactivar_producto(productos):
    """RF04: Desactivar producto."""
    print("\n--- Desactivar Producto ---")
    codigo = input("Código del producto a desactivar: ").strip().upper()
    producto = buscar_producto_por_codigo(productos, codigo)

    if not producto:
        print(f"No existe el producto con el código '{codigo}'.")
        return

    if not producto.get("activo", True):
        print(f"El producto '{codigo}' ya está desactivado.")
        return

    confirmar = input(f"¿Inactivar el producto '{producto['nombre']}'? (s/n): ").strip().lower()
    if confirmar == 's':
        producto["activo"] = False
        guardar_datos_json(RUTAS_ARCHIVOS["productos"], productos)
        print(f"\nProducto '{codigo}' desactivado correctamente.")
    else:
        print("\nOperación cancelada.")


def menu_productos(datos):
    """Submenú de productos."""
    while True:
        print("\n----- MÓDULO DE PRODUCTOS -----")
        print("1. Registrar producto")
        print("2. Consultar productos")
        print("3. Actualizar producto")
        print("4. Desactivar producto")
        print("0. Volver al menú principal")
        opcion = input("Elija una opción: ").strip()

        if opcion == "1":
            registrar_producto(datos["productos"])
        elif opcion == "2":
            listar_productos(datos)
        elif opcion == "3":
            actualizar_producto(datos["productos"])
        elif opcion == "4":
            desactivar_producto(datos["productos"])
        elif opcion == "0":
            break
        else:
            print("Opción no válida.")


# ==============================================================================
# MÓDULO: GESTIÓN DE LOTES PRODUCTIVOS
# ==============================================================================
def buscar_lote_por_id(lotes, id_lote):
    """Busca un lote por ID."""
    id_upper = id_lote.upper()
    for lote in lotes:
        if lote["id_lote"].upper() == id_upper:
            return lote
    return None


def registrar_lote(datos):
    """RF05: Registrar lote."""
    print("\n--- Registrar Lote Productivo ---")
    
    codigo_prod = leer_texto("Código del producto a sembrar: ").upper()
    prod = buscar_producto_por_codigo(datos["productos"], codigo_prod)

    if not prod:
        print(f"El producto '{codigo_prod}' no existe.")
        return

    if not prod.get("activo", True):
        print(f"El producto '{prod['nombre']}' está desactivado. No se pueden registrar nuevos lotes.")
        return

    id_lote = generar_id_secuencial(datos["lotes"], "L", "id_lote")
    print(f"Número de lote asignado: {id_lote}")

    fecha_siembra = leer_fecha_ddmmyyyy("Fecha de siembra (día/mes/año): ")
    area_m2 = leer_numero_positivo("Tamaño del terreno en metros cuadrados: ")

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
    print(f"\nLote '{id_lote}' para el producto '{prod['nombre']}' guardado correctamente.")


def cosechar_lote(datos):
    """RF07: Cosechar lote."""
    print("\n--- Cosechar Lote ---")
    id_lote = input("Número del lote a cosechar: ").strip().upper()
    lote = buscar_lote_por_id(datos["lotes"], id_lote)

    if not lote:
        print(f"El lote '{id_lote}' no existe.")
        return

    if lote["estado"] == "COSECHADO":
        print(f"El lote '{id_lote}' ya fue cosechado previamente.")
        return

    if lote["estado"] == "CANCELADO":
        print(f"El lote '{id_lote}' está cancelado y no se puede cosechar.")
        return

    cantidad = leer_entero_positivo("Cantidad recolectada: ")
    fecha_cosecha = datetime.now().strftime("%d/%m/%Y %H:%M")

    lote["cantidad_producida"] = cantidad
    lote["estado"] = "COSECHADO"

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
    
    print(f"\nLote '{id_lote}' cosechado correctamente.")
    print(f"Se sumaron {cantidad:,} unidades al inventario.")


def cambiar_estado_lote(lotes):
    """RF06: Cambiar estado del lote."""
    print("\n--- Cambiar Estado de Lote ---")
    id_lote = input("Número del lote: ").strip().upper()
    lote = buscar_lote_por_id(lotes, id_lote)

    if not lote:
        print(f"El lote '{id_lote}' no existe.")
        return

    print(f"Estado actual: {lote['estado']}")
    if lote["estado"] == "COSECHADO":
        print("Los lotes cosechados no pueden cambiar de estado.")
        return

    print("Estados disponibles: [1] En producción  [2] Cancelado")
    opc = input("Elija la opción: ").strip()

    if opc == "1":
        lote["estado"] = "EN_PRODUCCION"
    elif opc == "2":
        lote["estado"] = "CANCELADO"
    else:
        print("Opción no válida.")
        return

    guardar_datos_json(RUTAS_ARCHIVOS["lotes"], lotes)
    print(f"\nEstado del lote '{id_lote}' modificado a '{lote['estado']}'.")


def listar_lotes(lotes):
    """Listar lotes."""
    if not lotes:
        print("\nNo hay lotes registrados.")
        return

    print("\n" + "="*75)
    print(f"{'N° LOTE':<8} | {'PROD. CÓD':<10} | {'FECHA SIEMBRA':<14} | {'ÁREA (m²)':<10} | {'CANT.':<8} | {'ESTADO'}")
    print("="*75)
    for l in lotes:
        cant_fmt = f"{l['cantidad_producida']:,}".replace(",", ".")
        area_fmt = f"{l['area_m2']:,.1f}"
        print(f"{l['id_lote']:<8} | {l['producto_codigo']:<10} | {l['fecha_siembra']:<14} | {area_fmt:<10} | {cant_fmt:<8} | {l['estado']}")
    print("="*75)


def menu_lotes(datos):
    """Submenú de lotes."""
    while True:
        print("\n----- MÓDULO DE LOTES PRODUCTIVOS -----")
        print("1. Registrar lote")
        print("2. Cosechar lote")
        print("3. Cambiar estado de lote")
        print("4. Ver lista de lotes")
        print("0. Volver al menú principal")
        opcion = input("Elija una opción: ").strip()

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
            print("Opción no válida.")


# ==============================================================================
# MÓDULO: MOVIMIENTOS DE INVENTARIO
# ==============================================================================
def registrar_entrada_inventario(datos):
    """RF08: Ingresar mercancía."""
    print("\n--- Registrar Entrada de Mercancía ---")
    codigo_prod = leer_texto("Código del producto: ").upper()
    prod = buscar_producto_por_codigo(datos["productos"], codigo_prod)

    if not prod:
        print(f"El producto '{codigo_prod}' no existe.")
        return

    if not prod.get("activo", True):
        print(f"El producto '{prod['nombre']}' está inactivo.")
        return

    cantidad = leer_entero_positivo("Cantidad a ingresar: ")
    motivo = leer_texto("Motivo o razón del ingreso: ")
    fecha_mov = datetime.now().strftime("%d/%m/%Y %H:%M")

    id_mov = generar_id_secuencial(datos["movimientos"], "M", "id")

    nuevo_movimiento = {
        "id": id_mov,
        "producto_codigo": codigo_prod,
        "tipo": "ENTRADA",
        "cantidad": cantidad,
        "motivo": motivo,
        "fecha": fecha_mov
    }

    datos["movimientos"].append(nuevo_movimiento)
    guardar_datos_json(RUTAS_ARCHIVOS["movimientos"], datos["movimientos"])
    print(f"\nEntrada registrada correctamente para '{prod['nombre']}'.")


def registrar_salida_inventario(datos):
    """RF09: Retirar mercancía."""
    print("\n--- Registrar Salida de Mercancía ---")
    codigo_prod = leer_texto("Código del producto: ").upper()
    prod = buscar_producto_por_codigo(datos["productos"], codigo_prod)

    if not prod:
        print(f"El producto '{codigo_prod}' no existe.")
        return

    stock_disponible = calcular_stock_producto(datos["movimientos"], codigo_prod)
    print(f"Cantidad disponible actualmente para '{prod['nombre']}': {stock_disponible:,}")

    cantidad = leer_entero_positivo("Cantidad a retirar: ")

    if cantidad > stock_disponible:
        print(f"No hay suficiente cantidad disponible ({stock_disponible:,}) para retirar {cantidad:,} unidades.")
        return

    motivo = leer_texto("Motivo o razón del retiro: ")
    fecha_mov = datetime.now().strftime("%d/%m/%Y %H:%M")

    id_mov = generar_id_secuencial(datos["movimientos"], "M", "id")

    nuevo_movimiento = {
        "id": id_mov,
        "producto_codigo": codigo_prod,
        "tipo": "SALIDA",
        "cantidad": cantidad,
        "motivo": motivo,
        "fecha": fecha_mov
    }

    datos["movimientos"].append(nuevo_movimiento)
    guardar_datos_json(RUTAS_ARCHIVOS["movimientos"], datos["movimientos"])
    print(f"\nSalida registrada correctamente. Nueva cantidad disponible: {stock_disponible - cantidad:,}.")


def listar_movimientos(movimientos):
    """Ver historial."""
    if not movimientos:
        print("\nNo existen registros de movimientos.")
        return

    print("\n" + "="*85)
    print(f"{'ID':<7} | {'PROD. CÓD':<10} | {'TIPO':<8} | {'CANTIDAD':<10} | {'FECHA':<16} | {'MOTIVO'}")
    print("="*85)
    for m in movimientos:
        cant_fmt = f"{m['cantidad']:,}".replace(",", ".")
        print(f"{m['id']:<7} | {m['producto_codigo']:<10} | {m['tipo']:<8} | {cant_fmt:<10} | {m['fecha']:<16} | {m['motivo']}")
    print("="*85)


def menu_inventario(datos):
    """Submenú inventario."""
    while True:
        print("\n----- MÓDULO DE MOVIMIENTOS DE INVENTARIO -----")
        print("1. Registrar ingreso manual de mercancía")
        print("2. Registrar retiro manual de mercancía")
        print("3. Ver historial de movimientos")
        print("0. Volver al menú principal")
        opcion = input("Elija una opción: ").strip()

        if opcion == "1":
            registrar_entrada_inventario(datos)
        elif opcion == "2":
            registrar_salida_inventario(datos)
        elif opcion == "3":
            listar_movimientos(datos["movimientos"])
        elif opcion == "0":
            break
        else:
            print("Opción no válida.")


# ==============================================================================
# MÓDULO: REGISTRO Y CONSULTA DE VENTAS
# ==============================================================================
def registrar_venta(datos):
    """RF10 y RF11: Registrar ventas."""
    print("\n--- Registrar Venta ---")
    cliente = leer_texto("Nombre del cliente: ")

    items_venta = []
    total_venta = 0

    while True:
        codigo_prod = leer_texto("Código del producto (o escriba 'FIN' para terminar la venta): ").upper()
        if codigo_prod == "FIN":
            if not items_venta:
                print("No agregó productos. Venta cancelada.")
                return
            break

        prod = buscar_producto_por_codigo(datos["productos"], codigo_prod)
        if not prod:
            print(f"El producto con código '{codigo_prod}' no existe.")
            continue

        if not prod.get("activo", True):
            print(f"El producto '{prod['nombre']}' ({codigo_prod}) está desactivado.")
            continue

        stock_disponible = calcular_stock_producto(datos["movimientos"], codigo_prod)
        ya_agregado = sum(item["cantidad"] for item in items_venta if item["producto_codigo"] == codigo_prod)
        stock_efectivo = stock_disponible - ya_agregado

        print(f"Producto: {prod['nombre']} | Precio: ${prod['precio']:,} | Disponible: {stock_efectivo:,}")

        if stock_efectivo <= 0:
            print(f"No hay unidades disponibles de '{prod['nombre']}'.")
            continue

        cantidad = leer_entero_positivo("Cantidad a vender: ")

        if cantidad > stock_efectivo:
            print(f"Cantidad insuficiente. Solo hay {stock_efectivo:,} unidades disponibles.")
            continue

        subtotal = cantidad * prod["precio"]
        total_venta += subtotal

        items_venta.append({
            "producto_codigo": codigo_prod,
            "nombre": prod["nombre"],
            "cantidad": cantidad,
            "precio_unitario": prod["precio"],
            "subtotal": subtotal
        })

        print(f"Agregado: {cantidad} x {prod['nombre']} - Valor: ${subtotal:,}")

    id_venta = generar_id_secuencial(datos["ventas"], "V", "id_venta")
    fecha_venta = datetime.now().strftime("%d/%m/%Y %H:%M")

    nueva_venta = {
        "id_venta": id_venta,
        "cliente": cliente,
        "fecha": fecha_venta,
        "items": items_venta,
        "total": total_venta
    }

    datos["ventas"].append(nueva_venta)

    for item in items_venta:
        id_mov = generar_id_secuencial(datos["movimientos"], "M", "id")
        nuevo_movimiento = {
            "id": id_mov,
            "producto_codigo": item["producto_codigo"],
            "tipo": "SALIDA",
            "cantidad": item["cantidad"],
            "motivo": f"Venta {id_venta}",
            "fecha": fecha_venta
        }
        datos["movimientos"].append(nuevo_movimiento)

    guardar_datos_json(RUTAS_ARCHIVOS["ventas"], datos["ventas"])
    guardar_datos_json(RUTAS_ARCHIVOS["movimientos"], datos["movimientos"])

    print(f"\nVenta {id_venta} realizada con éxito a {cliente}.")
    print(f"Total pagado: ${total_venta:,}")


def consultar_ventas(ventas):
    """Consultar lista de ventas."""
    if not ventas:
        print("\nNo hay ventas registradas.")
        return

    print("\n" + "="*70)
    print(f"{'RECIBO':<8} | {'FECHA':<16} | {'CLIENTE':<25} | {'TOTAL'}")
    print("="*70)
    for v in ventas:
        total_fmt = f"${v['total']:,}".replace(",", ".")
        print(f"{v['id_venta']:<8} | {v['fecha']:<16} | {v['cliente']:<25} | {total_fmt}")
    print("="*70)


# ==============================================================================
# MÓDULO: ALERTAS DE STOCK (RF12)
# ==============================================================================
def consultar_alertas_stock(datos):
    """Muestra alertas cuando el stock es menor o igual al stock mínimo."""
    productos = datos["productos"]
    movimientos = datos["movimientos"]

    if not productos:
        print("\nNo hay productos registrados.")
        return

    alertas = []
    for p in productos:
        if not p.get("activo", True):
            continue
        stock_actual = calcular_stock_producto(movimientos, p["codigo"])
        if stock_actual <= p["stock_minimo"]:
            alertas.append({
                "codigo": p["codigo"],
                "nombre": p["nombre"],
                "stock_actual": stock_actual,
                "stock_minimo": p["stock_minimo"]
            })

    print("\n--- ALERTAS DE STOCK MÍNIMO ---")
    if not alertas:
        print("Todos los productos tienen una cantidad adecuada en inventario.")
        return

    print("ATENCIÓN: Los siguientes productos están en cantidad mínima o agotados:\n")
    print("="*70)
    print(f"{'CÓDIGO':<8} | {'NOMBRE':<25} | {'DISPONIBLE':<12} | {'MÍNIMO'}")
    print("="*70)
    for a in alertas:
        actual_fmt = f"{a['stock_actual']:,}".replace(",", ".")
        min_fmt = f"{a['stock_minimo']:,}".replace(",", ".")
        print(f"{a['codigo']:<8} | {a['nombre']:<25} | {actual_fmt:<12} | {min_fmt}")
    print("="*70)


# ==============================================================================
# MÓDULO: REPORTES (RF13, RF14, RF15)
# ==============================================================================
def reporte_existencias_y_valor(datos):
    """RF13: Reporte de existencias y valor del inventario a precio de venta."""
    productos = datos["productos"]
    movimientos = datos["movimientos"]

    print("\n--- REPORTE DE EXISTENCIAS Y VALOR DEL INVENTARIO ---")
    if not productos:
        print("No hay productos registrados.")
        return

    total_unidades = 0
    valor_total_inventario = 0

    print("="*80)
    print(f"{'CÓDIGO':<8} | {'NOMBRE':<20} | {'CANTIDAD':<10} | {'PRECIO UNIT.':<12} | {'VALOR TOTAL'}")
    print("="*80)

    for p in productos:
        if not p.get("activo", True):
            continue
        stock_actual = calcular_stock_producto(movimientos, p["codigo"])
        valor_producto = stock_actual * p["precio"]
        
        total_unidades += stock_actual
        valor_total_inventario += valor_producto

        precio_fmt = f"${p['precio']:,}".replace(",", ".")
        valor_fmt = f"${valor_producto:,}".replace(",", ".")
        stock_fmt = f"{stock_actual:,}".replace(",", ".")

        print(f"{p['codigo']:<8} | {p['nombre']:<20} | {stock_fmt:<10} | {precio_fmt:<12} | {valor_fmt}")

    print("="*80)
    print(f"Total de unidades disponibles: {total_unidades:,}".replace(",", "."))
    print(f"Valor total del inventario: ${valor_total_inventario:,}".replace(",", "."))


def reporte_ventas_acumuladas(ventas):
    """RF14: Reporte de ventas (número de ventas, unidades vendidas e ingresos)."""
    print("\n--- REPORTE GENERAL DE VENTAS ---")
    if not ventas:
        print("No se han registrado ventas hasta el momento.")
        return

    num_ventas = len(ventas)
    unidades_vendidas = sum(sum(item["cantidad"] for item in v["items"]) for v in ventas)
    ingresos_totales = sum(v["total"] for v in ventas)

    print(f"Número total de ventas realizadas: {num_ventas}")
    print(f"Total de unidades vendidas: {unidades_vendidas:,}".replace(",", "."))
    print(f"Ingresos totales acumulados: ${ingresos_totales:,}".replace(",", "."))


def reporte_ranking_mas_vendidos(ventas):
    """RF15: Ranking de los 3 productos más vendidos."""
    print("\n--- TOP 3 PRODUCTOS MÁS VENDIDOS ---")
    if not ventas:
        print("No hay ventas registradas para generar el ranking.")
        return

    conteo_productos = {}
    for v in ventas:
        for item in v["items"]:
            codigo = item["producto_codigo"]
            nombre = item["nombre"]
            cant = item["cantidad"]
            
            if codigo in conteo_productos:
                conteo_productos[codigo]["cantidad"] += cant
            else:
                conteo_productos[codigo] = {"nombre": nombre, "cantidad": cant}

    # Ordenar por cantidad vendida de mayor a menor
    ranking = sorted(conteo_productos.items(), key=lambda x: x[1]["cantidad"], reverse=True)[:3]

    print("="*60)
    print(f"{'POSICIÓN':<10} | {'CÓDIGO':<8} | {'NOMBRE':<25} | {'VENDIDOS'}")
    print("="*60)
    for pos, (codigo, info) in enumerate(ranking, 1):
        cant_fmt = f"{info['cantidad']:,}".replace(",", ".")
        print(f"{pos:<10} | {codigo:<8} | {info['nombre']:<25} | {cant_fmt}")
    print("="*60)


def menu_reportes(datos):
    """Submenú de reportes."""
    while True:
        print("\n----- MÓDULO DE REPORTES -----")
        print("1. Ver valor total del inventario ")
        print("2. Ver total acumulado de ventas ")
        print("3. Ver los 3 productos más vendidos")
        print("0. Volver al menú principal")
        opcion = input("Elija una opción: ").strip()

        if opcion == "1":
            reporte_existencias_y_valor(datos)
        elif opcion == "2":
            reporte_ventas_acumuladas(datos["ventas"])
        elif opcion == "3":
            reporte_ranking_mas_vendidos(datos["ventas"])
        elif opcion == "0":
            break
        else:
            print("Opción no válida.")


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
    print("6. Alertas de stock mínimo")
    print("7. Reportes de negocio")
    print("8. Guardar información")
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
        opcion = input("Elija una opción: ").strip()

        if opcion == "1":
            menu_productos(datos)
        elif opcion == "2":
            menu_lotes(datos)
        elif opcion == "3":
            menu_inventario(datos)
        elif opcion == "4":
            registrar_venta(datos)
        elif opcion == "5":
            consultar_ventas(datos["ventas"])
        elif opcion == "6":
            consultar_alertas_stock(datos)
        elif opcion == "7":
            menu_reportes(datos)
        elif opcion == "8":
            guardar_todo(datos)
        elif opcion == "0":
            guardar_todo(datos)
            print("\nSaliendo del sistema AgroControl CBA. Hasta luego.")
            mantenimiento = False
        else:
            print("\nOpción no válida. Intente nuevamente.")


if __name__ == "__main__":
    main()