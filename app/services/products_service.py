from io import BytesIO

import pymysql
from PIL import Image, ImageOps, UnidentifiedImageError

from database.init_db import conectar

# =========================
# OFERTAS (descuento por producto)
# =========================

# tope del porcentaje que el admin puede asignar a un producto
DESCUENTO_MAXIMO = 90

# precio que paga el cliente por una existencia `e` de un producto `p`:
# el precio de lista menos el descuento del producto, en pesos enteros.
# Lo usan el catalogo, la ficha, el carrito y (a traves del carrito) la
# factura, asi todos muestran y cobran lo mismo.
PRECIO_FINAL_SQL = "ROUND(e.precio * (100 - p.descuento) / 100)"

# =========================
# NOVEDADES
# =========================

# un producto es "nuevo" durante estos dias desde que se crea en el panel;
# despues deja de serlo solo (sale de /nuevo y pierde la etiqueta)
DIAS_NUEVO = 30
ES_NUEVO_SQL = f"(p.created_at >= NOW() - INTERVAL {DIAS_NUEVO} DAY)"


def asegurar_columna_descuento():
    """Agrega productos.descuento si la base es anterior a las ofertas
    (equivale a database/migraciones/001_descuento_productos.sql).
    """
    conexion = conectar()
    cursor = conexion.cursor()
    try:
        cursor.execute(
            """
            SELECT 1 FROM information_schema.COLUMNS
            WHERE TABLE_SCHEMA = DATABASE() AND TABLE_NAME = 'productos'
              AND COLUMN_NAME = 'descuento'
            """
        )
        if not cursor.fetchone():
            cursor.execute(
                """
                ALTER TABLE productos
                ADD COLUMN descuento tinyint(3) UNSIGNED NOT NULL DEFAULT 0
                COMMENT 'Porcentaje de descuento (0 = sin oferta)'
                AFTER estado
                """
            )
            conexion.commit()
    finally:
        conexion.close()


def _leer_descuento(datos):
    """Valida el porcentaje de descuento de un formulario (vacio = 0)."""
    valor = str(datos.get("descuento", "") or "0").strip()
    try:
        descuento = int(valor)
    except ValueError:
        descuento = -1
    if not 0 <= descuento <= DESCUENTO_MAXIMO:
        raise ValueError(
            "El descuento debe ser un número entero entre 0 y {} %".format(DESCUENTO_MAXIMO)
        )
    return descuento


def _condicion_filtros_existencia(talla_id=None, precio_min=None, precio_max=None):
    """Condiciones para filtrar existencias por talla/rango de precio.

    Devuelve (condiciones_sql, parametros): una lista de fragmentos SQL
    listos para unir con " AND " y sus parametros, reutilizable tanto
    para acotar que productos aparecen (EXISTS) como para acotar que
    existencias se muestran por producto.
    """
    condiciones = []
    parametros = []

    if talla_id:
        condiciones.append("e.talla_id = %s")
        parametros.append(talla_id)
    if precio_min:
        condiciones.append(f"{PRECIO_FINAL_SQL} >= %s")
        parametros.append(precio_min)
    if precio_max:
        condiciones.append(f"{PRECIO_FINAL_SQL} <= %s")
        parametros.append(precio_max)

    return condiciones, parametros


