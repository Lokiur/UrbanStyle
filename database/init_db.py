import os

import pymysql


def conectar():
    """Crea y retorna una nueva conexión a la base de datos.

    Los datos de conexion salen de variables de entorno (.env en local,
    el dashboard del hosting en produccion). Si no estan definidas, cae
    a los valores de un XAMPP local para no romper el flujo de desarrollo.

    autocommit va apagado: cada escritura confirma con conexion.commit(),
    y asi los rollback() de los pedidos (crear_pedido, anular, cancelar)
    deshacen de verdad todo lo hecho si algo falla a mitad de camino.
    Si no se puede conectar, el error se propaga en vez de devolver None
    (ningun servicio sabria que hacer con una conexion None).
    """
    conexion_kwargs = dict(
        host=os.environ.get("DB_HOST", "127.0.0.1"),
        user=os.environ.get("DB_USER", "root"),
        password=os.environ.get("DB_PASSWORD", ""),
        database=os.environ.get("DB_NAME", "urbanstyle"),
        port=int(os.environ.get("DB_PORT", "3306")),
        charset="utf8mb4",
        cursorclass=pymysql.cursors.DictCursor,
        autocommit=False,
    )

    # algunos proveedores de MySQL externos (Aiven, TiDB Cloud, etc.) exigen
    # TLS; sin certificado especifico, un dict vacio alcanza para activarlo.
    if os.environ.get("DB_SSL", "").lower() in ("1", "true", "yes"):
        conexion_kwargs["ssl"] = {"ssl": {}}

    return pymysql.connect(**conexion_kwargs)
