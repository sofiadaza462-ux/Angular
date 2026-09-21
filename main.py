from datetime import datetime
import json
import os
import csv
import shutil
from getpass import getpass

# Carpeta donde está main.py
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Archivos donde se guarda la información
RUTAS_ARCHIVOS = {
    "productos": os.path.join(BASE_DIR, "data", "productos.json"),
    "lotes": os.path.join(BASE_DIR, "data", "lotes.json"),
    "movimientos": os.path.join(BASE_DIR, "data", "movimientos.json"),
    "ventas": os.path.join(BASE_DIR, "data", "ventas.json"),
    "usuarios": os.path.join(BASE_DIR, "data", "usuarios.json"),
}

# Lee la información guardada
def cargar_datos_json(ruta):
    if not os.path.exists(ruta):
        return []
    try:
        with open(ruta, "r", encoding="utf-8") as archivo:
            return json.load(archivo)
    except (json.JSONDecodeError, OSError):
        print(f"Advertencia: No se pudo leer {ruta}. Se iniciará con lista vacía.")
        return []


# Guarda la información
def guardar_datos_json(ruta, datos):
    try:
        with open(ruta, "w", encoding="utf-8") as archivo:
            json.dump(datos, archivo, indent=4, ensure_ascii=False)
        return True
    except OSError as e:
        print(f"Error al guardar en {ruta}: {e}")
        return False


# Guarda todos los datos
def guardar_todo(datos):
    for clave, ruta in RUTAS_ARCHIVOS.items():
        if clave != "usuarios":
            guardar_datos_json(ruta, datos[clave])
    print("\n Todos los datos han sido guardados exitosamente en data/")


# Pide un texto
def leer_texto(mensaje):
    while True:
        valor = input(mensaje).strip()
        if valor:
            return valor
        print("Error: El campo no puede estar vacío. Intente de nuevo.")


# Pide un número entero positivo
def leer_entero_positivo(mensaje):
    while True:
        valor = input(mensaje).strip()
        try:
            num = int(valor)
            if num > 0:
                return num
            print("Error: Debe ingresar un valor.")
        except ValueError:
            print("Error: Ingrese un valor entero válido .")


# Pide un número entero que puede ser cero
def leer_entero_no_negativo(mensaje):
    while True:
        valor = input(mensaje).strip()
        try:
            num = int(valor)
            if num >= 0:
                return num
            print("Error: El valor no puede ser negativo.")
        except ValueError:
            print("Error: Ingrese un valor.")


# Pide un número decimal positivo
def leer_numero_positivo(mensaje):
    while True:
        valor = input(mensaje).strip()
        try:
            num = float(valor)
            if num > 0:
                return num
            print("Error: Debe ingresar un valor mayor a 0.")
        except ValueError:
            print("Error: Por favor ingrese un número válido.")


# Valida una fecha
def leer_fecha_ddmmyyyy(mensaje):
    while True:
        fecha_str = input(mensaje).strip()
        try:
            fecha_dt = datetime.strptime(fecha_str, "%d/%m/%Y")
            return fecha_dt.strftime("%d/%m/%Y")
        except ValueError:
            print("Error: La fecha debe tener el formato dd/mm/aaaa.")


# Crea códigos consecutivos
def generar_id_secuencial(coleccion, prefijo, campo_id):
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


# Calcula el stock
def calcular_stock_producto(movimientos, codigo_producto):
    codigo_upper = codigo_producto.upper()

    entradas = sum(
        m["cantidad"]
        for m in movimientos
        if m["producto_codigo"].upper() == codigo_upper
        and m["tipo"] == "ENTRADA"
    )

    salidas = sum(
        m["cantidad"]
        for m in movimientos
        if m["producto_codigo"].upper() == codigo_upper
        and m["tipo"] == "SALIDA"
    )

    return entradas - salidas


# Busca un producto
def buscar_producto_por_codigo(productos, codigo):
    codigo_upper = codigo.upper()

    for prod in productos:
        if prod["codigo"].upper() == codigo_upper:
            return prod

    return None


# Busca un usuario
def buscar_usuario(usuarios, usuario):
    for u in usuarios:
        if u.get("usuario", "").lower() == usuario.lower():
            return u

    return None


# Inicia sesión
def iniciar_sesion(usuarios):
    print("\n==================== INICIO DE SESIÓN ====================")

    for intento in range(3):
        usuario = input("Usuario: ").strip()
        contrasena = getpass("Contraseña: ")

        datos_usuario = buscar_usuario(usuarios, usuario)

        if datos_usuario and datos_usuario.get("contrasena") == contrasena:

            if not datos_usuario.get("activo", True):
                print("Error: El usuario se encuentra inactivo.")
                return None

            print(f"\nBienvenido, {usuario}.")
            print(f"Rol: {datos_usuario.get('rol', 'OPERADOR')}")

            return datos_usuario

        print("Error: Usuario o contraseña incorrectos.")

    print("Error: Se superó el número máximo de intentos.")
    return None


