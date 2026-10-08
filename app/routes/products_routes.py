from flask import Blueprint, Response, abort, render_template, request

from app.services.products_service import (
    DIAS_NUEVO,
    buscar_productos,
    listar_categorias,
    listar_categorias_vitrina,
    listar_tallas,
    obtener_categoria,
    obtener_detalle_producto,
    obtener_imagen_categoria,
    obtener_imagen_producto,
    obtener_nuevos,
    obtener_productos,
    obtener_relacionados,
)

productos = Blueprint("productos", __name__)

# prendas que muestra /nuevo cuando no llego nada en los ultimos DIAS_NUEVO dias
ULTIMOS_INGRESOS = 8


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
        "categorias": listar_categorias(),
        "filtro_talla_id": talla_id,
        "filtro_precio_min": precio_min,
        "filtro_precio_max": precio_max,
    }


@productos.route("/categories")
def categories():
    categorias = listar_categorias_vitrina()
    return render_template(
        "categories.html",
        categorias=categorias,
        total_productos=sum(c["total_productos"] for c in categorias),
        tallas=listar_tallas(),
    )


@productos.route("/producto/<int:id>/imagen")
def imagen_producto(id):
    fila = obtener_imagen_producto(id)
    if not fila or not fila["imagen"]:
        abort(404)
    return Response(fila["imagen"], mimetype=fila["imagen_mime"] or "image/jpeg")


@productos.route("/categoria/<int:id>/imagen")
def imagen_categoria(id):
    fila = obtener_imagen_categoria(id)
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


@productos.route("/nuevo")
def nuevo():
    """Lo que llego en los ultimos DIAS_NUEVO dias. Las pildoras de
    categoria filtran dentro de las novedades (?categoria=<id>) y solo
    aparecen las categorias que tienen alguna. Si no hay ninguna novedad
    se muestran los ultimos ingresos, sin presentarlos como nuevos.
    """
    talla_id, precio_min, precio_max = _filtros_desde_request()
    categoria_id = request.args.get("categoria", type=int)

    novedades = obtener_nuevos()
    contexto = _contexto_filtros()
    con_novedades = {p["categoria_id"] for p in novedades}
    contexto["categorias_nuevo"] = [
        c for c in contexto["categorias"] if c["id"] in con_novedades
    ]

    if not novedades:
        productos_pagina = obtener_productos()[:ULTIMOS_INGRESOS]
    elif categoria_id or talla_id or precio_min or precio_max:
        productos_pagina = obtener_nuevos(categoria_id, talla_id, precio_min, precio_max)
    else:
        productos_pagina = novedades

    return render_template(
        "products.html",
        modo="nuevo",
        sin_novedades=not novedades,
        dias_nuevo=DIAS_NUEVO,
        productos=productos_pagina,
        categoria_actual=categoria_id,
        **contexto,
    )


@productos.route("/producto/<int:id>")
def detalle_producto(id):
    producto = obtener_detalle_producto(id)
    if not producto:
        abort(404)
    return render_template(
        "producto_detalle.html",
        producto=producto,
        relacionados=obtener_relacionados(id, producto["categoria_id"]),
    )


@productos.route("/categoria/<int:id>")
def categoria_productos(id):
    talla_id, precio_min, precio_max = _filtros_desde_request()
    return render_template(
        "products.html",
        productos=obtener_categoria(id, talla_id, precio_min, precio_max),
        categoria_actual=id,
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
