import pymysql

from database.init_db import conectar


def _consultar_productos(cursor, condicion="", parametros=()):
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
    if condicion:
        sql += f" AND {condicion}"
    sql += " GROUP BY p.id"
    cursor.execute(sql, parametros)
    productos = cursor.fetchall()

    if not productos:
        return productos

    ids = [p["id"] for p in productos]
    formato = ",".join(["%s"] * len(ids))
    cursor.execute(
        f"""
        SELECT e.id AS existencia_id, e.producto_id, e.precio, e.stock,
               t.id AS talla_id, t.nombre AS talla
        FROM existencias e
        JOIN tallas t ON t.id = e.talla_id
        WHERE e.producto_id IN ({formato}) AND e.estado = 'activo'
        ORDER BY t.id, e.precio ASC
        """,
        ids,
    )

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


def obtener_productos():
    conexion = conectar()
    cursor = conexion.cursor()
    productos = _consultar_productos(cursor)
    conexion.close()
    return productos


def obtener_categoria(id):
    conexion = conectar()
    cursor = conexion.cursor()
    productos = _consultar_productos(cursor, "p.categoria_id = %s", (id,))
    conexion.close()
    return productos


def buscar_productos(query):
    if not query:
        return []

    conexion = conectar()
    cursor = conexion.cursor()
    like = f"%{query}%"
    productos = _consultar_productos(
        cursor, "(p.nombre LIKE %s OR p.descripcion LIKE %s)", (like, like)
    )
    conexion.close()
    return productos


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
    cursor.execute("SELECT * FROM categorias")
    categorias = cursor.fetchall()
    conexion.close()
    return categorias


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
