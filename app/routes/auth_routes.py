from flask import Blueprint, redirect, render_template, request, session, url_for

from app.services import auth_service
from app.utils.security import captcha_valido, generar_captcha, password_service

auth = Blueprint("auth", __name__)


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
            a, b = generar_captcha()
            return render_template(
                "register.html",
                message="La contraseña debe tener al menos 8 caracteres e incluir letras y números.",
                captcha_a=a,
                captcha_b=b,
            )

        if not captcha_valido(request.form.get("captcha", "")):
            a, b = generar_captcha()
            return render_template(
                "register.html",
                message="Captcha incorrecto, intenta de nuevo.",
                captcha_a=a,
                captcha_b=b,
            )

        if auth_service.existe_usuario(username, email):
            a, b = generar_captcha()
            return render_template(
                "register.html",
                message="Ese usuario o correo ya está registrado.",
                captcha_a=a,
                captcha_b=b,
            )

        auth_service.registrar(request.form)

        return redirect(url_for("auth.login"))

    a, b = generar_captcha()
    return render_template("register.html", captcha_a=a, captcha_b=b)


# =========================
# LOGIN
# =========================


@auth.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        if not captcha_valido(request.form.get("captcha", "")):
            a, b = generar_captcha()
            return render_template(
                "login.html",
                message="Captcha incorrecto, intenta de nuevo.",
                captcha_a=a,
                captcha_b=b,
            )

        usuario = auth_service.login(username, password)

        if usuario:
            session["user"] = usuario["username"]
            session["user_id"] = usuario["id"]
            session["name"] = usuario["name"]
            session["rol"] = usuario["rol"]
            return redirect(url_for("home.index"))

        a, b = generar_captcha()
        return render_template(
            "login.html",
            message="Usuario o contraseña incorrectos",
            captcha_a=a,
            captcha_b=b,
        )

    a, b = generar_captcha()
    return render_template("login.html", captcha_a=a, captcha_b=b)


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
            a, b = generar_captcha()
            return render_template(
                "recuperar.html",
                message="La contraseña debe tener al menos 8 caracteres e incluir letras y números.",
                captcha_a=a,
                captcha_b=b,
            )

        if not captcha_valido(request.form.get("captcha", "")):
            a, b = generar_captcha()
            return render_template(
                "recuperar.html",
                message="Captcha incorrecto, intenta de nuevo.",
                captcha_a=a,
                captcha_b=b,
            )

        usuario = auth_service.buscar_por_documento(username, documento_identidad)

        if not usuario:
            a, b = generar_captcha()
            return render_template(
                "recuperar.html",
                message="El usuario o el documento de identidad no coinciden.",
                captcha_a=a,
                captcha_b=b,
            )

        auth_service.cambiar_password(usuario["id"], nueva_password)

        return redirect(url_for("auth.login"))

    a, b = generar_captcha()
    return render_template("recuperar.html", captcha_a=a, captcha_b=b)


# =========================
# LOGOUT
# =========================


@auth.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("auth.login"))
