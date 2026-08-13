import pymysql


def conectar():
    return pymysql.connect(
        host="localhost",
        user="root",
        password="",
        database="urbanstyle",
        port=3306,
        cursorclass=pymysql.cursors.DictCursor,
    )
