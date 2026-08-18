from database.init_db import conectar


def obtener_pedidos(user_id):
    conexion = conectar()
    cursor = conexion.cursor()
    cursor.execute(
        "SELECT * FROM facturas WHERE user_id=%s ORDER BY fecha DESC",
        (user_id,),
    )
    pedidos = cursor.fetchall()
    conexion.close()
    return pedidos


def listar_pedidos():
    conexion = conectar()
    cursor = conexion.cursor()
    cursor.execute(
        """
        SELECT f.*, u.username AS cliente_usuario,
               u.name AS cliente_nombre, u.apellidos AS cliente_apellidos
        FROM facturas f
        JOIN users u ON u.id = f.user_id
        ORDER BY f.fecha DESC
        """
    )
    pedidos = cursor.fetchall()
    conexion.close()
    return pedidos
