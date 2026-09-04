from flask import Blueprint, redirect, render_template, request, session, url_for

from app.services import auth_service
from app.utils.security import captcha_context, captcha_valido, password_service

auth = Blueprint("auth", __name__)


def _honeypot():
    return request.form.get("website", "")


# =========================
# REGISTER
# =========================


@auth.route("/register", methods=["GET", "POST"])
def register():

    if request.method == "POST":
        username = request.form["username"]
        email = request.form["email"]
        password = request.form["password"]

        if not password_service.validate(password):
            return render_template(
                "register.html",
                message="La contraseña debe tener al menos 8 caracteres e incluir letras y números.",
                **captcha_context(),
            )

        if not captcha_valido(request.form.get("captcha", ""), _honeypot()):
            return render_template(
                "register.html",
                message="Captcha incorrecto, intenta de nuevo.",
                **captcha_context(),
            )

        if auth_service.existe_usuario(username, email):
            return render_template(
                "register.html",
                message="Ese usuario o correo ya está registrado.",
                **captcha_context(),
            )

        auth_service.registrar(request.form)

        return redirect(url_for("auth.login"))

    return render_template("register.html", **captcha_context())


# =========================
# LOGIN
# =========================


@auth.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        if not captcha_valido(request.form.get("captcha", ""), _honeypot()):
            return render_template(
                "login.html",
                message="Captcha incorrecto, intenta de nuevo.",
                **captcha_context(),
            )

        usuario = auth_service.login(username, password)

        if usuario:
            session["user"] = usuario["username"]
            session["user_id"] = usuario["id"]
            session["name"] = usuario["name"]
            session["rol"] = usuario["rol"]
            session["avatar"] = usuario.get("avatar")
            return redirect(url_for("home.index"))

        return render_template(
            "login.html",
            message="Usuario o contraseña incorrectos",
            **captcha_context(),
        )

    return render_template("login.html", **captcha_context())


# =========================
# RECUPERAR CONTRASEÑA
# =========================


@auth.route("/recuperar", methods=["GET", "POST"])
def recuperar():

    if request.method == "POST":
        username = request.form["username"]
        documento_identidad = request.form["documento_identidad"]
        nueva_password = request.form["nueva_password"]

        if not password_service.validate(nueva_password):
            return render_template(
                "recuperar.html",
                message="La contraseña debe tener al menos 8 caracteres e incluir letras y números.",
                **captcha_context(),
            )

        if not captcha_valido(request.form.get("captcha", ""), _honeypot()):
            return render_template(
                "recuperar.html",
                message="Captcha incorrecto, intenta de nuevo.",
                **captcha_context(),
            )

        usuario = auth_service.buscar_por_documento(username, documento_identidad)

        if not usuario:
            return render_template(
                "recuperar.html",
                message="El usuario o el documento de identidad no coinciden.",
                **captcha_context(),
            )

        auth_service.cambiar_password(usuario["id"], nueva_password)

        return redirect(url_for("auth.login"))

    return render_template("recuperar.html", **captcha_context())


# =========================
# LOGOUT
# =========================


@auth.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("auth.login"))