def _consultar_productos(
    cursor,
    condicion="",
    parametros=(),
    talla_id=None,
    precio_min=None,
    precio_max=None,
):
    filtros_existencia, params_filtro = _condicion_filtros_existencia(
        talla_id, precio_min, precio_max
    )

    sql = f"""
        SELECT p.id, p.referencia, p.nombre, p.descripcion, p.categoria_id,
               p.marca_id, p.estado, p.descuento, p.created_at, p.updated_at,
               (p.imagen IS NOT NULL) AS tiene_imagen,
               {ES_NUEVO_SQL} AS es_nuevo,
               MIN({PRECIO_FINAL_SQL}) AS precio_desde,
               MIN(e.precio) AS precio_original_desde,
               COALESCE(SUM(e.stock), 0) AS stock_total
        FROM productos p
        LEFT JOIN existencias e ON e.producto_id = p.id AND e.estado = 'activo'
        WHERE p.estado = 'activo'
    """
    parametros = list(parametros)
    if condicion:
        sql += f" AND {condicion}"
    if filtros_existencia:
        sql += """ AND EXISTS (
            SELECT 1 FROM existencias ex
            WHERE ex.producto_id = p.id AND ex.estado = 'activo' AND {}
        )""".format(" AND ".join(c.replace("e.", "ex.") for c in filtros_existencia))
        parametros += params_filtro
    # lo mas reciente primero en todo el catalogo
    sql += " GROUP BY p.id ORDER BY p.created_at DESC, p.id DESC"
    cursor.execute(sql, parametros)
    productos = cursor.fetchall()

    if not productos:
        return productos

    ids = [p["id"] for p in productos]
    formato = ",".join(["%s"] * len(ids))
    sql_tallas = f"""
        SELECT e.id AS existencia_id, e.producto_id,
               {PRECIO_FINAL_SQL} AS precio, e.precio AS precio_original, e.stock,
               t.id AS talla_id, t.nombre AS talla
        FROM existencias e
        JOIN productos p ON p.id = e.producto_id
        JOIN tallas t ON t.id = e.talla_id
        WHERE e.producto_id IN ({formato}) AND e.estado = 'activo'
    """
    params_tallas = list(ids)
    if filtros_existencia:
        sql_tallas += " AND " + " AND ".join(filtros_existencia)
        params_tallas += params_filtro
    sql_tallas += " ORDER BY t.id, e.precio ASC"
    cursor.execute(sql_tallas, params_tallas)

    tallas_por_producto = {}
    for fila in cursor.fetchall():
        vistas = tallas_por_producto.setdefault(fila["producto_id"], {})
        # cada (producto, talla) es una sola existencia (clave unica en la BD)
        vistas.setdefault(
            fila["talla_id"],
            {
                "talla_id": fila["talla_id"],
                "nombre": fila["talla"],
                "existencia_id": fila["existencia_id"],
                "precio": fila["precio"],
                "precio_original": fila["precio_original"],
                "stock": fila["stock"],
            },
        )

    for producto in productos:
        producto["tallas"] = list(tallas_por_producto.get(producto["id"], {}).values())

    return productos


def obtener_productos(talla_id=None, precio_min=None, precio_max=None):
    conexion = conectar()
    cursor = conexion.cursor()
    productos = _consultar_productos(
        cursor, talla_id=talla_id, precio_min=precio_min, precio_max=precio_max
    )
    conexion.close()
    return productos


def obtener_nuevos(categoria_id=None, talla_id=None, precio_min=None, precio_max=None):
    """Productos creados en los ultimos DIAS_NUEVO dias, del mas reciente
    al mas antiguo; opcionalmente solo los de una categoria.
    """
    condicion = ES_NUEVO_SQL
    parametros = ()
    if categoria_id:
        condicion += " AND p.categoria_id = %s"
        parametros = (categoria_id,)

    conexion = conectar()
    cursor = conexion.cursor()
    productos = _consultar_productos(
        cursor,
        condicion,
        parametros,
        talla_id=talla_id,
        precio_min=precio_min,
        precio_max=precio_max,
    )
    conexion.close()
    return productos


def obtener_categoria(id, talla_id=None, precio_min=None, precio_max=None):
    conexion = conectar()
    cursor = conexion.cursor()
    productos = _consultar_productos(
        cursor,
        "p.categoria_id = %s",
        (id,),
        talla_id=talla_id,
        precio_min=precio_min,
        precio_max=precio_max,
    )
    conexion.close()
    return productos


