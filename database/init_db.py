import pymysql

def conectar():
    """Crea y retorna una nueva conexión a la base de datos."""
    try:
        return pymysql.connect(
            host="127.0.0.1",# Cambiar 'localhost' por '127.0.0.1' evita problemas de DNS en Windows
            user="root",
            password="",
            database="urbanstyle",
            port=3306,# ¡Verifica en tu XAMPP si realmente es el 3306 o el 3307!
            cursorclass=pymysql.cursors.DictCursor,
            autocommit=True # Evita transacciones bloqueadas
        )
    except pymysql.MySQLError as e:
        print(f"Error al conectar: {e}")
        return None
