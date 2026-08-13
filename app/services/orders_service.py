from decimal import Decimal

from database.init_db import conectar
from app.services import cart_service

ENVIO_COSTO = Decimal("12000")
IVA_PORCENTAJE = Decimal("0.19")


def obtener_pedidos(user_id):
    conexion = conectar()
    cursor = conexion.cursor()
    cursor.execute(
        "SELECT * FROM facturas WHERE user_id=%s ORDER BY fecha DESC",
        (user_id,),
    )
    pedidos = cursor.fetchall()
    conexion.close()
    return pedidos


def obtener_direcciones(user_id):
    conexion = conectar()
    cursor = conexion.cursor()
    cursor.execute(
        "SELECT * FROM direcciones WHERE user_id=%s ORDER BY principal DESC, id",
        (user_id,),
    )
    direcciones = cursor.fetchall()
    conexion.close()
    return direcciones


def obtener_metodos_pago():
    conexion = conectar()
    cursor = conexion.cursor()
    cursor.execute(
        "SELECT * FROM metodos_pago WHERE estado='activo' AND nombre<>'Efectivo' ORDER BY nombre"
    )
    metodos_pago = cursor.fetchall()
    conexion.close()
    return metodos_pago


def calcular_totales(items):
    subtotal = sum((item["subtotal"] for item in items), Decimal("0"))
    iva = subtotal * IVA_PORCENTAJE
    envio = ENVIO_COSTO if items else Decimal("0")
    total = subtotal + iva + envio
    return subtotal, iva, envio, total


def crear_pedido(user_id, direccion_form, metodo_pago_id):
    """Confirma el carrito del usuario como un pedido (factura).

    `direccion_form` es el form completo de la request: si trae
    direccion_id="nueva" se crea una direccion nueva con los campos
    direccion/ciudad/departamento/codigo_postal; si trae un id, se
    reutiliza una direccion existente del usuario.

    Devuelve el id de la factura creada, o None si la operacion no
    pudo completarse (carrito vacio, datos invalidos).
    """
    items = cart_service.obtener_items(user_id)

    if not items:
        return None

    conexion = conectar()
    cursor = conexion.cursor()

    direccion_raw = direccion_form.get("direccion_id", "")

    if direccion_raw == "nueva":
        direccion_txt = direccion_form.get("direccion", "").strip()
        ciudad = direccion_form.get("ciudad", "").strip()
        departamento = direccion_form.get("departamento", "").strip()
        codigo_postal = direccion_form.get("codigo_postal", "").strip()

        if not direccion_txt or not ciudad:
            conexion.close()
            return None

        # nota: la tabla `direcciones` tiene un trigger BEFORE INSERT que
        # falla con error 1442 si se inserta con principal=1 (bug del propio
        # trigger, reproducible incluso desde un INSERT plano fuera de esta
        # app), por lo que las direcciones nuevas siempre entran con
        # principal=0.
        cursor.execute(
            """
            INSERT INTO direcciones (user_id, direccion, ciudad, departamento, codigo_postal, principal)
            VALUES (%s, %s, %s, %s, %s, 0)
            """,
            (user_id, direccion_txt, ciudad, departamento or None, codigo_postal or None),
        )
        direccion_id = cursor.lastrowid
    else:
        direccion_id = int(direccion_raw) if direccion_raw.isdigit() else None
        if direccion_id:
            cursor.execute(
                "SELECT id FROM direcciones WHERE id=%s AND user_id=%s",
                (direccion_id, user_id),
            )
            if not cursor.fetchone():
                direccion_id = None

    if not direccion_id or not metodo_pago_id:
        conexion.close()
        return None

    subtotal, iva, envio, total = calcular_totales(items)

    cursor.execute(
        """
        INSERT INTO facturas
        (user_id, direccion_id, metodo_pago_id, subtotal, iva, envio, total, estado)
        VALUES (%s, %s, %s, %s, %s, %s, %s, 'activa')
        """,
        (user_id, direccion_id, metodo_pago_id, subtotal, iva, envio, total),
    )
    factura_id = cursor.lastrowid

    numero_factura = f"FAC-{factura_id:04d}"
    cursor.execute(
        "UPDATE facturas SET numero_factura=%s WHERE id=%s",
        (numero_factura, factura_id),
    )

    for item in items:
        cursor.execute(
            """
            INSERT INTO detalle_factura (factura_id, existencia_id, cantidad, precio_unitario, subtotal)
            VALUES (%s, %s, %s, %s, %s)
            """,
            (factura_id, item["existencia_id"], item["cantidad"], item["precio"], item["subtotal"]),
        )

    cursor.execute(
        """
        DELETE dc FROM detalle_carrito dc
        JOIN carrito c ON c.id = dc.carrito_id
        WHERE c.user_id=%s
        """,
        (user_id,),
    )

    conexion.commit()
    conexion.close()

    return factura_id