def buscar_productos(query, talla_id=None, precio_min=None, precio_max=None):
    if not query:
        return []

    conexion = conectar()
    cursor = conexion.cursor()
    like = f"%{query}%"
    productos = _consultar_productos(
        cursor,
        "(p.nombre LIKE %s OR p.descripcion LIKE %s)",
        (like, like),
        talla_id=talla_id,
        precio_min=precio_min,
        precio_max=precio_max,
    )
    conexion.close()
    return productos


def obtener_ofertas():
    """Productos activos con descuento, para la pagina de Ofertas: primero
    los que tienen stock, luego los de mayor descuento y, entre esos, los
    mas nuevos. Los que no tienen ninguna talla activa (sin precio) no se
    muestran: no hay nada que rebajar.
    """
    conexion = conectar()
    cursor = conexion.cursor()
    productos = _consultar_productos(cursor, "p.descuento > 0")
    conexion.close()
    productos = [p for p in productos if p["precio_desde"] is not None]
    return sorted(
        productos,
        key=lambda p: (p["stock_total"] > 0, p["descuento"], p["created_at"]),
        reverse=True,
    )


def obtener_detalle_producto(id):
    """Ficha completa de un producto activo: categoria, marca y todas sus
    existencias (una por talla) para la pagina de detalle. Devuelve None
    si no existe o esta inactivo.
    """
    conexion = conectar()
    cursor = conexion.cursor()
    cursor.execute(
        f"""
        SELECT p.id, p.referencia, p.nombre, p.descripcion, p.categoria_id,
               p.descuento, (p.imagen IS NOT NULL) AS tiene_imagen,
               {ES_NUEVO_SQL} AS es_nuevo,
               c.nombre AS categoria_nombre, m.nombre AS marca_nombre
        FROM productos p
        JOIN categorias c ON c.id = p.categoria_id
        JOIN marcas m ON m.id = p.marca_id
        WHERE p.id = %s AND p.estado = 'activo'
        """,
        (id,),
    )
    producto = cursor.fetchone()

    if producto:
        cursor.execute(
            f"""
            SELECT e.id AS existencia_id, {PRECIO_FINAL_SQL} AS precio,
                   e.precio AS precio_original, e.stock,
                   t.id AS talla_id, t.nombre AS talla
            FROM existencias e
            JOIN productos p ON p.id = e.producto_id
            JOIN tallas t ON t.id = e.talla_id
            WHERE e.producto_id = %s AND e.estado = 'activo'
            ORDER BY t.id
            """,
            (id,),
        )
        existencias = cursor.fetchall()
        for e in existencias:
            e["precio"] = float(e["precio"])
            e["precio_original"] = float(e["precio_original"])
        producto["existencias"] = existencias

        precios = [e["precio"] for e in existencias]
        producto["precio_desde"] = min(precios) if precios else None
        producto["stock_total"] = sum(e["stock"] for e in existencias)

        producto["tallas"] = [
            {"id": e["talla_id"], "nombre": e["talla"]} for e in existencias
        ]

    conexion.close()
    return producto


def obtener_relacionados(producto_id, categoria_id, limite=4):
    """Otros productos de la misma categoria para "Tambien te puede gustar"."""
    conexion = conectar()
    cursor = conexion.cursor()
    productos = _consultar_productos(
        cursor, "p.categoria_id = %s AND p.id <> %s", (categoria_id, producto_id)
    )
    conexion.close()
    return productos[:limite]


def listar_tallas():
    conexion = conectar()
    cursor = conexion.cursor()
    cursor.execute("SELECT * FROM tallas ORDER BY id")
    tallas = cursor.fetchall()
    conexion.close()
    return tallas


# =========================
# CRUD (Admin)
# =========================


