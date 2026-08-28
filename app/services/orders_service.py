import hashlib
import hmac
import re
from datetime import date, datetime, timedelta
from decimal import Decimal

from flask import current_app

from database.init_db import conectar
from app.services import cart_service

ENVIO_COSTO = Decimal("12000")
IVA_PORCENTAJE = Decimal("0.19")

# flujo de un pedido: pendiente -> preparacion -> enviado -> entregado, o
# pendiente/preparacion/enviado -> anulado. entregado y anulado son
# estados finales.
TRANSICIONES_ADMIN = {
    "pendiente": ("preparacion", "anulado"),
    "preparacion": ("enviado", "anulado"),
    "enviado": ("entregado", "anulado"),
    "entregado": (),
    "anulado": (),
}

# orden de las etapas de envio para pintar la linea de tiempo en "Mis
# Pedidos" (no incluye "anulado", que es un estado aparte, no un paso).
ETAPAS_ENVIO = ["pendiente", "preparacion", "enviado", "entregado"]

ETAPAS_ENVIO_LABELS = {
    "pendiente": "Pedido recibido",
    "preparacion": "En preparación",
    "enviado": "Enviado",
    "entregado": "Entregado",
}

# minutos que tiene el cliente, desde que paga, para cancelar su propio
# pedido (solo si sigue "pendiente", es decir, aun no se ha despachado).
VENTANA_CANCELACION_CLIENTE_MINUTOS = 30


def numero_autorizacion(pago_id):
    """Numero de autorizacion de un pago.

    No se guarda en `pagos` (la tabla no tiene columna para el), se
    deriva del id del pago firmandolo con la secret_key de la app. El
    resultado se ve aleatorio pero siempre es el mismo para el mismo
    pago, asi se puede volver a mostrar en "Mis Pedidos" y en la factura
    en PDF sin tocar el esquema de la base de datos.
    """
    firma = hmac.new(
        current_app.secret_key.encode(),
        str(pago_id).encode(),
        hashlib.sha256,
    ).hexdigest()

    return "AUT-{:08d}".format(int(firma[:12], 16) % 100000000)


def obtener_pedidos(user_id):
    conexion = conectar()
    cursor = conexion.cursor()
    cursor.execute(
        """
        SELECT f.*,
               (SELECT MAX(p.id) FROM pagos p WHERE p.factura_id = f.id) AS pago_id,
               TIMESTAMPDIFF(MINUTE, f.fecha, NOW()) AS minutos_transcurridos
        FROM facturas f
        WHERE f.user_id=%s
        ORDER BY f.fecha DESC
        """,
        (user_id,),
    )
    pedidos = cursor.fetchall()
    conexion.close()

    for pedido in pedidos:
        pedido["numero_autorizacion"] = (
            numero_autorizacion(pedido["pago_id"]) if pedido["pago_id"] else None
        )

    return pedidos


def listar_pedidos():
    conexion = conectar()
    cursor = conexion.cursor()
    cursor.execute(
        """
        SELECT f.*, u.username AS cliente_usuario,
               u.name AS cliente_nombre, u.apellidos AS cliente_apellidos
        FROM facturas f
        JOIN users u ON u.id = f.user_id
        ORDER BY f.fecha DESC
        """
    )
    pedidos = cursor.fetchall()
    conexion.close()
    return pedidos


def _condicion_periodo(fecha_inicio, fecha_fin, alias):
    """Arma el WHERE de un reporte de ventas: excluye anulados y, si se
    dan, acota por fecha (inclusive en ambos extremos).

    Devuelve (sql_where, parametros) para usar con `.format()` + cursor.
    """
    condiciones = ["{}.estado != 'anulado'".format(alias)]
    parametros = []

    if fecha_inicio:
        condiciones.append("{}.fecha >= %s".format(alias))
        parametros.append(fecha_inicio + " 00:00:00")

    if fecha_fin:
        condiciones.append("{}.fecha <= %s".format(alias))
        parametros.append(fecha_fin + " 23:59:59")

    return " AND ".join(condiciones), parametros


