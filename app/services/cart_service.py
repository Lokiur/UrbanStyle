from database.init_db import conectar


def obtener_items(user_id):
    conexion = conectar()
    cursor = conexion.cursor()
    cursor.execute(
        """
        SELECT dc.id AS detalle_id, dc.cantidad, e.id AS existencia_id, e.precio,
               p.id AS producto_id, p.nombre AS producto_nombre,
               t.nombre AS talla,
               (e.precio * dc.cantidad) AS subtotal,
               (p.imagen IS NOT NULL) AS tiene_imagen
        FROM carrito c
        JOIN detalle_carrito dc ON dc.carrito_id = c.id
        JOIN existencias e ON e.id = dc.existencia_id
        JOIN productos p ON p.id = e.producto_id
        JOIN tallas t ON t.id = e.talla_id
        WHERE c.user_id = %s
        ORDER BY dc.id
        """,
        (user_id,),
    )
    items = cursor.fetchall()
    conexion.close()
    return items


def contar_items(user_id):
    conexion = conectar()
    cursor = conexion.cursor()
    cursor.execute(
        """
        SELECT COALESCE(SUM(dc.cantidad), 0) AS total
        FROM carrito c
        JOIN detalle_carrito dc ON dc.carrito_id = c.id
        WHERE c.user_id = %s
        """,
        (user_id,),
    )
    row = cursor.fetchone()
    conexion.close()
    return row["total"] if row else 0


def agregar(user_id, producto_id, existencia_id=None):
    """Agrega al carrito una unidad de la talla pedida (existencia_id).
    Nunca la sustituye por otra talla en silencio: si esa talla ya no
    tiene stock, o el carrito ya tiene todo el stock disponible, devuelve
    un error en vez de agregar cualquier cosa.
    """
    conexion = conectar()
    cursor = conexion.cursor()

    if existencia_id:
        cursor.execute(
            """
            SELECT id, stock FROM existencias
            WHERE id=%s AND producto_id=%s AND estado='activo' AND stock>0
            """,
            (existencia_id, producto_id),
        )
    else:
        # no llego ninguna talla (ej. todas se mostraban deshabilitadas):
        # se ofrece cualquier existencia disponible del producto
        cursor.execute(
            """
            SELECT id, stock FROM existencias
            WHERE producto_id=%s AND estado='activo' AND stock>0
            ORDER BY precio ASC LIMIT 1
            """,
            (producto_id,),
        )
    existencia = cursor.fetchone()

    if not existencia:
        conexion.close()
        return {"ok": False, "error": "Esa talla ya no tiene stock disponible."}

    cursor.execute(
        "SELECT id FROM carrito WHERE user_id=%s ORDER BY id DESC LIMIT 1",
        (user_id,),
    )
    carrito = cursor.fetchone()

    if carrito:
        carrito_id = carrito["id"]
    else:
        cursor.execute("INSERT INTO carrito (user_id) VALUES (%s)", (user_id,))
        carrito_id = cursor.lastrowid

    cursor.execute(
        "SELECT id, cantidad FROM detalle_carrito WHERE carrito_id=%s AND existencia_id=%s",
        (carrito_id, existencia["id"]),
    )
    detalle = cursor.fetchone()

    if detalle and detalle["cantidad"] >= existencia["stock"]:
        conexion.rollback()
        conexion.close()
        return {
            "ok": False,
            "error": "Ya tienes en la bolsa todas las unidades disponibles de esa talla.",
        }

    if detalle:
        cursor.execute(
            "UPDATE detalle_carrito SET cantidad = cantidad + 1 WHERE id=%s",
            (detalle["id"],),
        )
    else:
        cursor.execute(
            """
            INSERT INTO detalle_carrito (carrito_id, existencia_id, cantidad)
            VALUES (%s, %s, 1)
            """,
            (carrito_id, existencia["id"]),
        )

    conexion.commit()
    conexion.close()
    return {"ok": True}


def sumar(user_id, detalle_id):
    """Suma una unidad, sin pasar del stock disponible de esa talla."""
    conexion = conectar()
    cursor = conexion.cursor()
    cursor.execute(
        """
        UPDATE detalle_carrito dc
        JOIN carrito c ON c.id = dc.carrito_id
        JOIN existencias e ON e.id = dc.existencia_id
        SET dc.cantidad = dc.cantidad + 1
        WHERE dc.id=%s AND c.user_id=%s AND dc.cantidad < e.stock
        """,
        (detalle_id, user_id),
    )
    conexion.commit()
    conexion.close()


def restar(user_id, detalle_id):
    conexion = conectar()
    cursor = conexion.cursor()
    cursor.execute(
        """
        SELECT dc.id, dc.cantidad FROM detalle_carrito dc
        JOIN carrito c ON c.id = dc.carrito_id
        WHERE dc.id=%s AND c.user_id=%s
        """,
        (detalle_id, user_id),
    )
    detalle = cursor.fetchone()

    if detalle:
        if detalle["cantidad"] <= 1:
            cursor.execute("DELETE FROM detalle_carrito WHERE id=%s", (detalle_id,))
        else:
            cursor.execute(
                "UPDATE detalle_carrito SET cantidad = cantidad - 1 WHERE id=%s",
                (detalle_id,),
            )
        conexion.commit()

    conexion.close()


def eliminar(user_id, detalle_id):
    conexion = conectar()
    cursor = conexion.cursor()
    cursor.execute(
        """
        DELETE dc FROM detalle_carrito dc
        JOIN carrito c ON c.id = dc.carrito_id
        WHERE dc.id=%s AND c.user_id=%s
        """,
        (detalle_id, user_id),
    )
    conexion.commit()
    conexion.close()
