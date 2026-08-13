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
