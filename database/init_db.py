import pymysql

def conectar():
    """Crea y retorna una nueva conexión a la base de datos.

    autocommit va apagado: cada escritura confirma con conexion.commit(),
    y asi los rollback() de los pedidos (crear_pedido, anular, cancelar)
    deshacen de verdad todo lo hecho si algo falla a mitad de camino.
    Si no se puede conectar, el error se propaga en vez de devolver None
    (ningun servicio sabria que hacer con una conexion None).
    """
    return pymysql.conne
        host="127.0.0.1",# Cambiar 'localhost' por '127.0.0.1' evita problemas
de DNS en Windows
        user="root",
        password="",
        database="urbanstyle",
        port=3306,# ¡Vere es el 3306 o el 3307!
        charset="utf8mb4",
        cursorclass=pymy
        autocommit=False,
    )