from flask import Blueprint, abort, redirect, render_template, request, session, url_for

from app.services import orders_service, users_service
from app.utils.decorators import login_required
from app.utils.http import respuesta_imagen

usuario = Blueprint("usuario", __name__)


@usuario.route("/perfil", methods=["GET", "POST"])
@login_required
def perfil():
    guardado = False
    error_avatar = None

    if request.method == "POST":
        users_service.actualizar_perfil(session["user_id"], request.form)
        session["name"] = request.form["name"]

        avatar_file = request.files.get("avatar")
        if avatar_file and avatar_file.filename:
            try:
                users_service.actualizar_avatar(session["user_id"], avatar_file)
                session["avatar"] = True
            except ValueError as error:
                error_avatar = str(error)

        guardado = error_avatar is None

    datos = users_service.obtener_usuario(session["user_id"])
    direcciones = orders_service.obtener_direcciones(session["user_id"])

    return render_template(
        "perfil.html",
        usuario=datos,
        guardado=guardado,
        direcciones=direcciones,
        error_direccion=session.pop("error_direccion", None),
        error_avatar=error_avatar,
    )


@usuario.route("/perfil/avatar")
@login_required
def avatar_imagen():
    fila = users_service.obtener_imagen_avatar(session["user_id"])
    if not fila or not fila["avatar_imagen"]:
        abort(404)
    return respuesta_imagen(fila["avatar_imagen"], fila["avatar_mime"])


@usuario.route("/perfil/direcciones", methods=["POST"])
@login_required
def crear_direccion():
    error = orders_service.crear_direccion(session["user_id"], request.form)
    if error:
        session["error_direccion"] = error
    return redirect(url_for("usuario.perfil") + "#direcciones")


@usuario.route("/perfil/direcciones/<int:id>", methods=["POST"])
@login_required
def editar_direccion(id):
    error = orders_service.actualizar_direccion(session["user_id"], id, request.form)
    if error:
        session["error_direccion"] = error
    return redirect(url_for("usuario.perfil") + "#direcciones")


@usuario.route("/perfil/direcciones/<int:id>/eliminar", methods=["POST"])
@login_required
def eliminar_direccion(id):
    orders_service.eliminar_direccion(session["user_id"], id)
    return redirect(url_for("usuario.perfil") + "#direcciones")


@usuario.route("/perfil/direcciones/<int:id>/principal", methods=["POST"])
@login_required
def marcar_direccion_principal(id):
    orders_service.marcar_direccion_principal(session["user_id"], id)
    return redirect(url_for("usuario.perfil") + "#direcciones")


@usuario.route("/mis-pedidos")
@login_required
def mis_pedidos():
    pedidos = orders_service.obtener_pedidos(session["user_id"])

    total_gastado = sum(
        float(p["total"]) for p in pedidos if p["estado"] != "anulado"
    )

    return render_template(
        "mis_pedidos.html",
        pedidos=pedidos,
        total_pedidos=len(pedidos),
        total_gastado=total_gastado,
        ventana_cancelacion_minutos=orders_service.VENTANA_CANCELACION_CLIENTE_MINUTOS,
        error_pedido=session.pop("error_pedido", None),
    )


@usuario.route("/mis-pedidos/<int:factura_id>/cancelar", methods=["POST"])
@login_required
def cancelar_pedido(factura_id):
    error = orders_service.cancelar_pedido_cliente(session["user_id"], factura_id)
    if error:
        session["error_pedido"] = error
    return redirect(url_for("usuario.mis_pedidos"))


@usuario.route("/mis-pedidos/<int:factura_id>")
@login_required
def pedido_detalle(factura_id):
    pedido = orders_service.obtener_factura(session["user_id"], factura_id)

    if not pedido:
        abort(404)

    if pedido["estado"] in orders_service.ETAPAS_ENVIO:
        paso_actual = orders_service.ETAPAS_ENVIO.index(pedido["estado"])
    else:
        paso_actual = -1

    return render_template(
        "pedido_detalle.html",
        pedido=pedido,
        etapas_envio=orders_service.ETAPAS_ENVIO,
        etapas_envio_labels=orders_service.ETAPAS_ENVIO_LABELS,
        paso_actual=paso_actual,
    )
