# =========================
# CRUD (Admin) Y PERFIL
# =========================

import pymysql

from app.utils.security import password_service
from database.init_db import conectar


def listar_usuarios():
    conexion = conectar()
    cursor = conexion.cursor()
    cursor.execute("SELECT * FROM users")
    usuarios = cursor.fetchall()
    conexion.close()
    return usuarios


def obtener_usuario(id):
    conexion = conectar()
    cursor = conexion.cursor()
    cursor.execute("SELECT * FROM users WHERE id=%s", (id,))
    usuario = cursor.fetchone()
    conexion.close()
    return usuario


def crear(datos):
    conexion = conectar()
    cursor = conexion.cursor()

    sql = """
    INSERT INTO users
    (username, name, apellidos, email, password, celular, fechanaci, rol, estado)
    VALUES (%s,%s,%s,%s,%s,%s,%s,%s,'activo')
    """

    cursor.execute(
        sql,
        (
            datos["username"],
            datos["name"],
            datos["apellidos"],
            datos["usuario_email"],
            password_service.hash(datos["password"]),
            datos["celular"],
            datos["fechanaci"],
            datos["rol"],
        ),
    )

    conexion.commit()
    conexion.close()


def eliminar(id):
    conexion = conectar()
    cursor = conexion.cursor()
    try:
        cursor.execute("DELETE FROM users WHERE id=%s", (id,))
        conexion.commit()
    except pymysql.err.IntegrityError:
        conexion.rollback()
    conexion.close()


def actualizar(id, datos):
    conexion = conectar()
    cursor = conexion.cursor()

    nueva_password = datos.get("password", "").strip()

    if nueva_password:
        cursor.execute(
            """
            UPDATE users
            SET username=%s, name=%s, apellidos=%s, email=%s, password=%s,
                celular=%s, fechanaci=%s, rol=%s
            WHERE id=%s
            """,
            (
                datos["username"],
                datos["name"],
                datos["apellidos"],
                datos["usuario_email"],
                password_service.hash(nueva_password),
                datos["celular"],
                datos["fechanaci"],
                datos["rol"],
                id,
            ),
        )
    else:
        cursor.execute(
            """
            UPDATE users
            SET username=%s, name=%s, apellidos=%s, email=%s,
                celular=%s, fechanaci=%s, rol=%s
            WHERE id=%s
            """,
            (
                datos["username"],
                datos["name"],
                datos["apellidos"],
                datos["usuario_email"],
                datos["celular"],
                datos["fechanaci"],
                datos["rol"],
                id,
            ),
        )

    conexion.commit()
    conexion.close()


def actualizar_avatar(id, nombre_archivo):
    conexion = conectar()
    cursor = conexion.cursor()
    cursor.execute(
        "UPDATE users SET avatar=%s WHERE id=%s",
        (nombre_archivo, id),
    )
    conexion.commit()
    conexion.close()


def actualizar_perfil(id, datos):
    conexion = conectar()
    cursor = conexion.cursor()

    nueva_password = datos.get("nueva_password", "").strip()

    if nueva_password:
        cursor.execute(
            "UPDATE users SET name=%s, apellidos=%s, email=%s, celular=%s, password=%s WHERE id=%s",
            (
                datos["name"],
                datos["apellidos"],
                datos["email"],
                datos.get("celular", ""),
                password_service.hash(nueva_password),
                id,
            ),
        )
    else:
        cursor.execute(
            "UPDATE users SET name=%s, apellidos=%s, email=%s, celular=%s WHERE id=%s",
            (
                datos["name"],
                datos["apellidos"],
                datos["email"],
                datos.get("celular", ""),
                id,
            ),
        )

    conexion.commit()
    conexion.close()