# Registra un producto
def registrar_producto(productos):
    print("\nRegistrar Nuevo Producto ")

    while True:
        codigo = leer_texto("Ingrese el código del producto (ej. P001): ").upper()

        if buscar_producto_por_codigo(productos, codigo):
            print(f"Error: El código '{codigo}' ya está registrado. Intente con otro.")
        else:
            break

    nombre = leer_texto("Ingrese el nombre del producto: ")
    categoria = leer_texto("Ingrese la categoría: ")
    unidad = leer_texto("Ingrese la unidad de medida: ")
    precio = leer_entero_positivo("Ingrese el precio unitario: ")
    stock_minimo = leer_entero_no_negativo("Ingrese el stock mínimo: ")

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

    guardar_datos_json(
        RUTAS_ARCHIVOS["productos"],
        productos
    )

    print(f"\n Producto '{nombre}' ({codigo}) registrado correctamente.")


# Lista los productos
def listar_productos(datos):
    productos = datos["productos"]
    movimientos = datos["movimientos"]

    if not productos:
        print("\nNo hay productos registrados en el sistema.")
        return

    print("\n Opciones de Consulta")
    print("1. Ver todos los productos activos")
    print("2. Buscar producto por código o nombre")
    print("3. Ver todos los productos (incluye inactivos)")

    opcion = input("Seleccione una opción: ").strip()

    filtro = ""
    solo_activos = True

    if opcion == "2":
        filtro = input(
            "Ingrese texto a buscar código o parte del nombre: "
        ).strip().lower()

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

    print("\n" + "=" * 95)

    print(
        f"{'CÓDIGO':<8} | {'NOMBRE':<20} | {'CATEGORÍA':<13} | "
        f"{'PRECIO':<10} | {'STOCK ACT.':<10} | {'MÍN.':<6} | {'ESTADO'}"
    )

    print("=" * 95)

    for p in resultados:

        estado = "Activo" if p.get("activo", True) else "Inactivo"

        precio_fmt = f"${p['precio']:,}".replace(",", ".")

        stock_actual = calcular_stock_producto(
            movimientos,
            p["codigo"]
        )

        stock_act_fmt = f"{stock_actual:,}".replace(",", ".")
        stock_min_fmt = f"{p['stock_minimo']:,}".replace(",", ".")

        print(
            f"{p['codigo']:<8} | {p['nombre']:<20} | "
            f"{p['categoria']:<13} | {precio_fmt:<10} | "
            f"{stock_act_fmt:<10} | {stock_min_fmt:<6} | {estado}"
        )

    print("=" * 95)


# Actualiza un producto
def actualizar_producto(productos):
    print("\n Actualizar Producto")

    codigo = input(
        "Ingrese el código del producto a actualizar: "
    ).strip().upper()

    producto = buscar_producto_por_codigo(productos, codigo)

    if not producto:
        print(
            f"Error: No se encontró ningún producto con el código '{codigo}'."
        )
        return

    print(
        f"\nActualizando información para "
        f"[{producto['codigo']}] {producto['nombre']}"
    )

    print(
        "(Presione ENTER sin escribir nada para conservar el valor actual)\n"
    )

    nuevo_nombre = input(
        f"Nombre actual [{producto['nombre']}]: "
    ).strip()

    if nuevo_nombre:
        producto["nombre"] = nuevo_nombre

    nueva_cat = input(
        f"Categoría actual [{producto['categoria']}]: "
    ).strip()

    if nueva_cat:
        producto["categoria"] = nueva_cat

    nueva_unidad = input(
        f"Unidad actual [{producto['unidad']}]: "
    ).strip()

    if nueva_unidad:
        producto["unidad"] = nueva_unidad

    nuevo_precio = input(
        f"Precio actual [${producto['precio']:,}]: "
    ).strip().replace(".", "")

    if nuevo_precio:

        try:
            val = int(nuevo_precio)

            if val > 0:
                producto["precio"] = val
            else:
                print("Precio inválido.")

        except ValueError:
            print("Entrada inválida.")

    nuevo_stock_min = input(
        f"Stock mínimo actual [{producto['stock_minimo']:,}]: "
    ).strip().replace(".", "")

    if nuevo_stock_min:

        try:
            val = int(nuevo_stock_min)

            if val >= 0:
                producto["stock_minimo"] = val
            else:
                print("Stock mínimo inválido.")

        except ValueError:
            print("Entrada inválida.")

    guardar_datos_json(
        RUTAS_ARCHIVOS["productos"],
        productos
    )

    print(f"\n Producto '{codigo}' actualizado exitosamente.")


# Desactiva un producto
def desactivar_producto(productos):
    print("\n Desactivar Producto ")

    codigo = input(
        "Ingrese el código del producto a desactivar: "
    ).strip().upper()

    producto = buscar_producto_por_codigo(productos, codigo)

    if not producto:
        print(
            f"Error: No existe un producto con el código '{codigo}'."
        )
        return

    if not producto.get("activo", True):
        print(
            f"El producto '{codigo}' ya se encuentra desactivado."
        )
        return

    confirmar = input(
        f"¿Desea desactivar el producto "
        f"'{producto['nombre']}'? (s/n): "
    ).strip().lower()

    if confirmar == "s":

        producto["activo"] = False

        guardar_datos_json(
            RUTAS_ARCHIVOS["productos"],
            productos
        )

        print(
            f"\n Producto '{codigo}' desactivado correctamente."
        )

    else:
        print("\nOperación cancelada.")


