# =========================
# LOGIN / REGISTRO / RECUPERACION
# =========================

import hashlib

from flask import current_app
from itsdangerous import BadSignature, SignatureExpired, URLSafeTimedSerializer

from app.utils.security import password_service
from database.init_db import conectar


def login(username, password):
    conexion = conectar()
    cursor = conexion.cursor()

    cursor.execute(
        "SELECT * FROM users WHERE username=%s AND estado='activo'",
        (username,),
    )
    usuario = cursor.fetchone()
    conexion.close()

    if usuario and password_service.verify(password, usuario["password"]):
        return usuario

    return None


def existe_usuario(username, email):
    conexion = conectar()
    cursor = conexion.cursor()
    cursor.execute(
        "SELECT id FROM users WHERE username=%s OR email=%s",
        (username, email),
    )
    existente = cursor.fetchone()
    conexion.close()
    return existente is not None


def registrar(datos):
    conexion = conectar()
    cursor = conexion.cursor()

    sql = """
    INSERT INTO users
    (username, name, apellidos, documento_identidad, email, password, rol, estado)
    VALUES (%s, %s, %s, %s, %s, %s, 'usuario', 'activo')
    """

    cursor.execute(
        sql,
        (
            datos["username"],
            datos["name"],
            "Usuario",
            datos.get("documento_identidad", "").strip() or None,
            datos["email"],
            password_service.hash(datos["password"]),
        ),
    )

    conexion.commit()
    conexion.close()


def buscar_por_email(email):
    conexion = conectar()
    cursor = conexion.cursor()
    cursor.execute(
        "SELECT id, username, name, email, password FROM users "
        "WHERE email=%s AND estado='activo'",
        (email,),
    )
    usuario = cursor.fetchone()
    conexion.close()
    return usuario


def buscar_por_id(user_id):
    conexion = conectar()
    cursor = conexion.cursor()
    cursor.execute(
        "SELECT id, username, name, email, password FROM users "
        "WHERE id=%s AND estado='activo'",
        (user_id,),
    )
    usuario = cursor.fetchone()
    conexion.close()
    return usuario


# =========================
# TOKENS DE RECUPERACION
# =========================
# El token va firmado con la secret_key y caduca a los TOKEN_MAX_EDAD
# segundos. Incluye una huella del hash de la contraseña actual, asi
# que deja de valer en cuanto la contraseña cambia (un solo uso).

TOKEN_MAX_EDAD = 30 * 60
TOKEN_SALT = "recuperar-password"


def _serializer():
    return URLSafeTimedSerializer(current_app.secret_key, salt=TOKEN_SALT)


def _huella(password_hash):
    return hashlib.sha256(password_hash.encode()).hexdigest()[:16]


def generar_token_recuperacion(usuario):
    return _serializer().dumps({"id": usuario["id"], "h": _huella(usuario["password"])})


def verificar_token_recuperacion(token):
    try:
        datos = _serializer().loads(token, max_age=TOKEN_MAX_EDAD)
    except (BadSignature, SignatureExpired):
        return None

    usuario = buscar_por_id(datos.get("id"))
    if not usuario or datos.get("h") != _huella(usuario["password"]):
        return None

    return usuario


def cambiar_password(user_id, nueva_password):
    conexion = conectar()
    cursor = conexion.cursor()
    cursor.execute(
        "UPDATE users SET password=%s WHERE id=%s",
        (password_service.hash(nueva_password), user_id),
    )
    conexion.commit()
    conexion.close()
