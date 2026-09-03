import random
import time

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


# =========================================================
# CAPTCHA  (desafío aritmético con endurecimiento básico)
# ---------------------------------------------------------
#  Mejoras respecto de la suma fija de un dígito:
#   - Operaciones variadas (+, -, ×) y rangos mayores.
#   - Caducidad del desafío (no sirve para siempre).
#   - Rechazo de envíos sospechosamente rápidos (bots).
#   - Bloqueo temporal tras varios fallos seguidos.
#   - Campo trampa (honeypot) que un humano nunca rellena.
#  La respuesta correcta vive solo en la sesión del servidor.
# =========================================================

CAPTCHA_TTL = 300          # segundos que un desafío sigue siendo válido
CAPTCHA_MIN_SECONDS = 1.5  # tiempo mínimo "humano" para resolverlo
CAPTCHA_MAX_FAILS = 5      # fallos seguidos antes del bloqueo
CAPTCHA_LOCK_SECONDS = 30  # duración del bloqueo temporal

_OPERACIONES = (
    ("+", lambda a, b: a + b),
    ("−", lambda a, b: a - b),
    ("×", lambda a, b: a * b),
)


def _bloqueo_restante():
    return max(0, int(session.get("captcha_locked_until", 0) - time.time()))


def captcha_bloqueado():
    return _bloqueo_restante() > 0


def captcha_espera():
    return _bloqueo_restante()


def generar_captcha():
    """Crea un desafío nuevo (o mantiene el actual si hay bloqueo) y
    devuelve el texto de la pregunta, p. ej. ``"12 × 7"``."""
    if _bloqueo_restante() > 0 and session.get("captcha_question"):
        return session["captcha_question"]

    simbolo, operar = random.choice(_OPERACIONES)

    if simbolo == "×":
        a, b = random.randint(2, 9), random.randint(2, 9)
    elif simbolo == "−":
        a, b = random.randint(11, 20), random.randint(2, 9)
    else:
        a, b = random.randint(4, 19), random.randint(4, 19)

    session["captcha_answer"] = operar(a, b)
    session["captcha_question"] = f"{a} {simbolo} {b}"
    session["captcha_issued_at"] = time.time()
    return session["captcha_question"]


def captcha_context():
    """Diccionario listo para pasar al ``render_template`` de los
    formularios de autenticación."""
    return {
        "captcha_question": generar_captcha(),
        "captcha_bloqueado": captcha_bloqueado(),
        "captcha_espera": captcha_espera(),
    }


def captcha_valido(respuesta, honeypot=""):
    if _bloqueo_restante() > 0:
        return False

    # El honeypot es un campo oculto: si viene con algo, es un bot.
    if honeypot and honeypot.strip():
        _registrar_fallo()
        return False

    esperado = session.get("captcha_answer")
    emitido = session.get("captcha_issued_at", 0)

    if esperado is None:
        return False

    # Caducó: obliga a recargar el formulario.
    if time.time() - emitido > CAPTCHA_TTL:
        _olvidar_desafio()
        return False

    # Resuelto "demasiado rápido" para ser una persona.
    if time.time() - emitido < CAPTCHA_MIN_SECONDS:
        _registrar_fallo()
        return False

    try:
        correcto = int(str(respuesta).strip()) == int(esperado)
    except (TypeError, ValueError):
        correcto = False

    if correcto:
        _limpiar_todo()
        return True

    _registrar_fallo()
    return False


def _registrar_fallo():
    fallos = session.get("captcha_fails", 0) + 1
    session["captcha_fails"] = fallos
    if fallos >= CAPTCHA_MAX_FAILS:
        session["captcha_locked_until"] = time.time() + CAPTCHA_LOCK_SECONDS
        session["captcha_fails"] = 0


def _olvidar_desafio():
    for clave in ("captcha_answer", "captcha_question", "captcha_issued_at"):
        session.pop(clave, None)


def _limpiar_todo():
    for clave in (
        "captcha_answer",
        "captcha_question",
        "captcha_issued_at",
        "captcha_fails",
        "captcha_locked_until",
    ):
        session.pop(clave, None)
