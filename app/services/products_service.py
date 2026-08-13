import pymysql

from database.init_db import conectar


def _consultar_productos(cursor, condicion="", parametros=()):
    sql = """
        SELECT p.*,
               MIN(e.precio) AS precio_desde,
               COALESCE(SUM(e.stock), 0) AS stock_total,
               i.imagen AS imagen
        FROM productos p
        LEFT JOIN existencias e ON e.producto_id = p.id AND e.estado = 'activo'
        LEFT JOIN imagenes_producto i ON i.producto_id = p.id AND i.principal = 1
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
        SELECT p.*, c.nombre AS categoria_nombre, m.nombre AS marca_nombre
        FROM productos p
        JOIN categorias c ON c.id = p.categoria_id
        JOIN marcas m ON m.id = p.marca_id
        """
    )
    productos = cursor.fetchall()
    conexion.close()
    return productos


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


def crear_producto(datos):
    conexion = conectar()
    cursor = conexion.cursor()
    cursor.execute(
        """
        INSERT INTO productos (referencia, nombre, descripcion, categoria_id, marca_id, estado)
        VALUES (%s, %s, %s, %s, %s, 'activo')
        """,
        (
            datos["referencia"],
            datos["nombre"],
            datos.get("descripcion", ""),
            datos["categoria_id"],
            datos["marca_id"],
        ),
    )
    conexion.commit()
    conexion.close()


def actualizar_producto(id, datos):
    conexion = conectar()
    cursor = conexion.cursor()
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