# Menú de productos
def menu_productos(datos):
    while True:

        print("\nMÓDULO DE PRODUCTOS")
        print("1. Registrar producto")
        print("2. Consultar / Listar productos")
        print("3. Actualizar producto")
        print("4. Desactivar producto")
        print("0. Volver al menú principal")

        opcion = input(
            "Seleccione una opción: "
        ).strip()

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
            print("Opción inválida. Intente de nuevo.")


# Busca un lote
def buscar_lote_por_id(lotes, id_lote):
    id_upper = id_lote.upper()

    for lote in lotes:

        if lote["id_lote"].upper() == id_upper:
            return lote

    return None


# Registra un lote
def registrar_lote(datos):
    print("\n Registrar Lote Productivo ")

    codigo_prod = leer_texto(
        "Ingrese el código del producto asociado: "
    ).upper()

    prod = buscar_producto_por_codigo(
        datos["productos"],
        codigo_prod
    )

    if not prod:
        print(
            f"Error: El producto con código '{codigo_prod}' "
            f"no existe en el sistema."
        )
        return

    if not prod.get("activo", True):
        print(
            f"Error: El producto '{prod['nombre']}' ({codigo_prod}) "
            f"se encuentra DESACTIVADO. No se pueden registrar nuevos lotes."
        )
        return

    id_lote = generar_id_secuencial(
        datos["lotes"],
        "L",
        "id_lote"
    )

    print(f"ID asignado al lote: {id_lote}")

    fecha_siembra = leer_fecha_ddmmyyyy(
        "Ingrese la fecha de siembra (dd/mm/aaaa): "
    )

    area_m2 = leer_numero_positivo(
        "Ingrese el área en m²: "
    )

    nuevo_lote = {
        "id_lote": id_lote,
        "producto_codigo": codigo_prod,
        "fecha_siembra": fecha_siembra,
        "area_m2": area_m2,
        "cantidad_producida": 0,
        "estado": "EN_PRODUCCION"
    }

    datos["lotes"].append(nuevo_lote)

    guardar_datos_json(
        RUTAS_ARCHIVOS["lotes"],
        datos["lotes"]
    )

    print(
        f"\nLote '{id_lote}' para el producto activo "
        f"'{prod['nombre']}' registrado exitosamente."
    )


# Cosecha un lote
def cosechar_lote(datos):
    print("\n Cosechar Lote Productivo")

    id_lote = input(
        "Ingrese el ID del lote a cosechar (ej. L001): "
    ).strip().upper()

    lote = buscar_lote_por_id(
        datos["lotes"],
        id_lote
    )

    if not lote:
        print(
            f"Error (PF003): El lote '{id_lote}' no existe."
        )
        return

    if lote["estado"] == "COSECHADO":
        print(
            f"Error (PF004): El lote '{id_lote}' ya fue cosechado "
            f"previamente. No se permite doble cosecha."
        )
        return

    if lote["estado"] == "CANCELADO":
        print(
            f"Error: El lote '{id_lote}' está CANCELADO "
            f"y no se puede cosechar."
        )
        return

    cantidad = leer_entero_positivo(
        "Ingrese la cantidad producida cosechada: "
    )

    fecha_cosecha = datetime.now().strftime(
        "%d/%m/%Y %H:%M"
    )

    lote["cantidad_producida"] = cantidad
    lote["estado"] = "COSECHADO"

    id_mov = generar_id_secuencial(
        datos["movimientos"],
        "M",
        "id"
    )

    nuevo_movimiento = {
        "id": id_mov,
        "producto_codigo": lote["producto_codigo"],
        "tipo": "ENTRADA",
        "cantidad": cantidad,
        "motivo": f"Cosecha lote {id_lote}",
        "fecha": fecha_cosecha
    }

    datos["movimientos"].append(nuevo_movimiento)

    guardar_datos_json(
        RUTAS_ARCHIVOS["lotes"],
        datos["lotes"]
    )

    guardar_datos_json(
        RUTAS_ARCHIVOS["movimientos"],
        datos["movimientos"]
    )

    print(
        f"\n Lote '{id_lote}' cosechado exitosamente."
    )

    print(
        f" Se generó automáticamente la entrada de inventario "
        f"{id_mov} por {cantidad:,} unidades."
    )


# Cambia el estado de un lote
def cambiar_estado_lote(lotes):
    print("\n Cambiar Estado de Lote ")

    id_lote = input(
        "Ingrese el ID del lote: "
    ).strip().upper()

    lote = buscar_lote_por_id(
        lotes,
        id_lote
    )

    if not lote:
        print(
            f"Error: El lote '{id_lote}' no existe."
        )
        return

    print(
        f"Estado actual del lote '{id_lote}': "
        f"{lote['estado']}"
    )

    if lote["estado"] == "COSECHADO":
        print(
            "Atención: Un lote COSECHADO no se puede cambiar a otros estados."
        )
        return

    print(
        "Estados disponibles: [1] EN_PRODUCCION  [2] CANCELADO"
    )

    opc = input(
        "Seleccione nuevo estado: "
    ).strip()

    if opc == "1":
        lote["estado"] = "EN_PRODUCCION"

    elif opc == "2":
        lote["estado"] = "CANCELADO"

    else:
        print(
            "Opción inválida. Operación cancelada."
        )
        return

    guardar_datos_json(
        RUTAS_ARCHIVOS["lotes"],
        lotes
    )

    print(
        f"\n Estado del lote '{id_lote}' "
        f"cambiado a '{lote['estado']}'."
    )