def listar_productos_admin():
    conexion = conectar()
    cursor = conexion.cursor()
    cursor.execute(
        """
        SELECT p.id, p.referencia, p.nombre, p.descripcion, p.categoria_id,
               p.marca_id, p.estado, p.descuento, p.created_at, p.updated_at,
               (p.imagen IS NOT NULL) AS tiene_imagen,
               c.nombre AS categoria_nombre, m.nombre AS marca_nombre,
               (
                   SELECT COUNT(*) FROM detalle_factura df
                   JOIN existencias e ON e.id = df.existencia_id
                   WHERE e.producto_id = p.id
               ) AS ventas
        FROM productos p
        JOIN categorias c ON c.id = p.categoria_id
        JOIN marcas m ON m.id = p.marca_id
        """
    )
    productos = cursor.fetchall()
    conexion.close()
    return productos


def obtener_imagen_producto(id):
    conexion = conectar()
    cursor = conexion.cursor()
    cursor.execute(
        "SELECT imagen, imagen_mime FROM productos WHERE id = %s", (id,)
    )
    fila = cursor.fetchone()
    conexion.close()
    return fila


def listar_categorias():
    conexion = conectar()
    cursor = conexion.cursor()
    cursor.execute(
        "SELECT id, nombre, (imagen IS NOT NULL) AS tiene_imagen FROM categorias ORDER BY id"
    )
    categorias = cursor.fetchall()
    conexion.close()
    return categorias


def listar_categorias_vitrina(miniaturas=3):
    """Categorias para la pagina de colecciones, con lo que tienen dentro:
    cuantos productos activos, precio desde, unidades disponibles y los
    ids de hasta `miniaturas` productos con foto para mostrarlos.
    """
    conexion = conectar()
    cursor = conexion.cursor()
    cursor.execute(
        f"""
        SELECT c.id, c.nombre, (c.imagen IS NOT NULL) AS tiene_imagen,
               COUNT(DISTINCT p.id) AS total_productos,
               MIN({PRECIO_FINAL_SQL}) AS precio_desde,
               COALESCE(SUM(e.stock), 0) AS stock_total
        FROM categorias c
        LEFT JOIN productos p ON p.categoria_id = c.id AND p.estado = 'activo'
        LEFT JOIN existencias e ON e.producto_id = p.id AND e.estado = 'activo'
        GROUP BY c.id, c.nombre
        ORDER BY c.id
        """
    )
    categorias = cursor.fetchall()

    cursor.execute(
        """
        SELECT id, nombre, categoria_id FROM productos
        WHERE estado = 'activo' AND imagen IS NOT NULL
        ORDER BY created_at DESC, id DESC
        """
    )
    por_categoria = {}
    for producto in cursor.fetchall():
        lista = por_categoria.setdefault(producto["categoria_id"], [])
        if len(lista) < miniaturas:
            lista.append(producto)
    conexion.close()

    for categoria in categorias:
        categoria["miniaturas"] = por_categoria.get(categoria["id"], [])
    return categorias


def obtener_imagen_categoria(id):
    conexion = conectar()
    cursor = conexion.cursor()
    cursor.execute(
        "SELECT imagen, imagen_mime FROM categorias WHERE id = %s", (id,)
    )
    fila = cursor.fetchone()
    conexion.close()
    return fila


def crear_categoria(datos, archivo_imagen=None):
    nombre = datos.get("nombre", "").strip()
    if not nombre:
        raise ValueError("El nombre de la categoría es obligatorio")
    imagen, imagen_mime = _leer_imagen(archivo_imagen)

    conexion = conectar()
    cursor = conexion.cursor()
    try:
        cursor.execute(
            "INSERT INTO categorias (nombre, imagen, imagen_mime) VALUES (%s, %s, %s)",
            (nombre, imagen, imagen_mime),
        )
        conexion.commit()
    except pymysql.err.IntegrityError:
        conexion.rollback()
        raise ValueError("Ya existe una categoría con ese nombre")
    except pymysql.err.OperationalError:
        raise ValueError(ERROR_GUARDAR_IMAGEN)
    finally:
        _cerrar(conexion)


