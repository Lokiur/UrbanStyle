from io import BytesIO

from flask import (
    Blueprint,
    abort,
    redirect,
    render_template,
    request,
    send_file,
    session,
    url_for,
)

from app.services import cart_service, invoice_service, orders_service
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
        # se muestran una sola vez: los deja `confirmar` en la sesion
        confirmacion=session.pop("pago_confirmado", None),
        error_checkout=session.pop("error_checkout", None),
        error_carrito=session.pop("error_carrito", None),
    )


@carrito.route("/carrito/confirmar", methods=["POST"])
@login_required
def confirmar():
    resultado = orders_service.crear_pedido(
        session["user_id"],
        request.form,
        request.form.get("metodo_pago_id", type=int),
    )

    if not resultado["ok"]:
        session["error_checkout"] = resultado["error"]
    else:
        session["pago_confirmado"] = resultado

    return redirect(url_for("carrito.ver"))


@carrito.route("/factura/<int:factura_id>.pdf")
@login_required
def factura_pdf(factura_id):
    factura = orders_service.obtener_factura(session["user_id"], factura_id)

    if not factura:
        abort(404)

    return send_file(
        BytesIO(invoice_service.generar_pdf(factura)),
        mimetype="application/pdf",
        # inline: se abre en el visor del navegador, listo para imprimir
        download_name="{}.pdf".format(factura["numero_factura"] or factura_id),
    )


@carrito.route("/carrito/agregar/<int:producto_id>", methods=["POST"])
@login_required
def agregar(producto_id):
    resultado = cart_service.agregar(
        session["user_id"],
        producto_id,
        request.form.get("existencia_id", type=int),
    )

    if not resultado["ok"]:
        session["error_carrito"] = resultado["error"]

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
