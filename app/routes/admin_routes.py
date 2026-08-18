from flask import Blueprint, redirect, render_template, request, url_for

from app.services import products_service, users_service
from app.utils.decorators import admin_required

admin = Blueprint("admin", __name__)


# =========================
# PANEL ADMIN
# =========================


@admin.route("/admin")
@admin_required
def admin_panel():
    return render_template(
        "indexmvc.html",
        users=users_service.listar_usuarios(),
        productos=products_service.listar_productos_admin(),
        categorias=products_service.listar_categorias(),
        marcas=products_service.listar_marcas(),
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
    products_service.crear_producto(request.form, request.files.get("imagen"))
    return redirect(url_for("admin.admin_panel"))


@admin.route("/producto/editar/<int:id>", methods=["POST"])
@admin_required
def editar_producto(id):
    products_service.actualizar_producto(id, request.form, request.files.get("imagen"))
    return redirect(url_for("admin.admin_panel"))


@admin.route("/producto/eliminar/<int:id>")
@admin_required
def eliminar_producto(id):
    products_service.eliminar_producto(id)
    return redirect(url_for("admin.admin_panel"))