def actualizar_categoria(id, datos, archivo_imagen=None):
    nombre = datos.get("nombre", "").strip()
    if not nombre:
        raise ValueError("El nombre de la categoría es obligatorio")
    imagen, imagen_mime = _leer_imagen(archivo_imagen)

    conexion = conectar()
    cursor = conexion.cursor()
    try:
        if imagen is not None:
            cursor.execute(
                "UPDATE categorias SET nombre=%s, imagen=%s, imagen_mime=%s WHERE id=%s",
                (nombre, imagen, imagen_mime, id),
            )
        else:
            cursor.execute("UPDATE categorias SET nombre=%s WHERE id=%s", (nombre, id))
        conexion.commit()
    except pymysql.err.IntegrityError:
        conexion.rollback()
        raise ValueError("Ya existe una categoría con ese nombre")
    except pymysql.err.OperationalError:
        raise ValueError(ERROR_GUARDAR_IMAGEN)
    finally:
        _cerrar(conexion)


def eliminar_categoria(id):
    conexion = conectar()
    cursor = conexion.cursor()
    try:
        cursor.execute("DELETE FROM categorias WHERE id=%s", (id,))
        conexion.commit()
    except pymysql.err.IntegrityError:
        conexion.rollback()
        raise ValueError(
            "No se puede eliminar: hay productos asignados a esta categoría"
        )
    finally:
        conexion.close()


def listar_marcas():
    conexion = conectar()
    cursor = conexion.cursor()
    cursor.execute("SELECT * FROM marcas")
    marcas = cursor.fetchall()
    conexion.close()
    return marcas


TIPOS_IMAGEN_PERMITIDOS = {"image/jpeg", "image/png", "image/webp", "image/gif"}

# MySQL (XAMPP) trae max_allowed_packet = 1 MB por defecto: una consulta con
# una imagen mas grande se corta ("Lost connection to MySQL server"). Por eso
# las imagenes se guardan redimensionadas y comprimidas por debajo de este tope.
TAMANO_MAX_IMAGEN = 900 * 1024
LADO_MAX_IMAGEN = 1600


def _optimizar_imagen(datos):
    """Redimensiona y recomprime a WEBP hasta quedar bajo TAMANO_MAX_IMAGEN."""
    try:
        imagen = Image.open(BytesIO(datos))
        imagen.load()
    except (UnidentifiedImageError, OSError):
        raise ValueError("El archivo no es una imagen válida")

    imagen = ImageOps.exif_transpose(imagen)  # respeta la rotacion de fotos de celular
    if imagen.mode not in ("RGB", "RGBA"):
        imagen = imagen.convert("RGBA" if "transparency" in imagen.info else "RGB")

    lado = LADO_MAX_IMAGEN
    for _ in range(6):
        copia = imagen.copy()
        copia.thumbnail((lado, lado))
        for calidad in (85, 75, 65):
            salida = BytesIO()
            copia.save(salida, format="WEBP", quality=calidad, method=4)
            if salida.tell() <= TAMANO_MAX_IMAGEN:
                return salida.getvalue(), "image/webp"
        lado = int(lado * 0.75)

    raise ValueError("No se pudo reducir la imagen lo suficiente, prueba con otra")


def _leer_imagen(archivo):
    """Valida y lee un archivo subido (werkzeug FileStorage). Devuelve (bytes, mime) o (None, None)."""
    if archivo is None or not archivo.filename:
        return None, None
    if archivo.mimetype not in TIPOS_IMAGEN_PERMITIDOS:
        raise ValueError("Formato de imagen no soportado (usa JPG, PNG, WEBP o GIF)")

    datos = archivo.read()
    if not datos:
        raise ValueError("El archivo de imagen está vacío")

    # las imagenes pequenas se guardan tal cual (asi un GIF animado sigue animado)
    if len(datos) <= TAMANO_MAX_IMAGEN:
        try:
            Image.open(BytesIO(datos)).verify()
        except (UnidentifiedImageError, OSError):
            raise ValueError("El archivo no es una imagen válida")
        return datos, archivo.mimetype

    return _optimizar_imagen(datos)


