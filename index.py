import os

from flask import Flask, redirect, render_template, request, session, url_for

import database as db

# =============================
# CONFIGURACIÓN GENERAL
# =============================

template_dir = os.path.dirname(os.path.abspath(os.path.dirname(__file__)))
template_dir = os.path.join(template_dir, "UrbanStyle", "templates")

app = Flask(__name__, template_folder=template_dir)
app.secret_key = "supersecretkey"

# Cursor global
cursor = db.database.cursor(dictionary=True)

# =============================
# LOGIN
# =============================


@app.route("/")
def index():
    return render_template("login.html")


@app.route("/login", methods=["POST"])
def login():
    username = request.form["username"]
    password = request.form["password"]

    cursor.execute(
        """
        SELECT id, username, rol
        FROM users
        WHERE username = %s
        AND password = %s
        AND estado = 'activo'
        """,
        (username, password),
    )

    usuario = cursor.fetchone()

    if usuario:
        session["user_id"] = usuario["id"]
        session["username"] = usuario["username"]
        session["rol"] = usuario["rol"]
        return redirect("/dashboard")

    return render_template(
        "login.html", message="Credenciales incorrectas o usuario inactivo"
    )


@app.route("/dashboard")
def dashboard():
    if "username" in session:
        return redirect("/home")
    return redirect("/")


@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")


# =============================
# HOME (MVC)
# =============================


@app.route("/home")
def home():
    if "username" not in session:
        return redirect("/")

    cursor = db.database.cursor(dictionary=True)
    cursor.execute("SELECT * FROM users")
    usuarios = cursor.fetchall()
    cursor.close()

    return render_template("indexmvc.html", data=usuarios)


# =============================
# CREAR USUARIO
# =============================


@app.route("/usuario", methods=["POST"])
def addUser():
    username = request.form["username"]
    name = request.form["name"]
    apellidos = request.form["apellidos"]
    password = request.form["password"]
    email = request.form.get("usuario_email")  # ← nombre del form, NO se toca
    celular = request.form["celular"]
    fechanaci = request.form["fechanaci"]

    if all([username, name, apellidos, password, email, celular, fechanaci]):
        cursor = db.database.cursor()
        cursor.execute(
            """
            INSERT INTO users
            (username, name, apellidos, email, password, celular, fechanaci, rol, estado)
            VALUES (%s,%s,%s,%s,%s,%s,%s,'usuario','activo')
            """,
            (username, name, apellidos, email, password, celular, fechanaci),
        )
        db.database.commit()

    return redirect(url_for("home"))


# =============================
# ELIMINAR USUARIO
# =============================


@app.route("/delete/<string:id>")
def delete(id):
    cursor = db.database.cursor()
    cursor.execute("DELETE FROM users WHERE id = %s", (id,))
    db.database.commit()
    return redirect(url_for("home"))


# =============================
# EDITAR USUARIO
# =============================


@app.route("/edit/<string:id>", methods=["POST"])
def edit(id):
    username = request.form["username"]
    name = request.form["name"]
    apellidos = request.form["apellidos"]
    password = request.form["password"]
    email = request.form.get("usuario_email")
    celular = request.form["celular"]
    fechanaci = request.form["fechanaci"]

    if all([username, name, apellidos, password, email, celular, fechanaci]):
        cursor = db.database.cursor()
        cursor.execute(
            """
            UPDATE users
            SET username=%s,
                name=%s,
                apellidos=%s,
                password=%s,
                email=%s,
                celular=%s,
                fechanaci=%s
            WHERE id=%s
            """,
            (username, name, apellidos, password, email, celular, fechanaci, id),
        )
        db.database.commit()

    return redirect(url_for("home"))


# =============================
# RUTAS EXTRA (SIN MODIFICAR)
# =============================


@app.route("/lenguajes")
def mostrarLenguajes():
    MisLenguajes = ("PHP", "PYTHON", "Java", "c#", "JavaScript", "Perl", "Ruby", "Rust")
    return render_template("lenguajes.html", lenguajes=MisLenguajes)


@app.route("/contacto")
def contacto():
    return render_template("contacto.html")


@app.route("/micurriculum")
def micurriculum():
    return render_template("micurriculum.html")


# =============================
# RUN
# =============================

if __name__ == "__main__":
    app.run(debug=True, port=5600)
