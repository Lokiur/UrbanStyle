import random

from flask import session
from werkzeug.security import check_password_hash, generate_password_hash


class password:
    def hash(self, plain_password):
        return generate_password_hash(plain_password)

    def verify(self, plain_password, hashed_password):
        return check_password_hash(hashed_password, plain_password)

    def validate(self, plain_password):
        if not isinstance(plain_password, str):
            return False
        if len(plain_password) < 8:
            return False
        has_letter = any(ch.isalpha() for ch in plain_password)
        has_digit = any(ch.isdigit() for ch in plain_password)
        return has_letter and has_digit


password_service = password()


# =========================
# CAPTCHA (suma simple)
# =========================


def generar_captcha():
    a, b = random.randint(1, 9), random.randint(1, 9)
    session["captcha_a"] = a
    session["captcha_b"] = b
    return a, b


def captcha_valido(respuesta):
    esperado = session.pop("captcha_a", None), session.pop("captcha_b", None)
    if None in esperado:
        return False
    try:
        return int(respuesta) == sum(esperado)
    except (TypeError, ValueError):
        return False
