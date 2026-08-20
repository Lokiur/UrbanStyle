# =========================
# MENSAJES DE CONTACTO
# =========================

from database.init_db import conectar


def crear_mensaje(datos):
    conexion = conectar()
    cursor = conexion.cursor()
    cursor.execute(
        "INSERT INTO mensajes (nombre, email, mensaje) VALUES (%s, %s, %s)",
        (datos["nombre"], datos["email"], datos["mensaje"]),
    )
    conexion.commit()
    conexion.close()


def listar_mensajes():
    conexion = conectar()
    cursor = conexion.cursor()
    cursor.execute("SELECT * FROM mensajes ORDER BY fecha DESC")
    mensajes = cursor.fetchall()
    conexion.close()
    return mensajes


def marcar_leido(id):
    conexion = conectar()
    cursor = conexion.cursor()
    cursor.execute("UPDATE mensajes SET estado='leido' WHERE id=%s", (id,))
    conexion.commit()
    conexion.close()


def eliminar_mensaje(id):
    conexion = conectar()
    cursor = conexion.cursor()
    cursor.execute("DELETE FROM mensajes WHERE id=%s", (id,))
    conexion.commit()
    conexion.close()