# Lista los lotes
def listar_lotes(lotes):
    if not lotes:
        print("\nNo hay lotes registrados.")
        return

    print("\n" + "=" * 75)

    print(
        f"{'ID LOTE':<8} | {'PROD. CÓD':<10} | "
        f"{'FECHA SIEMBRA':<14} | {'ÁREA (m²)':<10} | "
        f"{'CANT.':<8} | {'ESTADO'}"
    )

    print("=" * 75)

    for l in lotes:

        cant_fmt = f"{l['cantidad_producida']:,}".replace(",", ".")
        area_fmt = f"{l['area_m2']:,.1f}"

        print(
            f"{l['id_lote']:<8} | "
            f"{l['producto_codigo']:<10} | "
            f"{l['fecha_siembra']:<14} | "
            f"{area_fmt:<10} | "
            f"{cant_fmt:<8} | "
            f"{l['estado']}"
        )

    print("=" * 75)


# Menú de lotes
def menu_lotes(datos):
    while True:

        print("\n MÓDULO DE LOTES PRODUCTIVOS ")
        print("1. Registrar lote")
        print("2. Cosechar lote")
        print("3. Cambiar estado de lote")
        print("4. Listar lotes")
        print("0. Volver al menú principal")

        opcion = input(
            "Seleccione una opción: "
        ).strip()

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
            print(
                "Opción inválida. Intente de nuevo."
            )


# Registra una entrada
def registrar_entrada_inventario(datos):
    print("\n Registrar Entrada Manual de Inventario")

    codigo_prod = leer_texto(
        "Ingrese el código del producto: "
    ).upper()

    prod = buscar_producto_por_codigo(
        datos["productos"],
        codigo_prod
    )

    if not prod:
        print(
            f"Error: El producto '{codigo_prod}' no existe."
        )
        return

    if not prod.get("activo", True):
        print(
            f"Error: El producto '{prod['nombre']}' "
            f"está deshabilitado/inactivo."
        )
        return

    cantidad = leer_entero_positivo(
        "Ingrese la cantidad a ingresar: "
    )

    motivo = leer_texto(
        "Ingrese el motivo obligatorio de la entrada: "
    )

    fecha_mov = datetime.now().strftime(
        "%d/%m/%Y %H:%M"
    )

    id_mov = generar_id_secuencial(
        datos["movimientos"],
        "M",
        "id"
    )

    nuevo_movimiento = {
        "id": id_mov,
        "producto_codigo": codigo_prod,
        "tipo": "ENTRADA",
        "cantidad": cantidad,
        "motivo": motivo,
        "fecha": fecha_mov
    }

    datos["movimientos"].append(
        nuevo_movimiento
    )

    guardar_datos_json(
        RUTAS_ARCHIVOS["movimientos"],
        datos["movimientos"]
    )

    print(
        f"\n Entrada {id_mov} registrada correctamente "
        f"para '{prod['nombre']}'."
    )


# Registra una salida
def registrar_salida_inventario(datos):
    print("\n Registrar Salida Manual de Inventario ")

    codigo_prod = leer_texto(
        "Ingrese el código del producto: "
    ).upper()

    prod = buscar_producto_por_codigo(
        datos["productos"],
        codigo_prod
    )

    if not prod:
        print(
            f"Error: El producto '{codigo_prod}' no existe."
        )
        return

    stock_disponible = calcular_stock_producto(
        datos["movimientos"],
        codigo_prod
    )

    print(
        f"Stock actual disponible para "
        f"'{prod['nombre']}': {stock_disponible:,} unidades."
    )

    cantidad = leer_entero_positivo(
        "Ingrese la cantidad a retirar: "
    )

    if cantidad > stock_disponible:
        print(
            f"Error: Operación denegada. El stock disponible "
            f"({stock_disponible:,}) es insuficiente para retirar "
            f"{cantidad:,} unidades."
        )
        return

    motivo = leer_texto(
        "Ingrese el motivo obligatorio de la salida: "
    )

    fecha_mov = datetime.now().strftime(
        "%d/%m/%Y %H:%M"
    )

    id_mov = generar_id_secuencial(
        datos["movimientos"],
        "M",
        "id"
    )

    nuevo_movimiento = {
        "id": id_mov,
        "producto_codigo": codigo_prod,
        "tipo": "SALIDA",
        "cantidad": cantidad,
        "motivo": motivo,
        "fecha": fecha_mov
    }

    datos["movimientos"].append(
        nuevo_movimiento
    )

    guardar_datos_json(
        RUTAS_ARCHIVOS["movimientos"],
        datos["movimientos"]
    )

    print(
        f"\nSalida {id_mov} registrada correctamente "
        f"para '{prod['nombre']}'. Nuevo stock: "
        f"{stock_disponible - cantidad:,}."
    )


