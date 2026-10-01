from flask import (
    Blueprint,
    current_app,
    redirect,
    render_template,
    request,
    session,
    url_for,
)

from app.services import auth_service
from app.utils.mailer import enviar_correo
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
        email = request.form.get("email", "").strip()

        if not captcha_valido(request.form.get("captcha", ""), _honeypot()):
            return render_template(
                "recuperar.html",
                message="Captcha incorrecto, intenta de nuevo.",
                email=email,
                **captcha_context(),
            )

        usuario = auth_service.buscar_por_email(email) if email else None

        if usuario:
            _enviar_enlace_recuperacion(usuario)

        # Misma respuesta exista o no la cuenta, para no revelar
        # que correos estan registrados.
        return render_template("recuperar.html", enviado=True, email=email)

    return render_template("recuperar.html", **captcha_context())


def _enviar_enlace_recuperacion(usuario):
    token = auth_service.generar_token_recuperacion(usuario)
    enlace = url_for("auth.restablecer", token=token, _external=True)
    minutos = auth_service.TOKEN_MAX_EDAD // 60

    texto = (
        f"Hola {usuario['name']},\n\n"
        "Recibimos una solicitud para restablecer la contraseña de tu cuenta "
        f"de UrbanStyle ({usuario['username']}).\n\n"
        f"Abre este enlace para elegir una nueva (caduca en {minutos} minutos):\n"
        f"{enlace}\n\n"
        "Si no fuiste tú, ignora este correo: tu contraseña no cambiará."
    )
    html = render_template(
        "email_recuperar.html", usuario=usuario, enlace=enlace, minutos=minutos
    )

    try:
        enviar_correo(usuario["email"], "Restablece tu contraseña | UrbanStyle", texto, html)
    except Exception:
        current_app.logger.exception("No se pudo enviar el correo de recuperación")


@auth.route("/restablecer/<token>", methods=["GET", "POST"])
def restablecer(token):

    usuario = auth_service.verificar_token_recuperacion(token)

    if not usuario:
        return render_template("restablecer.html", invalido=True)

    if request.method == "POST":
        nueva_password = request.form.get("nueva_password", "")
        confirmar = request.form.get("confirmar_password", "")

        if not password_service.validate(nueva_password):
            return render_template(
                "restablecer.html",
                message="La contraseña debe tener al menos 8 caracteres e incluir letras y números.",
            )

        if nueva_password != confirmar:
            return render_template(
                "restablecer.html", message="Las contraseñas no coinciden."
            )

        auth_service.cambiar_password(usuario["id"], nueva_password)

        return redirect(url_for("auth.login", restablecida=1))

    return render_template("restablecer.html")


# =========================
# LOGOUT
# =========================


@auth.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("auth.login"))
