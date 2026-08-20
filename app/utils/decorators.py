from functools import wraps

from flask import redirect, session, url_for

from app.services.users_service import obtener_usuario


def login_required(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        if "user" not in session:
            return redirect(url_for("auth.login"))

        # la cuenta pudo haber sido borrada (por un admin, o al reiniciar
        # la BD) mientras la sesion seguia activa en el navegador; sin este
        # chequeo, cualquier insert que use user_id como llave foranea
        # (carrito, direcciones, facturas...) truena con IntegrityError.
        if not obtener_usuario(session["user_id"]):
            session.clear()
            return redirect(url_for("auth.login"))

        return f(*args, **kwargs)

    return wrapper


def admin_required(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        if session.get("rol") != "admin":
            return redirect(url_for("home.index"))
        return f(*args, **kwargs)

    return wrapper
