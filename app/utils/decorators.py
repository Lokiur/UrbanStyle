from functools import wraps

from flask import redirect, session, url_for


def login_required(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        if "user" not in session:
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
