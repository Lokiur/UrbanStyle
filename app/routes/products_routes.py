from flask import Blueprint, render_template, request

from app.services.products_service import (
    buscar_productos,
    obtener_categoria,
    obtener_productos,
)

productos = Blueprint("productos", __name__)


@productos.route("/categories")
def categories():
    return render_template("categories.html")


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
