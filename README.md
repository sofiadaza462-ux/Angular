
Integrantes: Deiner Marin 
Alisson Daza
Sharith Daza
Diego gomez 
Yeilly Corredor 

# Sistema de Gestión Agropecuaria (AgroControl)

Este proyecto es una aplicación sencilla e integrada para llevar el control diario de productos, la producción del campo, la bodega y la facturación de ventas. 

Está diseñado para funcionar en un solo paquete continuo, asegurando que toda la información registrada se guarde de forma permanente entre cada uso.

##  ¿Qué permite hacer este sistema?

El sistema está dividido en varias secciones de trabajo interconectadas

### 1. Gestión de Productos
Permite administrar el catálogo base de lo que produce o maneja el centro agropecuario.
 Registrar productos: Guardar elementos nuevos asignándoles código, nombre, categoría, unidad de medida, precio de venta y un stock mínimo recomendado.
 
 Consultar y buscar: Ver la lista de productos activos o inactivos, o buscar uno específico por su código o nombre.
 
 Actualizar datos: Modificar la información de un producto si cambia su precio, nombre o límites de inventario.
 
 Desactivar productos: Ocultar productos que ya no se utilicen para evitar que se sigan registrando en siembras o ventas.


### 2. Gestión de Lotes Productivos
Lleva el seguimiento del ciclo de siembra y recolección en los terrenos del centro.

Registrar lotes: Asociar una nueva siembra a un producto activo, asignando fecha, tamaño del terreno (m²) y generando un identificador automático.

Cosechar lotes: Registrar la cantidad total recolectada al finalizar el ciclo. Al cosechar, el sistema envía automáticamente esas unidades a la bodega.

Cambiar estado:Actualizar si el lote está en producción o si fue cancelado por algún inconveniente.

Listar lotes: Ver el historial y estado actual de todas las zonas de cultivo.


### 3. Movimientos de Inventario (Bodega)
Controla las entradas y salidas de mercancía para mantener las existencias al día.

Entradas manuales: Ingresar mercancía a bodega especificando el motivo (por ejemplo, compras adicionales o devoluciones).

Salidas manuales: Retirar mercancía de bodega especificando el motivo (por ejemplo, pérdidas, autoconsumo o daño).

Validación de existencias: El sistema impide retirar más cantidad de la que realmente hay disponible en bodega.

Consultar historial: Ver la lista detallada de todos los movimientos de entrada y salida realizados con sus respectivas fechas y motivos.

### 4. Registro de Ventas
Permite comercializar los productos disponibles directamente a los clientes.

Procesar ventas: Seleccionar uno o varios productos, verificar si hay cantidad suficiente en bodega y calcular el total a cobrar.

Descuento automático: Cada producto vendido descuenta de forma inmediata las unidades correspondientes del inventario general.

Identificación del cliente: Asocia cada venta al nombre del comprador y genera un número de comprobante único.


### 5. Consulta de Ventas
Permite revisar la información comercial registrada.

Historial de facturación: Muestra el listado con el número de comprobante, la fecha, la hora, el nombre del cliente y el dinero total cobrado en cada transacción.


##  Guardado de Información

Toda la información registrada en cualquiera de los módulos (productos, siembras, bodega y ventas) se guarda automáticamente en archivos de texto dentro del sistema. Esto garantiza que al cerrar y volver a abrir la aplicación, no se pierda ningún dato.


### 6. Alertas de Stock Bajo
Mantiene un control preventivo sobre las existencias en bodega para evitar el desabastecimiento.

Detección automática: Revisa continuamente la cantidad disponible de cada producto activo y la compara con el límite mínimo configurado.

Avisos de atención: Muestra una lista detallada señalando los productos que han alcanzado o están por debajo de su cantidad mínima requerida.

Nivel de urgencia:Identifica de forma clara los productos que se encuentran en estado crítico (sin unidades disponibles) de aquellos que están próximos a agotarse.

