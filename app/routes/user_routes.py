from flask import Blueprint, render_template, request, session

from app.services import orders_service, users_service
from app.utils.decorators import login_required

usuario = Blueprint("usuario", __name__)


@usuario.route("/perfil", methods=["GET", "POST"])
@login_required
def perfil():

    if request.method == "POST":
        users_service.actualizar_perfil(session["user_id"], request.form)
        session["name"] = request.form["name"]

    datos = users_service.obtener_usuario(session["user_id"])

    return render_template("perfil.html", usuario=datos)


@usuario.route("/mis-pedidos")
@login_required
def mis_pedidos():
    pedidos = orders_service.obtener_pedidos(session["user_id"])
    return render_template("mis_pedidos.html", pedidos=pedidos)