# Lista los movimientos
def listar_movimientos(movimientos):
    if not movimientos:
        print(
            "\nNo existen movimientos de inventario registrados."
        )
        return

    print("\n" + "=" * 85)

    print(
        f"{'ID':<7} | {'PROD. CÓD':<10} | "
        f"{'TIPO':<8} | {'CANTIDAD':<10} | "
        f"{'FECHA':<16} | {'MOTIVO'}"
    )

    print("=" * 85)

    for m in movimientos:

        cant_fmt = f"{m['cantidad']:,}".replace(",", ".")

        print(
            f"{m['id']:<7} | "
            f"{m['producto_codigo']:<10} | "
            f"{m['tipo']:<8} | "
            f"{cant_fmt:<10} | "
            f"{m['fecha']:<16} | "
            f"{m['motivo']}"
        )

    print("=" * 85)


# Menú de inventario
def menu_inventario(datos):
    while True:

        print("\n MÓDULO DE MOVIMIENTOS DE INVENTARIO")
        print("1. Registrar entrada manual")
        print("2. Registrar salida manual")
        print("3. Consultar historial de movimientos")
        print("0. Volver al menú principal")

        opcion = input(
            "Seleccione una opción: "
        ).strip()

        if opcion == "1":
            registrar_entrada_inventario(datos)

        elif opcion == "2":
            registrar_salida_inventario(datos)

        elif opcion == "3":
            listar_movimientos(
                datos["movimientos"]
            )

        elif opcion == "0":
            break

        else:
            print(
                "Opción inválida. Intente de nuevo."
            )


# Registra una venta
def registrar_venta(datos):
    print("\nRegistrar Venta")

    cliente = leer_texto(
        "Nombre del cliente: "
    )

    items_venta = []
    total_venta = 0

    while True:

        codigo_prod = leer_texto(
            "Ingrese código del producto o FIN para procesar la venta: "
        ).upper()

        if codigo_prod == "FIN":

            if not items_venta:
                print(
                    "No ha agregado productos a la venta. Operación cancelada."
                )
                return

            break

        prod = buscar_producto_por_codigo(
            datos["productos"],
            codigo_prod
        )

        if not prod:
            print(
                f"Error: El producto con código "
                f"'{codigo_prod}' no existe."
            )
            continue

        if not prod.get("activo", True):
            print(
                f"Error: El producto '{prod['nombre']}' "
                f"({codigo_prod}) está deshabilitado."
            )
            continue

        stock_disponible = calcular_stock_producto(
            datos["movimientos"],
            codigo_prod
        )

        ya_agregado = sum(
            item["cantidad"]
            for item in items_venta
            if item["producto_codigo"] == codigo_prod
        )

        stock_efectivo = stock_disponible - ya_agregado

        print(
            f"Producto: {prod['nombre']} | "
            f"Precio: ${prod['precio']:,} | "
            f"Stock disponible: {stock_efectivo:,}"
        )

        if stock_efectivo <= 0:
            print(
                f"Error: No hay stock disponible para "
                f"'{prod['nombre']}'."
            )
            continue

        cantidad = leer_entero_positivo(
            "Cantidad a vender: "
        )

        if cantidad > stock_efectivo:
            print(
                f"Error: Stock insuficiente. "
                f"Disponible para venta: "
                f"{stock_efectivo:,} unidades."
            )
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

        print(
            f" Agregado: {cantidad}x {prod['nombre']} "
            f"- Subtotal: ${subtotal:,}"
        )

    id_venta = generar_id_secuencial(
        datos["ventas"],
        "V",
        "id_venta"
    )

    fecha_venta = datetime.now().strftime(
        "%d/%m/%Y %H:%M"
    )

    nueva_venta = {
        "id_venta": id_venta,
        "cliente": cliente,
        "fecha": fecha_venta,
        "items": items_venta,
        "total": total_venta
    }

    datos["ventas"].append(
        nueva_venta
    )

    for item in items_venta:

        id_mov = generar_id_secuencial(
            datos["movimientos"],
            "M",
            "id"
        )

        nuevo_movimiento = {
            "id": id_mov,
            "producto_codigo": item["producto_codigo"],
            "tipo": "SALIDA",
            "cantidad": item["cantidad"],
            "motivo": f"Venta {id_venta}",
            "fecha": fecha_venta
        }

        datos["movimientos"].append(
            nuevo_movimiento
        )

    guardar_datos_json(
        RUTAS_ARCHIVOS["ventas"],
        datos["ventas"]
    )

    guardar_datos_json(
        RUTAS_ARCHIVOS["movimientos"],
        datos["movimientos"]
    )

    print(
        f"\n Venta {id_venta} registrada exitosamente "
        f"a nombre de '{cliente}'."
    )

    print(
        f" Total cobrado: ${total_venta:,}"
    )


# Consulta las ventas
def consultar_ventas(ventas):
    if not ventas:
        print(
            "\nNo existen ventas registradas en el sistema."
        )
        return

    print("\n" + "=" * 70)

    print(
        f"{'FOLIO':<8} | {'FECHA':<16} | "
        f"{'CLIENTE':<25} | {'TOTAL'}"
    )

    print("=" * 70)

    for v in ventas:

        total_fmt = f"${v['total']:,}".replace(",", ".")

        print(
            f"{v['id_venta']:<8} | "
            f"{v['fecha']:<16} | "
            f"{v['cliente']:<25} | "
            f"{total_fmt}"
        )

    print("=" * 70)


