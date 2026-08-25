import os
import uuid

from flask import Blueprint, current_app, redirect, render_template, request, session, url_for

from app.services import orders_service, users_service
from app.utils.decorators import login_required

usuario = Blueprint("usuario", __name__)

AVATAR_EXTENSIONS = {"png", "jpg", "jpeg", "webp", "gif"}


def _extension_valida(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in AVATAR_EXTENSIONS


def _avatar_folder():
    ruta = os.path.join(current_app.static_folder, "img", "avatars")
    os.makedirs(ruta, exist_ok=True)
    return ruta


def _guardar_avatar(archivo, user_id):
    extension = archivo.filename.rsplit(".", 1)[1].lower()
    nombre_archivo = f"user_{user_id}_{uuid.uuid4().hex}.{extension}"

    carpeta = _avatar_folder()
    archivo.save(os.path.join(carpeta, nombre_archivo))

    avatar_anterior = session.get("avatar")
    if avatar_anterior:
        ruta_anterior = os.path.join(carpeta, avatar_anterior)
        if os.path.isfile(ruta_anterior):
            os.remove(ruta_anterior)

    return nombre_archivo


@usuario.route("/perfil", methods=["GET", "POST"])
@login_required
def perfil():
    guardado = False

    if request.method == "POST":
        users_service.actualizar_perfil(session["user_id"], request.form)
        session["name"] = request.form["name"]

        avatar_file = request.files.get("avatar")
        if avatar_file and avatar_file.filename and _extension_valida(avatar_file.filename):
            nombre_archivo = _guardar_avatar(avatar_file, session["user_id"])
            users_service.actualizar_avatar(session["user_id"], nombre_archivo)
            session["avatar"] = nombre_archivo

        guardado = True

    datos = users_service.obtener_usuario(session["user_id"])

    return render_template("perfil.html", usuario=datos, guardado=guardado)


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
