# =========================
# CRUD (Admin) Y PERFIL
# =========================

import pymysql

from app.services.products_service import _leer_imagen
from app.utils.security import password_service
from database.init_db import conectar

# columnas de `users` sin `avatar_imagen`: es un longblob y listarla en
# bloque (SELECT *) traeria la foto de cada usuario completa solo para
# mostrar una tabla o rellenar un formulario que no la necesita.
_COLUMNAS_USUARIO = """
    id, username, name, apellidos, documento_identidad, email, password,
    celular, avatar_mime, fechanaci, rol, estado, created_at, updated_at,
    (avatar_imagen IS NOT NULL) AS tiene_avatar
"""


def listar_usuarios():
    conexion = conectar()
    cursor = conexion.cursor()
    cursor.execute(f"SELECT {_COLUMNAS_USUARIO} FROM users")
    usuarios = cursor.fetchall()
    conexion.close()
    return usuarios


def listar_clientes():
    """Clientes de la tienda (rol 'usuario', sin cuentas de admin), para
    la consulta de clientes del panel admin.
    """
    conexion = conectar()
    cursor = conexion.cursor()
    cursor.execute(
        "SELECT id, name, apellidos, email, celular FROM users WHERE rol='usuario' ORDER BY name"
    )
    clientes = cursor.fetchall()
    conexion.close()
    return clientes


def obtener_usuario(id):
    conexion = conectar()
    cursor = conexion.cursor()
    cursor.execute(f"SELECT {_COLUMNAS_USUARIO} FROM users WHERE id=%s", (id,))
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


def actualizar_avatar(id, archivo_imagen):
    """Guarda la foto de perfil como BLOB (igual que las imagenes de
    producto/categoria): sobrevive a un redeploy con disco efimero.

    Lanza ValueError si el archivo no es una imagen valida (ver
    `products_service._leer_imagen`).
    """
    imagen, mime = _leer_imagen(archivo_imagen)
    if imagen is None:
        return

    conexion = conectar()
    cursor = conexion.cursor()
    try:
        cursor.execute(
            "UPDATE users SET avatar_imagen=%s, avatar_mime=%s WHERE id=%s",
            (imagen, mime, id),
        )
        conexion.commit()
    except pymysql.err.OperationalError:
        conexion.rollback()
        raise ValueError(
            "No se pudo guardar la imagen en la base de datos, prueba con una más liviana"
        )
    finally:
        conexion.close()


def obtener_imagen_avatar(id):
    conexion = conectar()
    cursor = conexion.cursor()
    cursor.execute(
        "SELECT avatar_imagen, avatar_mime FROM users WHERE id=%s", (id,)
    )
    fila = cursor.fetchone()
    conexion.close()
    return fila


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