def _cerrar(conexion):
    """Cierra la conexion aunque MySQL ya la haya cortado."""
    try:
        conexion.close()
    except pymysql.err.Error:
        pass


ERROR_GUARDAR_IMAGEN = (
    "No se pudo guardar en la base de datos. Si subiste una imagen, "
    "prueba con una más liviana"
)


def _error_integridad_producto(error):
    """Mensaje para el admin cuando MySQL rechaza el producto: la
    referencia es unica (1062) y la categoria/marca deben existir.
    """
    if error.args and error.args[0] == 1062:
        return "No se pudo asignar la referencia automática. Inténtalo de nuevo."
    return "La categoría o la marca elegida ya no existe. Recarga la página e inténtalo de nuevo."


def _referencia_automatica(producto_id):
    """REF + id del producto con al menos 3 cifras (REF001, REF018,
    REF1250). Va atada al id, asi que es unica y nunca se repite.
    """
    return "REF{:03d}".format(producto_id)


def crear_producto(datos, archivo_imagen=None):
    descuento = _leer_descuento(datos)
    imagen, imagen_mime = _leer_imagen(archivo_imagen)

    conexion = conectar()
    cursor = conexion.cursor()
    try:
        # la referencia sale del id, que solo se conoce al insertar: se
        # guarda sin ella y se completa en la misma transaccion
        cursor.execute(
            """
            INSERT INTO productos (nombre, descripcion, categoria_id, marca_id, estado, descuento, imagen, imagen_mime)
            VALUES (%s, %s, %s, %s, 'activo', %s, %s, %s)
            """,
            (
                datos["nombre"],
                datos.get("descripcion", ""),
                datos["categoria_id"],
                datos["marca_id"],
                descuento,
                imagen,
                imagen_mime,
            ),
        )
        producto_id = cursor.lastrowid
        cursor.execute(
            "UPDATE productos SET referencia=%s WHERE id=%s",
            (_referencia_automatica(producto_id), producto_id),
        )
        conexion.commit()
    except pymysql.err.IntegrityError as error:
        conexion.rollback()
        raise ValueError(_error_integridad_producto(error))
    except pymysql.err.OperationalError:
        raise ValueError(ERROR_GUARDAR_IMAGEN)
    finally:
        _cerrar(conexion)


def actualizar_producto(id, datos, archivo_imagen=None):
    # la referencia no se toca: es automatica y los SKU de las tallas
    # (<referencia>-<talla>) se armaron con ella
    descuento = _leer_descuento(datos)
    imagen, imagen_mime = _leer_imagen(archivo_imagen)

    conexion = conectar()
    cursor = conexion.cursor()
    try:
        if imagen is not None:
            cursor.execute(
                """
                UPDATE productos
                SET nombre=%s, descripcion=%s, categoria_id=%s, marca_id=%s,
                    estado=%s, descuento=%s, imagen=%s, imagen_mime=%s
                WHERE id=%s
                """,
                (
                    datos["nombre"],
                    datos.get("descripcion", ""),
                    datos["categoria_id"],
                    datos["marca_id"],
                    datos.get("estado", "activo"),
                    descuento,
                    imagen,
                    imagen_mime,
                    id,
                ),
            )
        else:
            cursor.execute(
                """
                UPDATE productos
                SET nombre=%s, descripcion=%s, categoria_id=%s, marca_id=%s,
                    estado=%s, descuento=%s
                WHERE id=%s
                """,
                (
                    datos["nombre"],
                    datos.get("descripcion", ""),
                    datos["categoria_id"],
                    datos["marca_id"],
                    datos.get("estado", "activo"),
                    descuento,
                    id,
                ),
            )
        conexion.commit()
    except pymysql.err.IntegrityError as error:
        conexion.rollback()
        raise ValueError(_error_integridad_producto(error))
    except pymysql.err.OperationalError:
        raise ValueError(ERROR_GUARDAR_IMAGEN)
    finally:
        _cerrar(conexion)


