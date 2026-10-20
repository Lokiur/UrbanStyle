import os

import pymysql
from dbutils.pooled_db import PooledDB

_pool = None


def _conexion_kwargs():
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

    return conexion_kwargs


def _obtener_pool():
    global _pool
    if _pool is None:
        # maxconnections es por proceso: con N workers de Gunicorn, el total
        # de conexiones al MySQL externo puede llegar a N * DB_POOL_SIZE.
        # El default (3) se mantiene bajo a proposito porque varios
        # proveedores de MySQL gratuitos limitan las conexiones simultaneas.
        _pool = PooledDB(
            creator=pymysql,
            maxconnections=int(os.environ.get("DB_POOL_SIZE", "3")),
            blocking=True,
            # revisa (y reabre si hace falta) la conexion antes de prestarla:
            # evita el error "MySQL server has gone away" cuando el proveedor
            # cierra conexiones ociosas por inactividad.
            ping=1,
            **_conexion_kwargs(),
        )
    return _pool


def conectar():
    """Toma una conexión del pool en vez de abrir una nueva por llamada.

    Con la BD en un host remoto, cada conexión nueva paga el handshake
    TCP + TLS + autenticación completo; esta app llama conectar() varias
    veces por request (una por cada función de los *_service.py), asi
    que reusar conexiones ya abiertas es la mejora de latencia mas
    grande posible sin depender del hosting.

    `.commit()`, `.rollback()` y `.cursor()` funcionan igual que antes;
    `.close()` ya no cierra el socket, devuelve la conexión al pool para
    la siguiente llamada.
    """
    return _obtener_pool().connection()
