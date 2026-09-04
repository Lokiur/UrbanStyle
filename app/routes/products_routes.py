from flask import Blueprint, Response, abort, render_template, request

from app.services.products_service import (
    buscar_productos,
    listar_tallas,
    obtener_categoria,
    obtener_imagen_producto,
    obtener_productos,
)

productos = Blueprint("productos", __name__)


def _filtros_desde_request():
    """Lee talla/precio min/max de la query string (RF13)."""
    talla_id = request.args.get("talla_id", type=int)
    precio_min = request.args.get("precio_min", type=int)
    precio_max = request.args.get("precio_max", type=int)
    return talla_id, precio_min, precio_max


def _contexto_filtros():
    talla_id, precio_min, precio_max = _filtros_desde_request()
    return {
        "tallas": listar_tallas(),
        "filtro_talla_id": talla_id,
        "filtro_precio_min": precio_min,
        "filtro_precio_max": precio_max,
    }


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
    talla_id, precio_min, precio_max = _filtros_desde_request()
    return render_template(
        "products.html",
        productos=obtener_productos(talla_id, precio_min, precio_max),
        **_contexto_filtros(),
    )


@productos.route("/categoria/<int:id>")
def categoria_productos(id):
    talla_id, precio_min, precio_max = _filtros_desde_request()
    return render_template(
        "products.html",
        productos=obtener_categoria(id, talla_id, precio_min, precio_max),
        **_contexto_filtros(),
    )


@productos.route("/buscar")
def buscar():
    query = request.args.get("q", "").strip()
    talla_id, precio_min, precio_max = _filtros_desde_request()
    return render_template(
        "products.html",
        productos=buscar_productos(query, talla_id, precio_min, precio_max),
        query=query,
        **_contexto_filtros(),
    )
