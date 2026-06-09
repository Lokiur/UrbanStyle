import re

import pymysql
from flask import Flask, redirect, render_template, request, session, url_for

app = Flask(__name__)
app.secret_key = "urbanstyle"

# =========================
# CONEXION MYSQL
# =========================


def conectar():
    return pymysql.connect(
        host="localhost",
        user="root",
        password="",
        database="urbanstyle",
        port=3306,
        cursorclass=pymysql.cursors.DictCursor,
    )


# =========================
# HOME
# =========================


@app.route("/")
def index():
    return render_template("index.html")


# =========================
# CATEGORIES
# =========================


@app.route("/categories")
def categories():
    return render_template("categories.html")


# =========================
# PRODUCTS
# =========================


@app.route("/products")
def products():
    conexion = conectar()
    cursor = conexion.cursor()
    cursor.execute("SELECT * FROM productos")
    productos = cursor.fetchall()
    conexion.close()
    return render_template("products.html", productos=productos)


# =========================
# PRODUCTOS POR CATEGORIA
# =========================


@app.route("/categoria/<int:id>")
def categoria_productos(id):
    conexion = conectar()
    cursor = conexion.cursor()
    cursor.execute("SELECT * FROM productos WHERE categoria_id = %s", (id,))
    productos = cursor.fetchall()
    conexion.close()
    return render_template("products.html", productos=productos)


# =========================
# OFFERS
# =========================


@app.route("/offers")
def offers():
    return render_template("offers.html")


# =========================
# ABOUT
# =========================


@app.route("/about")
def about():
    return render_template("about.html")


# =========================
# REGISTER
# =========================


@app.route("/register", methods=["GET", "POST"])
def register():

    if request.method == "POST":
        username = request.form["username"]
        name = request.form["name"]
        email = request.form["email"]
        password = request.form["password"]

        conexion = conectar()
        cursor = conexion.cursor()

        sql = """
        INSERT INTO users
        (username, name, apellidos, email, password, rol, estado)
        VALUES (%s, %s, %s, %s, %s, 'usuario', 'activo')
        """

        cursor.execute(sql, (username, name, "Usuario", email, password))

        conexion.commit()
        conexion.close()

        return redirect(url_for("login"))

    return render_template("register.html")


# =========================
# LOGIN
# =========================


@app.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        conexion = conectar()
        cursor = conexion.cursor()

        sql = """
        SELECT * FROM users
        WHERE username=%s
        AND password=%s
        AND estado='activo'
        """

        cursor.execute(sql, (username, password))
        user = cursor.fetchone()
        conexion.close()

        if user:
            session["user"] = user["username"]
            session["rol"] = user["rol"]
            return redirect(url_for("index"))

        return render_template("login.html", message="Usuario o contraseña incorrectos")

    return render_template("login.html")


# =========================
# PANEL ADMIN
# =========================


@app.route("/admin")
def admin_panel():

    if session.get("rol") != "admin":
        return redirect(url_for("index"))

    conexion = conectar()
    cursor = conexion.cursor()
    cursor.execute("SELECT * FROM users")
    users = cursor.fetchall()
    conexion.close()

    return render_template("indexmvc.html", users=users)


# =========================
# CRUD ADMIN
# =========================


# CREAR
@app.route("/usuario", methods=["POST"])
def crear_usuario():

    if session.get("rol") != "admin":
        return redirect(url_for("index"))

    username = request.form["username"]
    name = request.form["name"]
    apellidos = request.form["apellidos"]
    email = request.form["usuario_email"]
    password = request.form["password"]
    celular = request.form["celular"]
    fechanaci = request.form["fechanaci"]

    rol = request.form["rol"]

    conexion = conectar()
    cursor = conexion.cursor()

    sql = """
    INSERT INTO users
    (username, name, apellidos, email, password, celular, fechanaci, rol, estado)
    VALUES (%s,%s,%s,%s,%s,%s,%s,%s,'activo')
    """

    cursor.execute(
        sql, (username, name, apellidos, email, password, celular, fechanaci, rol)
    )

    conexion.commit()
    conexion.close()

    return redirect(url_for("admin_panel"))


# ELIMINAR
@app.route("/delete/<int:id>")
def delete(id):

    if session.get("rol") != "admin":
        return redirect(url_for("index"))

    conexion = conectar()
    cursor = conexion.cursor()
    cursor.execute("DELETE FROM users WHERE id=%s", (id,))
    conexion.commit()
    conexion.close()

    return redirect(url_for("admin_panel"))


# EDITAR
@app.route("/edit/<int:id>", methods=["POST"])
def edit(id):

    if session.get("rol") != "admin":
        return redirect(url_for("index"))

    username = request.form["username"]
    name = request.form["name"]
    apellidos = request.form["apellidos"]
    email = request.form["usuario_email"]
    password = request.form["password"]
    celular = request.form["celular"]
    fechanaci = request.form["fechanaci"]
    rol = request.form["rol"]

    conexion = conectar()
    cursor = conexion.cursor()

    sql = """
    UPDATE users
    SET username=%s,
        name=%s,
        apellidos=%s,
        email=%s,
        password=%s,
        celular=%s,
        fechanaci=%s,
        rol=%s
    WHERE id=%s
    """

    cursor.execute(
        sql, (username, name, apellidos, email, password, celular, fechanaci, rol, id)
    )

    conexion.commit()
    conexion.close()

    return redirect(url_for("admin_panel"))


# =========================
# LOGOUT
# =========================


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))


# =========================
# RUN
# =========================

if __name__ == "__main__":
    app.run(debug=True)