# Revisa el stock
def verificar_alertas_stock(datos):
    print("\n ALERTAS DE STOCK BAJO")

    productos = datos["productos"]
    movimientos = datos["movimientos"]

    alertas = []

    for p in productos:

        if not p.get("activo", True):
            continue

        stock_act = calcular_stock_producto(
            movimientos,
            p["codigo"]
        )

        if stock_act <= p["stock_minimo"]:
            alertas.append(
                (p, stock_act)
            )

    if not alertas:
        print(
            "\nTodos los productos activos cuentan con "
            "stock suficiente por encima del mínimo."
        )
        return

    print(
        "\n¡ATENCIÓN! Los siguientes productos han alcanzado "
        "o están por debajo del stock mínimo:"
    )

    print("=" * 80)

    print(
        f"{'CÓDIGO':<8} | {'NOMBRE':<20} | "
        f"{'STOCK ACTUAL':<14} | {'STOCK MÍNIMO':<14} | {'ESTADO'}"
    )

    print("=" * 80)

    for p, stock_act in alertas:

        estado_alerta = (
            "CRÍTICO (0)"
            if stock_act == 0
            else "ALERTA BAJA"
        )

        print(
            f"{p['codigo']:<8} | "
            f"{p['nombre']:<20} | "
            f"{stock_act:<14} | "
            f"{p['stock_minimo']:<14} | "
            f"{estado_alerta}"
        )

    print("=" * 80)


# Muestra los reportes
def generar_reportes(datos):
    print(
        "\n==================== REPORTES CONSOLIDADOS AGROCONTROL ===================="
    )

    productos_activos = [
        p for p in datos["productos"]
        if p.get("activo", True)
    ]

    movimientos = datos["movimientos"]

    valor_total_inventario = 0
    total_unidades_inventario = 0

    print(
        "\n1. EXISTENCIAS Y VALOR DEL INVENTARIO (PRECIO DE VENTA)"
    )

    print("=" * 75)

    print(
        f"{'CÓDIGO':<8} | {'NOMBRE':<20} | "
        f"{'STOCK ACT.':<10} | {'P. VENTA':<10} | {'VALOR TOTAL'}"
    )

    print("=" * 75)

    for p in productos_activos:

        stock = calcular_stock_producto(
            movimientos,
            p["codigo"]
        )

        valor_producto = (
            stock * p["precio"]
            if stock > 0
            else 0
        )

        if stock > 0:
            total_unidades_inventario += stock
            valor_total_inventario += valor_producto

        stock_fmt = f"{stock:,}".replace(",", ".")
        precio_fmt = f"${p['precio']:,}".replace(",", ".")
        valor_fmt = f"${valor_producto:,}".replace(",", ".")

        print(
            f"{p['codigo']:<8} | "
            f"{p['nombre']:<20} | "
            f"{stock_fmt:<10} | "
            f"{precio_fmt:<10} | "
            f"{valor_fmt}"
        )

    print("=" * 75)

    print(
        f"Total unidades en stock: "
        f"{total_unidades_inventario:,}".replace(",", ".")
    )

    print(
        f"VALOR TOTAL DEL INVENTARIO: "
        f"${valor_total_inventario:,}".replace(",", ".")
    )

    ventas = datos["ventas"]

    num_ventas = len(ventas)

    ingresos_acumulados = sum(
        v["total"]
        for v in ventas
    )

    unidades_vendidas_totales = sum(
        item["cantidad"]
        for v in ventas
        for item in v.get("items", [])
    )

    print("\n2. REPORTE DE VENTAS CONSOLIDADO")

    print(
        f"   - Número de ventas realizadas: {num_ventas}"
    )

    print(
        f"   - Total unidades vendidas:     "
        f"{unidades_vendidas_totales:,}".replace(",", ".")
    )

    print(
        f"   - Ingresos acumulados:         "
        f"${ingresos_acumulados:,}".replace(",", ".")
    )

    acumulado_por_producto = {}

    for v in ventas:

        for item in v.get("items", []):

            cod = item["producto_codigo"]
            nom = item["nombre"]
            cant = item["cantidad"]

            if cod not in acumulado_por_producto:
                acumulado_por_producto[cod] = {
                    "nombre": nom,
                    "cantidad": 0
                }

            acumulado_por_producto[cod]["cantidad"] += cant

    top_productos = sorted(
        acumulado_por_producto.items(),
        key=lambda x: x[1]["cantidad"],
        reverse=True
    )[:3]

    print(
        "\n3. RANKING TOP 3 PRODUCTOS MÁS VENDIDOS"
    )

    print("=" * 60)

    if not top_productos:

        print(
            "   No hay registros de ventas para calcular el ranking."
        )

    else:

        for i, (cod, info) in enumerate(
            top_productos,
            start=1
        ):

            cant_fmt = f"{info['cantidad']:,}".replace(",", ".")

            print(
                f"   {i}°. [{cod}] "
                f"{info['nombre']:<20} - "
                f"{cant_fmt} unidades vendidas"
            )

    print("=" * 60)

    print(
        "\n4. RESUMEN DE PRODUCCIÓN Y LOTES"
    )

    lotes = datos["lotes"]

    lotes_cosechados = [
        l for l in lotes
        if l["estado"] == "COSECHADO"
    ]

    lotes_proceso = [
        l for l in lotes
        if l["estado"] == "EN_PRODUCCION"
    ]

    total_cosechado = sum(
        l["cantidad_producida"]
        for l in lotes_cosechados
    )

    print(
        f"   - Total de lotes registrados: {len(lotes)}"
    )

    print(
        f"   - Lotes en producción: {len(lotes_proceso)}"
    )

    print(
        f"   - Lotes cosechados: {len(lotes_cosechados)}"
    )

    print(
        f"   - Total unidades producidas (cosechas): "
        f"{total_cosechado:,}".replace(",", ".")
    )