def eliminar_producto(id):
    """Elimina un producto y devuelve un mensaje para el admin.

    - Sin ventas: se borra con sus tallas, sus fotos extra y las lineas
      que tuviera en carritos.
    - Con ventas: borrarlo dañaria las facturas y el historial de
      pedidos (detalle_factura apunta a sus existencias), asi que se
      desactiva: sale de la tienda y de los carritos, y se puede volver
      a activar desde Editar.
    """
    conexion = conectar()
    cursor = conexion.cursor()
    try:
        cursor.execute("SELECT nombre FROM productos WHERE id=%s FOR UPDATE", (id,))
        producto = cursor.fetchone()
        if not producto:
            raise ValueError("Ese producto ya no existe")

        cursor.execute(
            """
            SELECT COUNT(*) AS ventas FROM detalle_factura df
            JOIN existencias e ON e.id = df.existencia_id
            WHERE e.producto_id = %s
            """,
            (id,),
        )
        ventas = cursor.fetchone()["ventas"]

        # en ambos casos deja de estar en los carritos
        cursor.execute(
            """
            DELETE dc FROM detalle_carrito dc
            JOIN existencias e ON e.id = dc.existencia_id
            WHERE e.producto_id = %s
            """,
            (id,),
        )

        if ventas:
            cursor.execute("UPDATE productos SET estado='inactivo' WHERE id=%s", (id,))
            conexion.commit()
            return (
                '"{}" tiene {} {} en facturas, así que no se puede borrar sin dañar '
                "el historial. Lo desactivé: ya no aparece en la tienda (puedes "
                "reactivarlo desde Editar)."
            ).format(producto["nombre"], ventas, "venta" if ventas == 1 else "ventas")

        cursor.execute("DELETE FROM existencias WHERE producto_id=%s", (id,))
        cursor.execute("DELETE FROM imagenes_producto WHERE producto_id=%s", (id,))
        cursor.execute("DELETE FROM productos WHERE id=%s", (id,))
        conexion.commit()
        return '"{}" se eliminó.'.format(producto["nombre"])
    except ValueError:
        conexion.rollback()
        raise
    except pymysql.err.IntegrityError:
        conexion.rollback()
        raise ValueError("No se pudo eliminar el producto: otros registros dependen de él")
    finally:
        conexion.close()


# =========================
# INVENTARIO (Admin)
# =========================


def listar_existencias_producto(producto_id):
    conexion = conectar()
    cursor = conexion.cursor()
    cursor.execute(
        """
        SELECT e.id, e.precio, e.stock, e.estado,
               t.nombre AS talla
        FROM existencias e
        JOIN tallas t ON t.id = e.talla_id
        WHERE e.producto_id = %s
        ORDER BY t.id
        """,
        (producto_id,),
    )
    existencias = cursor.fetchall()
    conexion.close()
    return existencias


def listar_inventario():
    """Inventario completo: cada existencia (producto + talla) con
    su stock, para el reporte de "consultar inventario completo".
    """
    conexion = conectar()
    cursor = conexion.cursor()
    cursor.execute(
        """
        SELECT e.id, p.nombre AS producto_nombre, p.referencia,
               t.nombre AS talla, e.precio, e.stock, e.estado
        FROM existencias e
        JOIN productos p ON p.id = e.producto_id
        JOIN tallas t ON t.id = e.talla_id
        ORDER BY p.nombre, t.id
        """
    )
    inventario = cursor.fetchall()
    conexion.close()
    return inventario


