from flask import Flask, render_template, request, redirect, url_for, session
import pymysql

app = Flask(__name__)

app.secret_key = "urbanstyle"

# CONEXION MYSQL

conexion = pymysql.connect(
    host="localhost",
    user="root",
    password="",
    database="urbanstyle",
    cursorclass=pymysql.cursors.DictCursor
)

# REGISTRO
@app.route("/register", methods=["GET", "POST"])
def register():

    if request.method == "POST":

        username = request.form["username"]
        name = request.form["name"]
        email = request.form["email"]
        password = request.form["password"]

        cursor = conexion.cursor()

        sql = """
        INSERT INTO users
        (username, name, apellidos, email, password)
        VALUES (%s, %s, %s, %s, %s)
        """

        cursor.execute(
            sql,
            (username, name, "Usuario", email, password)
        )

        conexion.commit()

        return redirect(url_for("login"))

    return render_template("register.html")

# HOME

@app.route("/")
def index():
    return render_template("index.html")

# CATEGORIES

@app.route("/categories")
def categories():
    return render_template("categories.html")

# PRODUCTS

@app.route("/products")
def products():

    cursor = conexion.cursor()

    sql = "SELECT * FROM productos"

    cursor.execute(sql)

    productos = cursor.fetchall()

    return render_template(
        "products.html",
        productos=productos
    )

# OFFERS

@app.route("/offers")
def offers():
    return render_template("offers.html")

# ABOUT

@app.route("/about")
def about():
    return render_template("about.html")

# LOGIN

@app.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        username = request.form["username"]
        password = request.form["password"]

        cursor = conexion.cursor()

        sql = """
        SELECT * FROM users
        WHERE username=%s AND password=%s
        """

        cursor.execute(sql, (username, password))

        user = cursor.fetchone()

        if user:

            session["user"] = user["username"]
            session["rol"] = user["rol"]

            return redirect(url_for("index"))

        else:

            return render_template(
                "login.html",
                message="Usuario o contraseña incorrectos"
            )

    return render_template("login.html")

# LOGOUT

@app.route("/logout")
def logout():

    session.clear()

    return redirect(url_for("login"))

# RUN

if __name__ == "__main__":
    app.run(debug=True)