# Reto: ventas por fechas
def ventas_por_fecha(datos):
    print("\n VENTAS POR RANGO DE FECHAS")

    fecha_inicio = leer_fecha_ddmmyyyy(
        "Ingrese la fecha inicial (dd/mm/aaaa): "
    )

    fecha_fin = leer_fecha_ddmmyyyy(
        "Ingrese la fecha final (dd/mm/aaaa): "
    )

    inicio = datetime.strptime(
        fecha_inicio,
        "%d/%m/%Y"
    )

    fin = datetime.strptime(
        fecha_fin,
        "%d/%m/%Y"
    )

    if inicio > fin:
        print("Error: La fecha inicial no puede ser mayor que la fecha final.")
        return

    resultados = []

    for venta in datos["ventas"]:

        try:
            fecha_venta = datetime.strptime(
                venta["fecha"][:10],
                "%d/%m/%Y"
            )

            if inicio <= fecha_venta <= fin:
                resultados.append(venta)

        except ValueError:
            continue

    if not resultados:
        print(
            "\nNo existen ventas en el rango seleccionado."
        )
        return

    total = sum(
        v["total"]
        for v in resultados
    )

    print(
        f"\nVentas encontradas: {len(resultados)}"
    )

    print(
        f"Total vendido: ${total:,}".replace(",", ".")
    )

    for venta in resultados:

        print(
            f"{venta['id_venta']} | "
            f"{venta['fecha']} | "
            f"{venta['cliente']} | "
            f"${venta['total']:,}".replace(",", ".")
        )


# Reto: calcula una utilidad estimada
def calcular_utilidad(datos):
    print("\n UTILIDAD ESTIMADA")

    ventas = datos["ventas"]

    if not ventas:
        print(
            "\nNo existen ventas para calcular la utilidad."
        )
        return

    ingresos = 0
    costo_estimado = 0

    for venta in ventas:

        ingresos += venta["total"]

        for item in venta.get("items", []):

            precio = item.get(
                "precio_unitario",
                0
            )

            cantidad = item.get(
                "cantidad",
                0
            )

            costo = precio * 0.70

            costo_estimado += costo * cantidad

    utilidad = ingresos - costo_estimado

    print(
        f"\nIngresos: ${ingresos:,.0f}".replace(",", ".")
    )

    print(
        f"Costo estimado: ${costo_estimado:,.0f}".replace(",", ".")
    )

    print(
        f"Utilidad estimada: ${utilidad:,.0f}".replace(",", ".")
    )

    print(
        "\nLa utilidad se calcula usando un costo estimado del 70% del precio."
    )


# Reto: registra una devolución
def registrar_devolucion(datos):
    print("\n REGISTRAR DEVOLUCIÓN")

    id_venta = leer_texto(
        "Ingrese el número de la venta: "
    ).upper()

    venta_encontrada = None

    for venta in datos["ventas"]:

        if venta["id_venta"].upper() == id_venta:
            venta_encontrada = venta
            break

    if not venta_encontrada:
        print(
            f"Error: No existe la venta '{id_venta}'."
        )
        return

    codigo_prod = leer_texto(
        "Ingrese el código del producto a devolver: "
    ).upper()

    item_encontrado = None

    for item in venta_encontrada.get("items", []):

        if item["producto_codigo"].upper() == codigo_prod:
            item_encontrado = item
            break

    if not item_encontrado:
        print(
            f"Error: El producto '{codigo_prod}' "
            f"no pertenece a la venta."
        )
        return

    cantidad = leer_entero_positivo(
        "Ingrese la cantidad a devolver: "
    )

    cantidad_devuelta = item_encontrado.get(
        "cantidad_devuelta",
        0
    )

    cantidad_disponible = (
        item_encontrado["cantidad"]
        - cantidad_devuelta
    )

    if cantidad > cantidad_disponible:
        print(
            f"Error: Solo se pueden devolver "
            f"{cantidad_disponible} unidades."
        )
        return

    item_encontrado["cantidad_devuelta"] = (
        cantidad_devuelta + cantidad
    )

    id_mov = generar_id_secuencial(
        datos["movimientos"],
        "M",
        "id"
    )

    fecha_mov = datetime.now().strftime(
        "%d/%m/%Y %H:%M"
    )

    nuevo_movimiento = {
        "id": id_mov,
        "producto_codigo": codigo_prod,
        "tipo": "ENTRADA",
        "cantidad": cantidad,
        "motivo": f"Devolución venta {id_venta}",
        "fecha": fecha_mov
    }

    datos["movimientos"].append(
        nuevo_movimiento
    )

    guardar_datos_json(
        RUTAS_ARCHIVOS["ventas"],
        datos["ventas"]
    )

    guardar_datos_json(
        RUTAS_ARCHIVOS["movimientos"],
        datos["movimientos"]
    )

    print(
        f"\nDevolución registrada correctamente."
    )

    print(
        f"Se agregaron {cantidad} unidades al inventario."
    )