def resumen_ventas_periodo(fecha_inicio=None, fecha_fin=None):
    """Total vendido y cantidad de pedidos (no anulados) en un rango de
    fechas. Sin fecha_inicio/fecha_fin no hay limite en ese extremo.
    """
    where, parametros = _condicion_periodo(fecha_inicio, fecha_fin, "facturas")

    conexion = conectar()
    cursor = conexion.cursor()
    cursor.execute(
        """
        SELECT COUNT(*) AS cantidad, COALESCE(SUM(total), 0) AS total
        FROM facturas
        WHERE {}
        """.format(where),
        parametros,
    )
    resumen = cursor.fetchone()
    conexion.close()
    return resumen


def ventas_por_metodo_pago(fecha_inicio=None, fecha_fin=None):
    """Ventas (no anuladas) agrupadas por metodo de pago, de mayor a menor."""
    where, parametros = _condicion_periodo(fecha_inicio, fecha_fin, "f")

    conexion = conectar()
    cursor = conexion.cursor()
    cursor.execute(
        """
        SELECT mp.nombre AS etiqueta,
               COUNT(*) AS cantidad,
               COALESCE(SUM(f.total), 0) AS total
        FROM facturas f
        JOIN metodos_pago mp ON mp.id = f.metodo_pago_id
        WHERE {}
        GROUP BY mp.id, mp.nombre
        ORDER BY total DESC
        """.format(where),
        parametros,
    )
    filas = cursor.fetchall()
    conexion.close()
    return filas


def ventas_por_ciudad(fecha_inicio=None, fecha_fin=None):
    """Ventas (no anuladas) agrupadas por ciudad/departamento de envio,
    de mayor a menor.
    """
    where, parametros = _condicion_periodo(fecha_inicio, fecha_fin, "f")

    conexion = conectar()
    cursor = conexion.cursor()
    cursor.execute(
        """
        SELECT COALESCE(NULLIF(d.ciudad, ''), 'Sin ciudad') AS ciudad,
               d.departamento,
               COUNT(*) AS cantidad,
               COALESCE(SUM(f.total), 0) AS total
        FROM facturas f
        JOIN direcciones d ON d.id = f.direccion_id
        WHERE {}
        GROUP BY d.ciudad, d.departamento
        ORDER BY total DESC
        """.format(where),
        parametros,
    )
    filas = cursor.fetchall()
    conexion.close()
    return filas


MESES_ES = [
    "Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio",
    "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre",
]


def comparativo_ventas_mes_actual():
    """Compara las ventas (no anuladas) del mes calendario en curso con
    las del mes anterior: total facturado, cantidad de pedidos y
    variacion porcentual.

    No depende del filtro de periodo del panel; siempre toma el mes en
    curso segun la fecha de hoy.
    """
    hoy = date.today()
    inicio_mes_actual = hoy.replace(day=1)
    inicio_mes_anterior = (inicio_mes_actual - timedelta(days=1)).replace(day=1)

    conexion = conectar()
    cursor = conexion.cursor()
    cursor.execute(
        """
        SELECT
            COALESCE(SUM(CASE WHEN fecha >= %s THEN total END), 0) AS total_actual,
            COUNT(CASE WHEN fecha >= %s THEN 1 END) AS cantidad_actual,
            COALESCE(SUM(CASE WHEN fecha < %s THEN total END), 0) AS total_anterior,
            COUNT(CASE WHEN fecha < %s THEN 1 END) AS cantidad_anterior
        FROM facturas
        WHERE estado != 'anulado' AND fecha >= %s
        """,
        (
            inicio_mes_actual,
            inicio_mes_actual,
            inicio_mes_actual,
            inicio_mes_actual,
            inicio_mes_anterior,
        ),
    )
    fila = cursor.fetchone()
    conexion.close()

    total_actual = float(fila["total_actual"])
    total_anterior = float(fila["total_anterior"])
    diferencia = total_actual - total_anterior
    variacion_pct = (diferencia / total_anterior * 100) if total_anterior else None

    return {
        "mes_actual_label": "{} {}".format(
            MESES_ES[inicio_mes_actual.month - 1], inicio_mes_actual.year
        ),
        "mes_anterior_label": "{} {}".format(
            MESES_ES[inicio_mes_anterior.month - 1], inicio_mes_anterior.year
        ),
        "total_actual": total_actual,
        "total_anterior": total_anterior,
        "cantidad_actual": fila["cantidad_actual"],
        "cantidad_anterior": fila["cantidad_anterior"],
        "diferencia": diferencia,
        "variacion_pct": variacion_pct,
    }


