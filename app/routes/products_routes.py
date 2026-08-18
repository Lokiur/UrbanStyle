from flask import Blueprint, Response, abort, render_template, request

from app.services.products_service import (
    buscar_productos,
    obtener_categoria,
    obtener_imagen_producto,
    obtener_productos,
)

productos = Blueprint("productos", __name__)


@productos.route("/categories")
def categories():
    return render_template("categories.html")


@productos.route("/producto/<int:id>/imagen")
def imagen_producto(id):
    fila = obtener_imagen_producto(id)
    if not fila or not fila["imagen"]:
        abort(404)
    return Response(fila["imagen"], mimetype=fila["imagen_mime"] or "image/jpeg")


@productos.route("/products")
def products():
    return render_template("products.html", productos=obtener_productos())


@productos.route("/categoria/<int:id>")
def categoria_productos(id):
    return render_template("products.html", productos=obtener_categoria(id))


@productos.route("/buscar")
def buscar():
    query = request.args.get("q", "").strip()
    return render_template(
        "products.html",
        productos=buscar_productos(query),
        query=query,
    )
