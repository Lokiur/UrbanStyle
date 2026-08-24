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

from app.services import (
    contact_service,
    invoice_service,
    orders_service,
    products_service,
    users_service,
)
from app.utils.decorators import admin_required

admin = Blueprint("admin", __name__)


# =========================
# PANEL ADMIN
# =========================


@admin.route("/admin")
@admin_required
def admin_panel():
    users = users_service.listar_usuarios()
    productos = products_service.listar_productos_admin()
    pedidos = orders_service.listar_pedidos()
    mensajes = contact_service.listar_mensajes()

    return render_template(
        "indexmvc.html",
        users=users,
        productos=productos,
        categorias=products_service.listar_categorias(),
        marcas=products_service.listar_marcas(),
        pedidos=pedidos,
        mensajes=mensajes,
        total_usuarios=len(users),
        total_productos=len(productos),
        total_pedidos=len(pedidos),
        ventas_totales=sum(
            float(p["total"]) for p in pedidos if p["estado"] != "anulado"
        ),
        total_mensajes=len(mensajes),
        mensajes_nuevos=sum(1 for m in mensajes if m["estado"] == "nuevo"),
        error_producto=session.pop("error_producto", None),
        error_pedido=session.pop("error_pedido", None),
    )


# =========================
# CRUD ADMIN - USUARIOS
# =========================


@admin.route("/usuario", methods=["POST"])
@admin_required
def crear_usuario():
    users_service.crear(request.form)
    return redirect(url_for("admin.admin_panel"))


@admin.route("/delete/<int:id>")
@admin_required
def delete(id):
    users_service.eliminar(id)
    return redirect(url_for("admin.admin_panel"))


@admin.route("/edit/<int:id>", methods=["POST"])
@admin_required
def edit(id):
    users_service.actualizar(id, request.form)
    return redirect(url_for("admin.admin_panel"))


# =========================
# CRUD ADMIN - PRODUCTOS
# =========================


@admin.route("/producto", methods=["POST"])
@admin_required
def crear_producto():
    try:
        products_service.crear_producto(request.form, request.files.get("imagen"))
    except ValueError as error:
        session["error_producto"] = str(error)
    return redirect(url_for("admin.admin_panel") + "#section-productos")


@admin.route("/producto/editar/<int:id>", methods=["POST"])
@admin_required
def editar_producto(id):
    try:
        products_service.actualizar_producto(id, request.form, request.files.get("imagen"))
    except ValueError as error:
        session["error_producto"] = str(error)
    return redirect(url_for("admin.admin_panel") + "#section-productos")


@admin.route("/producto/eliminar/<int:id>")
@admin_required
def eliminar_producto(id):
    products_service.eliminar_producto(id)
    return redirect(url_for("admin.admin_panel"))


# =========================
# ADMIN - ESTADOS DE PEDIDOS
# =========================


@admin.route("/pedido/<int:id>/estado", methods=["POST"])
@admin_required
def actualizar_estado_pedido(id):
    error = orders_service.actualizar_estado_pedido(id, request.form.get("estado", ""))
    if error:
        session["error_pedido"] = error
    return redirect(url_for("admin.admin_panel") + "#section-pedidos")


@admin.route("/pedido/<int:id>/factura.pdf")
@admin_required
def factura_pdf(id):
    factura = orders_service.obtener_factura_admin(id)

    if not factura:
        abort(404)

    return send_file(
        BytesIO(invoice_service.generar_pdf(factura)),
        mimetype="application/pdf",
        download_name="{}.pdf".format(factura["numero_factura"] or id),
    )


# =========================
# ADMIN - MENSAJES DE CONTACTO
# =========================


@admin.route("/mensaje/leido/<int:id>")
@admin_required
def marcar_mensaje_leido(id):
    contact_service.marcar_leido(id)
    return redirect(url_for("admin.admin_panel") + "#section-mensajes")


@admin.route("/mensaje/eliminar/<int:id>")
@admin_required
def eliminar_mensaje(id):
    contact_service.eliminar_mensaje(id)
    return redirect(url_for("admin.admin_panel") + "#section-mensajes")