def ingresos_envio_por_empresa(fecha_inicio=None, fecha_fin=None):
    """Ingresos por costos de envio agrupados por empresa transportadora.

    Suma `envios.costo_envio` de los envios cuya factura no esta anulada,
    acotado por la fecha de la factura si se pasa un rango. De mayor a
    menor.
    """
    where, parametros = _condicion_periodo(fecha_inicio, fecha_fin, "f")

    conexion = conectar()
    cursor = conexion.cursor()
    cursor.execute(
        """
        SELECT ee.nombre AS etiqueta,
               COUNT(*) AS cantidad,
               COALESCE(SUM(e.costo_envio), 0) AS total
        FROM envios e
        JOIN empresas_envio ee ON ee.id = e.empresa_envio_id
        JOIN facturas f ON f.id = e.factura_id
        WHERE {}
        GROUP BY ee.id, ee.nombre
        ORDER BY total DESC
        """.format(where),
        parametros,
    )
    filas = cursor.fetchall()
    conexion.close()
    return filas


def listar_facturas_anuladas(fecha_inicio=None, fecha_fin=None):
    """Listado de facturas anuladas para el reporte del panel admin, con
    el cliente y el metodo de pago, mas recientes primero. Acotado por la
    fecha de la factura si se pasa un rango.
    """
    condiciones = ["f.estado = 'anulado'"]
    parametros = []

    if fecha_inicio:
        condiciones.append("f.fecha >= %s")
        parametros.append(fecha_inicio + " 00:00:00")

    if fecha_fin:
        condiciones.append("f.fecha <= %s")
        parametros.append(fecha_fin + " 23:59:59")

    conexion = conectar()
    cursor = conexion.cursor()
    cursor.execute(
        """
        SELECT f.id, f.numero_factura, f.fecha, f.total,
               u.name AS cliente_nombre, u.apellidos AS cliente_apellidos,
               u.username AS cliente_usuario,
               mp.nombre AS metodo_pago
        FROM facturas f
        JOIN users u ON u.id = f.user_id
        JOIN metodos_pago mp ON mp.id = f.metodo_pago_id
        WHERE {}
        ORDER BY f.fecha DESC
        """.format(" AND ".join(condiciones)),
        parametros,
    )
    filas = cursor.fetchall()
    conexion.close()
    return filas


def _restaurar_stock(cursor, factura_id):
    """Devuelve a `existencias` lo que se habia descontado de un pedido.

    Se usa al anular, tanto desde el admin como desde el cliente. Si una
    existencia habia quedado "agotada" por esta venta, vuelve a quedar
    disponible porque el stock devuelto siempre es mayor a 0.
    """
    cursor.execute(
        "SELECT existencia_id, cantidad FROM detalle_factura WHERE factura_id=%s",
        (factura_id,),
    )
    detalle = cursor.fetchall()

    for item in detalle:
        cursor.execute(
            "UPDATE existencias SET stock = stock + %s, estado='activo' WHERE id=%s",
            (item["cantidad"], item["existencia_id"]),
        )