# Reto: exporta inventario a CSV
def exportar_inventario_csv(datos):
    ruta_csv = os.path.join(
        BASE_DIR,
        "data",
        "inventario.csv"
    )

    try:

        with open(
            ruta_csv,
            "w",
            newline="",
            encoding="utf-8-sig"
        ) as archivo:

            escritor = csv.writer(
                archivo,
                delimiter=";"
            )

            escritor.writerow([
                "Código",
                "Nombre",
                "Categoría",
                "Unidad",
                "Precio",
                "Stock actual",
                "Stock mínimo",
                "Estado"
            ])

            for producto in datos["productos"]:

                stock = calcular_stock_producto(
                    datos["movimientos"],
                    producto["codigo"]
                )

                estado = (
                    "Activo"
                    if producto.get("activo", True)
                    else "Inactivo"
                )

                escritor.writerow([
                    producto["codigo"],
                    producto["nombre"],
                    producto["categoria"],
                    producto["unidad"],
                    producto["precio"],
                    stock,
                    producto["stock_minimo"],
                    estado
                ])

        print(
            "\nInventario exportado correctamente a data/inventario.csv."
        )

    except OSError as e:

        print(
            f"\nError al exportar el inventario: {e}"
        )


# Reto: crea copias de los JSON
def crear_copias_seguridad(datos):
    fecha = datetime.now().strftime(
        "%Y%m%d_%H%M%S"
    )

    copias = 0

    for clave, ruta in RUTAS_ARCHIVOS.items():

        if clave == "usuarios":
            continue

        if not os.path.exists(ruta):
            continue

        nombre = os.path.basename(ruta)

        nombre_backup = (
            nombre.replace(
                ".json",
                f"_backup_{fecha}.json"
            )
        )

        ruta_backup = os.path.join(
            BASE_DIR,
            "data",
            nombre_backup
        )

        try:

            shutil.copy2(
                ruta,
                ruta_backup
            )

            copias += 1

        except OSError:
            pass

    print(
        f"\nCopias de seguridad creadas: {copias}"
    )


# Menú de retos
def menu_retos(datos):
    while True:

        print("\n MÓDULO DE RETOS DE AMPLIACIÓN")
        print("1. Consultar ventas por rango de fechas")
        print("2. Calcular utilidad estimada")
        print("3. Registrar devolución")
        print("4. Exportar inventario a CSV")
        print("5. Crear copias de seguridad")
        print("0. Volver al menú principal")

        opcion = input(
            "Seleccione una opción: "
        ).strip()

        if opcion == "1":
            ventas_por_fecha(datos)

        elif opcion == "2":
            calcular_utilidad(datos)

        elif opcion == "3":
            registrar_devolucion(datos)

        elif opcion == "4":
            exportar_inventario_csv(datos)

        elif opcion == "5":
            crear_copias_seguridad(datos)

        elif opcion == "0":
            break

        else:
            print(
                "Opción inválida. Intente de nuevo."
            )


# Menú principal
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
    print("9. Retos de ampliación")
    print("0. Salir")
    print("=========================================================")


# Inicio del programa
def main():

    datos = {
        "productos": cargar_datos_json(
            RUTAS_ARCHIVOS["productos"]
        ),

        "lotes": cargar_datos_json(
            RUTAS_ARCHIVOS["lotes"]
        ),

        "movimientos": cargar_datos_json(
            RUTAS_ARCHIVOS["movimientos"]
        ),

        "ventas": cargar_datos_json(
            RUTAS_ARCHIVOS["ventas"]
        ),

        "usuarios": cargar_datos_json(
            RUTAS_ARCHIVOS["usuarios"]
        ),
    }

    if not datos["usuarios"]:

        print(
            "\nNo existen usuarios registrados."
        )

        print(
            "Cree el archivo data/usuarios.json "
            "para poder ingresar."
        )

        return

    usuario_actual = iniciar_sesion(
        datos["usuarios"]
    )

    if not usuario_actual:
        return

    mantenimiento = True

    while mantenimiento:

        mostrar_menu()

        opcion = input(
            "Seleccione una opción: "
        ).strip()

        if opcion == "1":
            menu_productos(datos)

        elif opcion == "2":
            menu_lotes(datos)

        elif opcion == "3":
            menu_inventario(datos)

        elif opcion == "4":
            registrar_venta(datos)

        elif opcion == "5":
            consultar_ventas(
                datos["ventas"]
            )

        elif opcion == "6":
            verificar_alertas_stock(datos)

        elif opcion == "7":
            generar_reportes(datos)

        elif opcion == "8":
            guardar_todo(datos)

        elif opcion == "9":
            menu_retos(datos)

        elif opcion == "0":

            guardar_todo(datos)

            print(
                "\nSaliendo de AgroControl CBA. ¡Hasta luego!"
            )

            mantenimiento = False

        else:
            print(
                "\nOpción no válida. Intente nuevamente."
            )


if __name__ == "__main__":
    main()
