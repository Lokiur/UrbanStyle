from flask import Blueprint, render_template

home = Blueprint("home", __name__)


@home.route("/")
def index():
    return render_template("index.html")


@home.route("/offers")
def offers():
    return render_template("offers.html")


@home.route("/about")
def about():
    return render_template("about.html")


@home.route("/contacto")
def contacto():
    return render_template("contacto.html")


@home.route("/preguntas-frecuentes")
def faq():
    return render_template("faq.html")


@home.route("/terminos")
def terminos():
    return render_template("terminos.html")