def actualizar_estado_pedido(factura_id, nuevo_estado):
    """Cambia el estado de envio de un pedido (accion del admin).

    Solo permite avanzar en el flujo pendiente -> preparacion -> enviado
    -> entregado, o anular desde pendiente/preparacion/enviado. Si se
    anula, restaura el stock.

    Devuelve un mensaje de error, o None si el cambio se aplico.
    """
    if nuevo_estado not in TRANSICIONES_ADMIN:
        return "Estado no valido."

    conexion = conectar()
    cursor = conexion.cursor()

    try:
        cursor.execute(
            "SELECT estado FROM facturas WHERE id=%s FOR UPDATE", (factura_id,)
        )
        factura = cursor.fetchone()

        if not factura:
            conexion.rollback()
            return "El pedido no existe."

        if nuevo_estado not in TRANSICIONES_ADMIN[factura["estado"]]:
            conexion.rollback()
            return "El pedido esta '{}' y no se puede pasar a '{}'.".format(
                factura["estado"], nuevo_estado
            )

        if nuevo_estado == "anulado":
            _restaurar_stock(cursor, factura_id)

        cursor.execute(
            "UPDATE facturas SET estado=%s WHERE id=%s", (nuevo_estado, factura_id)
        )
        conexion.commit()
        return None

    except Exception:
        conexion.rollback()
        raise

    finally:
        conexion.close()


def cancelar_pedido_cliente(user_id, factura_id):
    """Permite que el cliente cancele su propio pedido.

    Solo si el pedido es suyo, sigue "pendiente" (no se ha despachado) y
    no pasaron mas de VENTANA_CANCELACION_CLIENTE_MINUTOS desde el pago.
    Restaura el stock igual que una anulacion del admin.

    Devuelve un mensaje de error, o None si se cancelo.
    """
    conexion = conectar()
    cursor = conexion.cursor()

    try:
        cursor.execute(
            """
            SELECT estado, TIMESTAMPDIFF(MINUTE, fecha, NOW()) AS minutos
            FROM facturas WHERE id=%s AND user_id=%s FOR UPDATE
            """,
            (factura_id, user_id),
        )
        factura = cursor.fetchone()

        if not factura:
            conexion.rollback()
            return "El pedido no existe."

        if factura["estado"] != "pendiente":
            conexion.rollback()
            return "Este pedido ya no se puede cancelar."

        if factura["minutos"] > VENTANA_CANCELACION_CLIENTE_MINUTOS:
            conexion.rollback()
            return "Ya pasaron los {} minutos para cancelar este pedido.".format(
                VENTANA_CANCELACION_CLIENTE_MINUTOS
            )

        _restaurar_stock(cursor, factura_id)
        cursor.execute(
            "UPDATE facturas SET estado='anulado' WHERE id=%s", (factura_id,)
        )
        conexion.commit()
        return None

    except Exception:
        conexion.rollback()
        raise

    finally:
        conexion.close()


def obtener_factura(user_id, factura_id):
    """Trae una factura del usuario con todo lo que necesita el PDF.

    Devuelve None si la factura no existe o no es de ese usuario, para
    que nadie pueda descargar la factura de otro.
    """
    return _obtener_factura(factura_id, user_id)


def obtener_factura_admin(factura_id):
    """Trae cualquier factura con todo lo que necesita el PDF.

    A diferencia de `obtener_factura`, no filtra por dueño: es para el
    panel admin, donde se puede consultar la factura de cualquier
    pedido.
    """
    return _obtener_factura(factura_id)


