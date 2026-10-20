from flask import Blueprint, render_template, request

from app.services import contact_service, products_service

home = Blueprint("home", __name__)


@home.route("/")
def index():
    total_productos = len(products_service.obtener_productos())
    return render_template("index.html", total_productos=total_productos)


@home.route("/offers")
def offers():
    # el titular sale de los descuentos que el admin tenga asignados:
    # si cambian o se quitan, la pagina cambia sola (no hay textos fijos)
    ofertas = products_service.obtener_ofertas()
    descuentos = {p["descuento"] for p in ofertas}
    return render_template(
        "offers.html",
        ofertas=ofertas,
        descuento_max=max(descuentos, default=0),
        descuento_variable=len(descuentos) > 1,
    )


@home.route("/about")
def about():
    total_productos = len(products_service.obtener_productos())
    return render_template("about.html", total_productos=total_productos)


@home.route("/contacto", methods=["GET", "POST"])
def contacto():
    enviado = False

    if request.method == "POST":
        contact_service.crear_mensaje(request.form)
        enviado = True

    return render_template("contacto.html", enviado=enviado)


@home.route("/preguntas-frecuentes")
def faq():
    return render_template("faq.html")


@home.route("/terminos")
def terminos():
    return render_template("terminos.html")
