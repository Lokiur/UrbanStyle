import pymysql

from database.init_db import conectar


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
        condiciones.append("e.precio >= %s")
        parametros.append(precio_min)
    if precio_max:
        condiciones.append("e.precio <= %s")
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

    sql = """
        SELECT p.id, p.referencia, p.nombre, p.descripcion, p.categoria_id,
               p.marca_id, p.estado, p.created_at, p.updated_at,
               (p.imagen IS NOT NULL) AS tiene_imagen,
               MIN(e.precio) AS precio_desde,
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
    sql += " GROUP BY p.id"
    cursor.execute(sql, parametros)
    productos = cursor.fetchall()

    if not productos:
        return productos

    ids = [p["id"] for p in productos]
    formato = ",".join(["%s"] * len(ids))
    sql_tallas = f"""
        SELECT e.id AS existencia_id, e.producto_id, e.precio, e.stock,
               t.id AS talla_id, t.nombre AS talla
        FROM existencias e
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
        # una talla puede tener varios colores: nos quedamos con la primera
        # existencia (la de menor precio, por el ORDER BY) por cada talla
        vistas.setdefault(
            fila["talla_id"],
            {
                "talla_id": fila["talla_id"],
                "nombre": fila["talla"],
                "existencia_id": fila["existencia_id"],
                "precio": fila["precio"],
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
               p.marca_id, p.estado, p.created_at, p.updated_at,
               (p.imagen IS NOT NULL) AS tiene_imagen,
               c.nombre AS categoria_nombre, m.nombre AS marca_nombre
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
        "SELECT id, nombre, (imagen IS NOT NULL) AS tiene_imagen FROM categorias"
    )
    categorias = cursor.fetchall()
    conexion.close()
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
    finally:
        conexion.close()


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
    finally:
        conexion.close()


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


def _leer_imagen(archivo):
    """Valida y lee un archivo subido (werkzeug FileStorage). Devuelve (bytes, mime) o (None, None)."""
    if archivo is None or not archivo.filename:
        return None, None
    if archivo.mimetype not in TIPOS_IMAGEN_PERMITIDOS:
        raise ValueError("Formato de imagen no soportado (usa JPG, PNG, WEBP o GIF)")
    return archivo.read(), archivo.mimetype


def crear_producto(datos, archivo_imagen=None):
    imagen, imagen_mime = _leer_imagen(archivo_imagen)

    conexion = conectar()
    cursor = conexion.cursor()
    cursor.execute(
        """
        INSERT INTO productos (referencia, nombre, descripcion, categoria_id, marca_id, estado, imagen, imagen_mime)
        VALUES (%s, %s, %s, %s, %s, 'activo', %s, %s)
        """,
        (
            datos["referencia"],
            datos["nombre"],
            datos.get("descripcion", ""),
            datos["categoria_id"],
            datos["marca_id"],
            imagen,
            imagen_mime,
        ),
    )
    conexion.commit()
    conexion.close()


def actualizar_producto(id, datos, archivo_imagen=None):
    imagen, imagen_mime = _leer_imagen(archivo_imagen)

    conexion = conectar()
    cursor = conexion.cursor()
    if imagen is not None:
        cursor.execute(
            """
            UPDATE productos
            SET referencia=%s, nombre=%s, descripcion=%s, categoria_id=%s, marca_id=%s,
                estado=%s, imagen=%s, imagen_mime=%s
            WHERE id=%s
            """,
            (
                datos["referencia"],
                datos["nombre"],
                datos.get("descripcion", ""),
                datos["categoria_id"],
                datos["marca_id"],
                datos.get("estado", "activo"),
                imagen,
                imagen_mime,
                id,
            ),
        )
    else:
        cursor.execute(
            """
            UPDATE productos
            SET referencia=%s, nombre=%s, descripcion=%s, categoria_id=%s, marca_id=%s, estado=%s
            WHERE id=%s
            """,
            (
                datos["referencia"],
                datos["nombre"],
                datos.get("descripcion", ""),
                datos["categoria_id"],
                datos["marca_id"],
                datos.get("estado", "activo"),
                id,
            ),
        )
    conexion.commit()
    conexion.close()


def eliminar_producto(id):
    conexion = conectar()
    cursor = conexion.cursor()
    try:
        cursor.execute("DELETE FROM productos WHERE id=%s", (id,))
        conexion.commit()
    except pymysql.err.IntegrityError:
        conexion.rollback()
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
               t.nombre AS talla, c.nombre AS color
        FROM existencias e
        JOIN tallas t ON t.id = e.talla_id
        JOIN colores c ON c.id = e.color_id
        WHERE e.producto_id = %s
        ORDER BY t.id, c.nombre
        """,
        (producto_id,),
    )
    existencias = cursor.fetchall()
    conexion.close()
    return existencias


def listar_inventario():
    """Inventario completo: cada existencia (producto + talla + color) con
    su stock, para el reporte de "consultar inventario completo".
    """
    conexion = conectar()
    cursor = conexion.cursor()
    cursor.execute(
        """
        SELECT e.id, p.nombre AS producto_nombre, p.referencia,
               t.nombre AS talla, c.nombre AS color, e.precio, e.stock, e.estado
        FROM existencias e
        JOIN productos p ON p.id = e.producto_id
        JOIN tallas t ON t.id = e.talla_id
        JOIN colores c ON c.id = e.color_id
        ORDER BY p.nombre, t.id, c.nombre
        """
    )
    inventario = cursor.fetchall()
    conexion.close()
    return inventario


def actualizar_stock_existencia(existencia_id, stock):
    """Actualiza el stock de una existencia puntual (producto+talla+color).

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