def _obtener_factura(factura_id, user_id=None):
    conexion = conectar()
    cursor = conexion.cursor()

    condicion = "f.id=%s"
    parametros = [factura_id]
    if user_id is not None:
        condicion += " AND f.user_id=%s"
        parametros.append(user_id)

    cursor.execute(
        """
        SELECT f.*,
               u.name, u.apellidos, u.email, u.documento_identidad, u.celular,
               d.direccion, d.ciudad, d.departamento, d.codigo_postal,
               mp.nombre AS metodo_pago,
               (SELECT MAX(p.id) FROM pagos p WHERE p.factura_id = f.id) AS pago_id
        FROM facturas f
        JOIN users u ON u.id = f.user_id
        JOIN direcciones d ON d.id = f.direccion_id
        JOIN metodos_pago mp ON mp.id = f.metodo_pago_id
        WHERE {}
        """.format(condicion),
        parametros,
    )
    factura = cursor.fetchone()

    if not factura:
        conexion.close()
        return None

    cursor.execute(
        """
        SELECT df.cantidad, df.precio_unitario, df.subtotal,
               p.nombre AS producto_nombre, p.referencia,
               t.nombre AS talla, c.nombre AS color, e.sku
        FROM detalle_factura df
        JOIN existencias e ON e.id = df.existencia_id
        JOIN productos p ON p.id = e.producto_id
        JOIN tallas t ON t.id = e.talla_id
        JOIN colores c ON c.id = e.color_id
        WHERE df.factura_id=%s
        ORDER BY df.id
        """,
        (factura_id,),
    )
    factura["items"] = cursor.fetchall()
    conexion.close()

    factura["numero_autorizacion"] = (
        numero_autorizacion(factura["pago_id"]) if factura["pago_id"] else None
    )

    return factura


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


def _validar_datos_pago(form, nombre_metodo):
    """Revisa los campos del metodo de pago elegido.

    Devuelve un mensaje de error, o None si los datos estan completos.
    Es la "verificacion del pago": solo si pasa se guarda la factura.
    """
    if "Tarjeta" in nombre_metodo:
        titular = form.get("tarjeta_nombre", "").strip()
        numero = re.sub(r"\D", "", form.get("tarjeta_numero", ""))
        vencimiento = form.get("tarjeta_vencimiento", "").strip()
        cvv = form.get("tarjeta_cvv", "").strip()

        if len(titular) < 3:
            return "Escribe el nombre que aparece en la tarjeta."

        if not 13 <= len(numero) <= 19:
            return "El numero de tarjeta debe tener entre 13 y 19 digitos."

        if not re.fullmatch(r"(0[1-9]|1[0-2])/\d{2}", vencimiento):
            return "La fecha de vencimiento debe tener el formato MM/AA."

        mes, anio = vencimiento.split("/")
        hoy = datetime.now()
        if (2000 + int(anio), int(mes)) < (hoy.year, hoy.month):
            return "La tarjeta ya esta vencida."

        if not re.fullmatch(r"\d{3,4}", cvv):
            return "El CVV debe tener 3 o 4 digitos."

    elif nombre_metodo == "PSE":
        if not form.get("pse_banco", "").strip():
            return "Selecciona el banco con el que vas a pagar por PSE."

    elif nombre_metodo in ("Nequi", "Daviplata"):
        celular = re.sub(r"\D", "", form.get("billetera_celular", ""))
        if len(celular) != 10:
            return "El numero de celular debe tener 10 digitos."

    return None


def _resolver_direccion(cursor, user_id, form):
    """Devuelve el id de la direccion de envio elegida (o None)."""
    direccion_raw = form.get("direccion_id", "")

    if direccion_raw == "nueva":
        direccion_txt = form.get("direccion", "").strip()
        ciudad = form.get("ciudad", "").strip()
        departamento = form.get("departamento", "").strip()
        codigo_postal = form.get("codigo_postal", "").strip()

        if not direccion_txt or not ciudad:
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
        return cursor.lastrowid

    if not direccion_raw.isdigit():
        return None

    cursor.execute(
        "SELECT id FROM direcciones WHERE id=%s AND user_id=%s",
        (int(direccion_raw), user_id),
    )
    direccion = cursor.fetchone()

    return direccion["id"] if direccion else None


