import pymysql

def conectar():
    """Crea y retorna una nueva conexión a la base de datos."""
    try:
        return pymysql.connect(
            host="127.0.0.1",
            user="root",
            password="",
            database="urbanstyle",
            port=3306,# 
            cursorclass=pymysql.cursors.DictCursor,
            autocommit=True 
        )
    except pymysql.MySQLError as e:
        print(f"Error al conectar: {e}")
        return None