def crear_existencia(datos):
    """Agrega stock de una talla a un producto y devuelve un mensaje para
    el admin.

    - Si el producto aun no tiene esa talla, la crea (una existencia
      nueva) con su precio y stock inicial; el SKU es <referencia>-<talla>.
    - Si ya la tiene, suma las unidades a su stock y deja el precio como
      estaba (asi no se cambia un precio sin querer).
    """
    try:
        producto_id = int(datos.get("producto_id", ""))
        talla_id = int(datos.get("talla_id", ""))
        stock = int(datos.get("stock", "0") or 0)
    except ValueError:
        raise ValueError("Elige producto y talla, y escribe las unidades con un número entero")
    stock = max(0, stock)

    texto_precio = str(datos.get("precio", "") or "").strip()
    try:
        precio = float(texto_precio) if texto_precio else None
    except ValueError:
        raise ValueError("El precio debe ser un número")

    conexion = conectar()
    cursor = conexion.cursor()
    try:
        cursor.execute(
            """
            SELECT p.referencia, t.nombre AS talla
            FROM productos p JOIN tallas t ON t.id = %s
            WHERE p.id = %s
            """,
            (talla_id, producto_id),
        )
        producto = cursor.fetchone()
        if not producto:
            raise ValueError("El producto o la talla no existen")

        cursor.execute(
            "SELECT id, stock, precio FROM existencias WHERE producto_id=%s AND talla_id=%s FOR UPDATE",
            (producto_id, talla_id),
        )
        existencia = cursor.fetchone()

        if existencia:
            if stock <= 0:
                raise ValueError(
                    "La talla {} ya existe con {} unidades: escribe cuántas unidades quieres sumar".format(
                        producto["talla"], existencia["stock"]
                    )
                )
            total = existencia["stock"] + stock
            cursor.execute(
                "UPDATE existencias SET stock=%s, estado=IF(%s > 0, 'activo', 'agotado') WHERE id=%s",
                (total, total, existencia["id"]),
            )
            conexion.commit()
            return "Se {} a la talla {}: ahora hay {} (precio sin cambios: $ {:,.0f}).".format(
                "sumó 1 unidad" if stock == 1 else "sumaron {} unidades".format(stock),
                producto["talla"],
                total,
                existencia["precio"],
            )

        if precio is None or precio <= 0:
            raise ValueError(
                "La talla {} es nueva para este producto: indica su precio (mayor a 0)".format(producto["talla"])
            )
        cursor.execute(
            """
            INSERT INTO existencias (producto_id, talla_id, sku, precio, stock, estado)
            VALUES (%s, %s, %s, %s, %s, IF(%s > 0, 'activo', 'agotado'))
            """,
            (
                producto_id,
                talla_id,
                "{}-{}".format(producto["referencia"], producto["talla"]) if producto["referencia"] else None,
                precio,
                stock,
                stock,
            ),
        )
        conexion.commit()
        return "Talla {} agregada con {} unidades a $ {:,.0f}.".format(producto["talla"], stock, precio)
    except ValueError:
        conexion.rollback()
        raise
    except pymysql.err.IntegrityError as error:
        conexion.rollback()
        if error.args and error.args[0] == 1062:
            # el SKU tambien es unico: otro producto ya usa <referencia>-<talla>
            raise ValueError("No se pudo crear la talla: ya existe otra existencia con ese SKU")
        # p. ej. una base vieja que aun exige color en existencias
        raise ValueError(
            "La base de datos rechazó la talla ({}). Puede que tu base esté "
            "desactualizada: importa database/BD/urbanstyle.sql".format(error.args[-1])
        )
    finally:
        conexion.close()


def actualizar_stock_existencia(existencia_id, stock):
    """Actualiza el stock de una existencia puntual (producto+talla).

    Si el stock queda en 0 la marca como 'agotado'; si vuelve a haber
    stock la reactiva, igual que hace la venta al descontar (ver
    `orders_service._descontar_stock`).
    """
    stock = max(0, int(stock))

    conexion = conectar()
    cursor = conexion.cursor()
    cursor.execute(
        "UPDATE existencias SET stock=%s, estado=IF(%s > 0, 'activo', 'agotado') WHERE id=%s",
        (stock, stock, existencia_id),
    )
    conexion.commit()
    conexion.close()