def _descontar_stock(cursor, items):
    """Descuenta de `existencias` lo que se acaba de vender.

    Devuelve un mensaje de error si alguna existencia no alcanza, o None
    si todo el carrito se pudo descontar.
    """
    for item in items:
        cursor.execute(
            "SELECT stock FROM existencias WHERE id=%s FOR UPDATE",
            (item["existencia_id"],),
        )
        existencia = cursor.fetchone()

        if not existencia or existencia["stock"] < item["cantidad"]:
            disponible = existencia["stock"] if existencia else 0
            return "No hay stock suficiente de {} (talla {}): quedan {} y pediste {}.".format(
                item["producto_nombre"], item["talla"], disponible, item["cantidad"]
            )

        # el estado se asigna antes que el stock a proposito: MySQL evalua
        # el SET de izquierda a derecha, asi el IF todavia ve el stock viejo.
        cursor.execute(
            """
            UPDATE existencias
            SET estado = IF(stock - %s <= 0, 'agotado', estado),
                stock = stock - %s
            WHERE id = %s
            """,
            (item["cantidad"], item["cantidad"], item["existencia_id"]),
        )

    return None


def crear_pedido(user_id, form, metodo_pago_id):
    """Confirma el carrito del usuario como un pedido pagado.

    El orden importa: primero se verifican los datos del pago y solo si
    pasan se guarda la factura a nombre del usuario, se descuenta el
    stock de `existencias`, se registra el pago y se vacia el carrito.
    Todo va en una sola transaccion, asi que si algo falla no queda ni
    la factura ni el descuento.

    Devuelve {"ok": True, ...datos del pago} si se completo, o
    {"ok": False, "error": "..."} con el motivo si no.
    """
    items = cart_service.obtener_items(user_id)

    if not items:
        return {"ok": False, "error": "Tu carrito esta vacio."}

    conexion = conectar()
    cursor = conexion.cursor()

    try:
        cursor.execute(
            "SELECT nombre FROM metodos_pago WHERE id=%s AND estado='activo'",
            (metodo_pago_id,),
        )
        metodo = cursor.fetchone()

        if not metodo:
            return {"ok": False, "error": "Selecciona un metodo de pago valido."}

        error_pago = _validar_datos_pago(form, metodo["nombre"])
        if error_pago:
            return {"ok": False, "error": error_pago}

        direccion_id = _resolver_direccion(cursor, user_id, form)

        if not direccion_id:
            conexion.rollback()
            return {"ok": False, "error": "Elige o completa una direccion de envio."}

        error_stock = _descontar_stock(cursor, items)

        if error_stock:
            conexion.rollback()
            return {"ok": False, "error": error_stock}

        subtotal, iva, envio, total = calcular_totales(items)

        cursor.execute(
            """
            INSERT INTO facturas
            (user_id, direccion_id, metodo_pago_id, subtotal, iva, envio, total, estado)
            VALUES (%s, %s, %s, %s, %s, %s, %s, 'pendiente')
            """,
            (user_id, direccion_id, metodo_pago_id, subtotal, iva, envio, total),
        )
        factura_id = cursor.lastrowid

        numero_factura = "FAC-{:04d}".format(factura_id)
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
                (
                    factura_id,
                    item["existencia_id"],
                    item["cantidad"],
                    item["precio"],
                    item["subtotal"],
                ),
            )

        cursor.execute(
            "INSERT INTO pagos (factura_id, monto, estado) VALUES (%s, %s, 'pagado')",
            (factura_id, total),
        )
        pago_id = cursor.lastrowid

        cursor.execute(
            """
            DELETE dc FROM detalle_carrito dc
            JOIN carrito c ON c.id = dc.carrito_id
            WHERE c.user_id=%s
            """,
            (user_id,),
        )

        conexion.commit()

        return {
            "ok": True,
            "factura_id": factura_id,
            "numero_factura": numero_factura,
            "numero_autorizacion": numero_autorizacion(pago_id),
            "metodo_pago": metodo["nombre"],
            "total": str(total),
        }

    except Exception:
        conexion.rollback()
        raise

    finally:
        conexion.close()
