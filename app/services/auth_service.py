# =========================
# LOGIN / REGISTRO / RECUPERACION
# =========================

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


def buscar_por_documento(username, documento_identidad):
    conexion = conectar()
    cursor = conexion.cursor()
    cursor.execute(
        "SELECT id FROM users WHERE username=%s AND documento_identidad=%s",
        (username, documento_identidad),
    )
    usuario = cursor.fetchone()
    conexion.close()
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
