from flask import Blueprint, redirect, render_template, request, session, url_for

from app.services import cart_service, orders_service
from app.utils.decorators import login_required

carrito = Blueprint("carrito", __name__)


@carrito.route("/carrito")
@login_required
def ver():
    items = cart_service.obtener_items(session["user_id"])
    subtotal, iva, envio, total_final = orders_service.calcular_totales(items)

    return render_template(
        "carrito.html",
        items=items,
        total=subtotal,
        iva=iva,
        envio=envio,
        total_final=total_final,
        direcciones=orders_service.obtener_direcciones(session["user_id"]),
        metodos_pago=orders_service.obtener_metodos_pago(),
    )


@carrito.route("/carrito/confirmar", methods=["POST"])
@login_required
def confirmar():
    factura_id = orders_service.crear_pedido(
        session["user_id"],
        request.form,
        request.form.get("metodo_pago_id", type=int),
    )

    if not factura_id:
        return redirect(url_for("carrito.ver"))

    return redirect(url_for("usuario.mis_pedidos", ok=1))


@carrito.route("/carrito/agregar/<int:producto_id>", methods=["POST"])
@login_required
def agregar(producto_id):
    cart_service.agregar(
        session["user_id"],
        producto_id,
        request.form.get("existencia_id", type=int),
    )
    return redirect(url_for("carrito.ver"))


@carrito.route("/carrito/sumar/<int:detalle_id>", methods=["POST"])
@login_required
def sumar(detalle_id):
    cart_service.sumar(session["user_id"], detalle_id)
    return redirect(url_for("carrito.ver"))


@carrito.route("/carrito/restar/<int:detalle_id>", methods=["POST"])
@login_required
def restar(detalle_id):
    cart_service.restar(session["user_id"], detalle_id)
    return redirect(url_for("carrito.ver"))


@carrito.route("/carrito/eliminar/<int:detalle_id>", methods=["POST"])
@login_required
def eliminar(detalle_id):
    cart_service.eliminar(session["user_id"], detalle_id)
    return redirect(url_for("carrito.ver"))
