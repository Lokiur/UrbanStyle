import random
from decimal import Decimal
from functools import wraps

import pymysql
from flask import Flask, redirect, render_template, request, session, url_for
from werkzeug.security import check_password_hash, generate_password_hash

app = Flask(__name__)
app.secret_key = "urbanstyle"


class password:
    def hash(self, plain_password):
        return generate_password_hash(plain_password)

    def verify(self, plain_password, hashed_password):
        return check_password_hash(hashed_password, plain_password)

    def validate(self, plain_password):
        if not isinstance(plain_password, str):
            return False
        if len(plain_password) < 8:
            return False
        has_letter = any(ch.isalpha() for ch in plain_password)
        has_digit = any(ch.isdigit() for ch in plain_password)
        return has_letter and has_digit


password_service = password()

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
# HELPERS DE PRODUCTOS Y CARRITO
# =========================


def obtener_productos(cursor, condicion="", parametros=()):
    sql = """
        SELECT p.*,
               MIN(e.precio) AS precio_desde,
               COALESCE(SUM(e.stock), 0) AS stock_total,
               i.imagen AS imagen
        FROM productos p
        LEFT JOIN existencias e ON e.producto_id = p.id AND e.estado = 'activo'
        LEFT JOIN imagenes_producto i ON i.producto_id = p.id AND i.principal = 1
        WHERE p.estado = 'activo'
    """
    if condicion:
        sql += f" AND {condicion}"
    sql += " GROUP BY p.id"
    cursor.execute(sql, parametros)
    productos = cursor.fetchall()

    if not productos:
        return productos

    ids = [p["id"] for p in productos]
    formato = ",".join(["%s"] * len(ids))
    cursor.execute(
        f"""
        SELECT e.id AS existencia_id, e.producto_id, e.precio, e.stock,
               t.id AS talla_id, t.nombre AS talla
        FROM existencias e
        JOIN tallas t ON t.id = e.talla_id
        WHERE e.producto_id IN ({formato}) AND e.estado = 'activo'
        ORDER BY t.id, e.precio ASC
        """,
        ids,
    )

    tallas_por_producto = {}
    for fila in cursor.fetchall():
        vistas = tallas_por_producto.setdefault(fila["producto_id"], {})
        # una talla puede tener varios colores: nos quedamos con la primera
        # existencia (la de menor precio, por el ORDER BY) por cada talla
        vistas.setdefault(
            fila["talla_id"],
            {
                "talla_id": fila["talla_id"],
                "nombre": fila["talla"],
                "existencia_id": fila["existencia_id"],
                "precio": fila["precio"],
                "stock": fila["stock"],
            },
        )

    for producto in productos:
        producto["tallas"] = list(tallas_por_producto.get(producto["id"], {}).values())

    return productos


def obtener_items_carrito(cursor, user_id):
    cursor.execute(
        """
        SELECT dc.id AS detalle_id, dc.cantidad, e.id AS existencia_id, e.precio,
               p.id AS producto_id, p.nombre AS producto_nombre,
               t.nombre AS talla, col.nombre AS color,
               (e.precio * dc.cantidad) AS subtotal,
               i.imagen AS imagen
        FROM carrito c
        JOIN detalle_carrito dc ON dc.carrito_id = c.id
        JOIN existencias e ON e.id = dc.existencia_id
        JOIN productos p ON p.id = e.producto_id
        JOIN tallas t ON t.id = e.talla_id
        JOIN colores col ON col.id = e.color_id
        LEFT JOIN imagenes_producto i ON i.producto_id = p.id AND i.principal = 1
        WHERE c.user_id = %s
        ORDER BY dc.id
        """,
        (user_id,),
    )
    return cursor.fetchall()


@app.context_processor
def inject_carrito_count():
    count = 0
    if "user_id" in session:
        conexion = conectar()
        cursor = conexion.cursor()
        cursor.execute(
            """
            SELECT COALESCE(SUM(dc.cantidad), 0) AS total
            FROM carrito c
            JOIN detalle_carrito dc ON dc.carrito_id = c.id
            WHERE c.user_id = %s
            """,
            (session["user_id"],),
        )
        row = cursor.fetchone()
        count = row["total"] if row else 0
        conexion.close()
    return dict(carrito_count=count)


# =========================
# DECORADORES DE ACCESO
# =========================


def login_required(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        if "user" not in session:
            return redirect(url_for("login"))
        return f(*args, **kwargs)

    return wrapper


def admin_required(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        if session.get("rol") != "admin":
            return redirect(url_for("index"))
        return f(*args, **kwargs)

    return wrapper


# =========================
# CAPTCHA (suma simple)
# =========================


def generar_captcha():
    a, b = random.randint(1, 9), random.randint(1, 9)
    session["captcha_a"] = a
    session["captcha_b"] = b
    return a, b


def captcha_valido(respuesta):
    esperado = session.pop("captcha_a", None), session.pop("captcha_b", None)
    if None in esperado:
        return False
    try:
        return int(respuesta) == sum(esperado)
    except (TypeError, ValueError):
        return False


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
    productos = obtener_productos(cursor)
    conexion.close()
    return render_template("products.html", productos=productos)


# =========================
# PRODUCTOS POR CATEGORIA
# =========================


@app.route("/categoria/<int:id>")
def categoria_productos(id):
    conexion = conectar()
    cursor = conexion.cursor()
    productos = obtener_productos(cursor, "p.categoria_id = %s", (id,))
    conexion.close()
    return render_template("products.html", productos=productos)


# =========================
# BUSCADOR
# =========================


@app.route("/buscar")
def buscar():
    query = request.args.get("q", "").strip()
    productos = []

    if query:
        conexion = conectar()
        cursor = conexion.cursor()
        like = f"%{query}%"
        productos = obtener_productos(
            cursor, "(p.nombre LIKE %s OR p.descripcion LIKE %s)", (like, like)
        )
        conexion.close()

    return render_template("products.html", productos=productos, query=query)


# =========================
# CARRITO
# =========================


ENVIO_COSTO = Decimal("12000")
IVA_PORCENTAJE = Decimal("0.19")


@app.route("/carrito")
@login_required
def ver_carrito():
    conexion = conectar()
    cursor = conexion.cursor()
    items = obtener_items_carrito(cursor, session["user_id"])

    cursor.execute(
        "SELECT * FROM direcciones WHERE user_id=%s ORDER BY principal DESC, id",
        (session["user_id"],),
    )
    direcciones = cursor.fetchall()

    cursor.execute(
        "SELECT * FROM metodos_pago WHERE estado='activo' ORDER BY nombre"
    )
    metodos_pago = cursor.fetchall()

    conexion.close()

    subtotal = sum((item["subtotal"] for item in items), Decimal("0"))
    iva = subtotal * IVA_PORCENTAJE
    envio = ENVIO_COSTO if items else Decimal("0")
    total_final = subtotal + iva + envio

    return render_template(
        "carrito.html",
        items=items,
        total=subtotal,
        iva=iva,
        envio=envio,
        total_final=total_final,
        direcciones=direcciones,
        metodos_pago=metodos_pago,
    )


@app.route("/carrito/confirmar", methods=["POST"])
@login_required
def carrito_confirmar():
    conexion = conectar()
    cursor = conexion.cursor()

    items = obtener_items_carrito(cursor, session["user_id"])
    if not items:
        conexion.close()
        return redirect(url_for("ver_carrito"))

    metodo_pago_id = request.form.get("metodo_pago_id", type=int)
    direccion_raw = request.form.get("direccion_id", "")

    if direccion_raw == "nueva":
        direccion_txt = request.form.get("direccion", "").strip()
        ciudad = request.form.get("ciudad", "").strip()
        departamento = request.form.get("departamento", "").strip()
        codigo_postal = request.form.get("codigo_postal", "").strip()

        if not direccion_txt or not ciudad:
            conexion.close()
            return redirect(url_for("ver_carrito"))

        # nota: la tabla `direcciones` tiene un trigger BEFORE INSERT que falla
        # con error 1442 si se inserta con principal=1 (bug del propio trigger,
        # reproducible incluso desde un INSERT plano fuera de esta app), por lo
        # que las direcciones nuevas siempre se insertan con principal=0.
        cursor.execute(
            """
            INSERT INTO direcciones (user_id, direccion, ciudad, departamento, codigo_postal, principal)
            VALUES (%s, %s, %s, %s, %s, 0)
            """,
            (session["user_id"], direccion_txt, ciudad, departamento or None, codigo_postal or None),
        )
        direccion_id = cursor.lastrowid
    else:
        direccion_id = int(direccion_raw) if direccion_raw.isdigit() else None
        if direccion_id:
            cursor.execute(
                "SELECT id FROM direcciones WHERE id=%s AND user_id=%s",
                (direccion_id, session["user_id"]),
            )
            if not cursor.fetchone():
                direccion_id = None

    if not direccion_id or not metodo_pago_id:
        conexion.close()
        return redirect(url_for("ver_carrito"))

    subtotal = sum((item["subtotal"] for item in items), Decimal("0"))
    iva = subtotal * IVA_PORCENTAJE
    envio = ENVIO_COSTO
    total = subtotal + iva + envio

    cursor.execute(
        """
        INSERT INTO facturas
        (user_id, direccion_id, metodo_pago_id, subtotal, iva, envio, total, estado)
        VALUES (%s, %s, %s, %s, %s, %s, %s, 'activa')
        """,
        (session["user_id"], direccion_id, metodo_pago_id, subtotal, iva, envio, total),
    )
    factura_id = cursor.lastrowid

    numero_factura = f"FAC-{factura_id:04d}"
    cursor.execute(
        "UPDATE facturas SET numero_factura=%s WHERE id=%s",
        (numero_factura, factura_id),
    )

    for item in items:
        cursor.execute(
            """
            INSERT INTO detalle_factura (factura_id, existencia_id, cantidad, precio_unitario, subtotal)
            VALUES (%s, %s, %s, %s, %s)
            """,
            (factura_id, item["existencia_id"], item["cantidad"], item["precio"], item["subtotal"]),
        )

    cursor.execute(
        """
        DELETE dc FROM detalle_carrito dc
        JOIN carrito c ON c.id = dc.carrito_id
        WHERE c.user_id=%s
        """,
        (session["user_id"],),
    )

    conexion.commit()
    conexion.close()

    return redirect(url_for("mis_pedidos", ok=1))


@app.route("/carrito/agregar/<int:producto_id>", methods=["POST"])
@login_required
def carrito_agregar(producto_id):
    conexion = conectar()
    cursor = conexion.cursor()

    existencia_id = request.form.get("existencia_id", type=int)
    existencia = None

    if existencia_id:
        cursor.execute(
            """
            SELECT id FROM existencias
            WHERE id=%s AND producto_id=%s AND estado='activo' AND stock>0
            """,
            (existencia_id, producto_id),
        )
        existencia = cursor.fetchone()

    if not existencia:
        cursor.execute(
            """
            SELECT id FROM existencias
            WHERE producto_id=%s AND estado='activo' AND stock>0
            ORDER BY precio ASC LIMIT 1
            """,
            (producto_id,),
        )
        existencia = cursor.fetchone()

    if existencia:
        cursor.execute(
            "SELECT id FROM carrito WHERE user_id=%s ORDER BY id DESC LIMIT 1",
            (session["user_id"],),
        )
        carrito = cursor.fetchone()

        if carrito:
            carrito_id = carrito["id"]
        else:
            cursor.execute(
                "INSERT INTO carrito (user_id) VALUES (%s)", (session["user_id"],)
            )
            carrito_id = cursor.lastrowid

        cursor.execute(
            "SELECT id FROM detalle_carrito WHERE carrito_id=%s AND existencia_id=%s",
            (carrito_id, existencia["id"]),
        )
        detalle = cursor.fetchone()

        if detalle:
            cursor.execute(
                "UPDATE detalle_carrito SET cantidad = cantidad + 1 WHERE id=%s",
                (detalle["id"],),
            )
        else:
            cursor.execute(
                """
                INSERT INTO detalle_carrito (carrito_id, existencia_id, cantidad)
                VALUES (%s, %s, 1)
                """,
                (carrito_id, existencia["id"]),
            )

        conexion.commit()

    conexion.close()
    return redirect(url_for("ver_carrito"))


@app.route("/carrito/sumar/<int:detalle_id>", methods=["POST"])
@login_required
def carrito_sumar(detalle_id):
    conexion = conectar()
    cursor = conexion.cursor()
    cursor.execute(
        """
        UPDATE detalle_carrito dc
        JOIN carrito c ON c.id = dc.carrito_id
        SET dc.cantidad = dc.cantidad + 1
        WHERE dc.id=%s AND c.user_id=%s
        """,
        (detalle_id, session["user_id"]),
    )
    conexion.commit()
    conexion.close()
    return redirect(url_for("ver_carrito"))


@app.route("/carrito/restar/<int:detalle_id>", methods=["POST"])
@login_required
def carrito_restar(detalle_id):
    conexion = conectar()
    cursor = conexion.cursor()
    cursor.execute(
        """
        SELECT dc.id, dc.cantidad FROM detalle_carrito dc
        JOIN carrito c ON c.id = dc.carrito_id
        WHERE dc.id=%s AND c.user_id=%s
        """,
        (detalle_id, session["user_id"]),
    )
    detalle = cursor.fetchone()

    if detalle:
        if detalle["cantidad"] <= 1:
            cursor.execute("DELETE FROM detalle_carrito WHERE id=%s", (detalle_id,))
        else:
            cursor.execute(
                "UPDATE detalle_carrito SET cantidad = cantidad - 1 WHERE id=%s",
                (detalle_id,),
            )
        conexion.commit()

    conexion.close()
    return redirect(url_for("ver_carrito"))


@app.route("/carrito/eliminar/<int:detalle_id>", methods=["POST"])
@login_required
def carrito_eliminar(detalle_id):
    conexion = conectar()
    cursor = conexion.cursor()
    cursor.execute(
        """
        DELETE dc FROM detalle_carrito dc
        JOIN carrito c ON c.id = dc.carrito_id
        WHERE dc.id=%s AND c.user_id=%s
        """,
        (detalle_id, session["user_id"]),
    )
    conexion.commit()
    conexion.close()
    return redirect(url_for("ver_carrito"))


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
# CONTACTO
# =========================


@app.route("/contacto")
def contacto():
    return render_template("contacto.html")


# =========================
# PREGUNTAS FRECUENTES
# =========================


@app.route("/preguntas-frecuentes")
def faq():
    return render_template("faq.html")


# =========================
# TERMINOS Y CONDICIONES
# =========================


@app.route("/terminos")
def terminos():
    return render_template("terminos.html")


# =========================
# REGISTER
# =========================


@app.route("/register", methods=["GET", "POST"])
def register():

    if request.method == "POST":
        username = request.form["username"]
        name = request.form["name"]
        documento_identidad = request.form.get("documento_identidad", "").strip()
        email = request.form["email"]
        password = request.form["password"]

        if not password_service.validate(password):
            a, b = generar_captcha()
            return render_template(
                "register.html",
                message="La contraseña debe tener al menos 8 caracteres e incluir letras y números.",
                captcha_a=a,
                captcha_b=b,
            )

        captcha = request.form.get("captcha", "")

        a, b = session.get("captcha_a"), session.get("captcha_b")

        if not captcha_valido(captcha):
            a, b = generar_captcha()
            return render_template(
                "register.html",
                message="Captcha incorrecto, intenta de nuevo.",
                captcha_a=a,
                captcha_b=b,
            )

        conexion = conectar()
        cursor = conexion.cursor()

        cursor.execute(
            "SELECT id FROM users WHERE username=%s OR email=%s",
            (username, email),
        )
        existente = cursor.fetchone()

        if existente:
            conexion.close()
            a, b = generar_captcha()
            return render_template(
                "register.html",
                message="Ese usuario o correo ya está registrado.",
                captcha_a=a,
                captcha_b=b,
            )

        sql = """
        INSERT INTO users
        (username, name, apellidos, documento_identidad, email, password, rol, estado)
        VALUES (%s, %s, %s, %s, %s, %s, 'usuario', 'activo')
        """

        cursor.execute(
            sql,
            (
                username,
                name,
                "Usuario",
                documento_identidad or None,
                email,
                password_service.hash(password),
            ),
        )

        conexion.commit()
        conexion.close()

        return redirect(url_for("login"))

    a, b = generar_captcha()
    return render_template("register.html", captcha_a=a, captcha_b=b)


# =========================
# LOGIN
# =========================


@app.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        captcha = request.form.get("captcha", "")

        if not captcha_valido(captcha):
            a, b = generar_captcha()
            return render_template(
                "login.html",
                message="Captcha incorrecto, intenta de nuevo.",
                captcha_a=a,
                captcha_b=b,
            )

        conexion = conectar()
        cursor = conexion.cursor()

        sql = "SELECT * FROM users WHERE username=%s AND estado='activo'"

        cursor.execute(sql, (username,))
        user = cursor.fetchone()
        conexion.close()

        if user and password_service.verify(password, user["password"]):
            session["user"] = user["username"]
            session["user_id"] = user["id"]
            session["name"] = user["name"]
            session["rol"] = user["rol"]
            return redirect(url_for("index"))

        a, b = generar_captcha()
        return render_template(
            "login.html",
            message="Usuario o contraseña incorrectos",
            captcha_a=a,
            captcha_b=b,
        )

    a, b = generar_captcha()
    return render_template("login.html", captcha_a=a, captcha_b=b)


# =========================
# RECUPERAR CONTRASEÑA
# =========================


@app.route("/recuperar", methods=["GET", "POST"])
def recuperar():

    if request.method == "POST":
        username = request.form["username"]
        documento_identidad = request.form["documento_identidad"]
        nueva_password = request.form["nueva_password"]

        if not password_service.validate(nueva_password):
            a, b = generar_captcha()
            return render_template(
                "recuperar.html",
                message="La contraseña debe tener al menos 8 caracteres e incluir letras y números.",
                captcha_a=a,
                captcha_b=b,
            )

        captcha = request.form.get("captcha", "")

        if not captcha_valido(captcha):
            a, b = generar_captcha()
            return render_template(
                "recuperar.html",
                message="Captcha incorrecto, intenta de nuevo.",
                captcha_a=a,
                captcha_b=b,
            )

        conexion = conectar()
        cursor = conexion.cursor()

        cursor.execute(
            "SELECT id FROM users WHERE username=%s AND documento_identidad=%s",
            (username, documento_identidad),
        )
        user = cursor.fetchone()

        if not user:
            conexion.close()
            a, b = generar_captcha()
            return render_template(
                "recuperar.html",
                message="El usuario o el documento de identidad no coinciden.",
                captcha_a=a,
                captcha_b=b,
            )

        cursor.execute(
            "UPDATE users SET password=%s WHERE id=%s",
            (password_service.hash(nueva_password), user["id"]),
        )
        conexion.commit()
        conexion.close()

        return redirect(url_for("login"))

    a, b = generar_captcha()
    return render_template("recuperar.html", captcha_a=a, captcha_b=b)


# =========================
# PERFIL DE USUARIO
# =========================


@app.route("/perfil", methods=["GET", "POST"])
@login_required
def perfil():
    conexion = conectar()
    cursor = conexion.cursor()

    if request.method == "POST":
        name = request.form["name"]
        apellidos = request.form["apellidos"]
        email = request.form["email"]
        celular = request.form.get("celular", "")
        nueva_password = request.form.get("nueva_password", "").strip()

        if nueva_password:
            cursor.execute(
                "UPDATE users SET name=%s, apellidos=%s, email=%s, celular=%s, password=%s WHERE id=%s",
                (
                    name,
                    apellidos,
                    email,
                    celular,
                    password_service.hash(nueva_password),
                    session["user_id"],
                ),
            )
        else:
            cursor.execute(
                "UPDATE users SET name=%s, apellidos=%s, email=%s, celular=%s WHERE id=%s",
                (name, apellidos, email, celular, session["user_id"]),
            )

        conexion.commit()
        session["name"] = name

    cursor.execute("SELECT * FROM users WHERE id=%s", (session["user_id"],))
    usuario = cursor.fetchone()
    conexion.close()

    return render_template("perfil.html", usuario=usuario)


# =========================
# MIS PEDIDOS
# =========================


@app.route("/mis-pedidos")
@login_required
def mis_pedidos():
    conexion = conectar()
    cursor = conexion.cursor()
    cursor.execute(
        "SELECT * FROM facturas WHERE user_id=%s ORDER BY fecha DESC",
        (session["user_id"],),
    )
    pedidos = cursor.fetchall()
    conexion.close()
    return render_template("mis_pedidos.html", pedidos=pedidos)


# =========================
# PANEL ADMIN
# =========================


@app.route("/admin")
@admin_required
def admin_panel():
    conexion = conectar()
    cursor = conexion.cursor()
    cursor.execute("SELECT * FROM users")
    users = cursor.fetchall()

    cursor.execute(
        """
        SELECT p.*, c.nombre AS categoria_nombre, m.nombre AS marca_nombre
        FROM productos p
        JOIN categorias c ON c.id = p.categoria_id
        JOIN marcas m ON m.id = p.marca_id
        """
    )
    productos = cursor.fetchall()

    cursor.execute("SELECT * FROM categorias")
    categorias = cursor.fetchall()

    cursor.execute("SELECT * FROM marcas")
    marcas = cursor.fetchall()

    conexion.close()

    return render_template(
        "indexmvc.html",
        users=users,
        productos=productos,
        categorias=categorias,
        marcas=marcas,
    )


# =========================
# CRUD ADMIN - USUARIOS
# =========================


# CREAR
@app.route("/usuario", methods=["POST"])
@admin_required
def crear_usuario():
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
        sql,
        (
            username,
            name,
            apellidos,
            email,
            generate_password_hash(password),
            celular,
            fechanaci,
            rol,
        ),
    )

    conexion.commit()
    conexion.close()

    return redirect(url_for("admin_panel"))


# ELIMINAR
@app.route("/delete/<int:id>")
@admin_required
def delete(id):
    conexion = conectar()
    cursor = conexion.cursor()
    try:
        cursor.execute("DELETE FROM users WHERE id=%s", (id,))
        conexion.commit()
    except pymysql.err.IntegrityError:
        conexion.rollback()
    conexion.close()

    return redirect(url_for("admin_panel"))


# EDITAR
@app.route("/edit/<int:id>", methods=["POST"])
@admin_required
def edit(id):
    username = request.form["username"]
    name = request.form["name"]
    apellidos = request.form["apellidos"]
    email = request.form["usuario_email"]
    password = request.form.get("password", "").strip()
    celular = request.form["celular"]
    fechanaci = request.form["fechanaci"]
    rol = request.form["rol"]

    conexion = conectar()
    cursor = conexion.cursor()

    if password:
        cursor.execute(
            """
            UPDATE users
            SET username=%s, name=%s, apellidos=%s, email=%s, password=%s,
                celular=%s, fechanaci=%s, rol=%s
            WHERE id=%s
            """,
            (
                username,
                name,
                apellidos,
                email,
                password_service.hash(password),
                celular,
                fechanaci,
                rol,
                id,
            ),
        )
    else:
        cursor.execute(
            """
            UPDATE users
            SET username=%s, name=%s, apellidos=%s, email=%s,
                celular=%s, fechanaci=%s, rol=%s
            WHERE id=%s
            """,
            (username, name, apellidos, email, celular, fechanaci, rol, id),
        )

    conexion.commit()
    conexion.close()

    return redirect(url_for("admin_panel"))


# =========================
# CRUD ADMIN - PRODUCTOS
# =========================


@app.route("/producto", methods=["POST"])
@admin_required
def crear_producto():
    referencia = request.form["referencia"]
    nombre = request.form["nombre"]
    descripcion = request.form.get("descripcion", "")
    categoria_id = request.form["categoria_id"]
    marca_id = request.form["marca_id"]

    conexion = conectar()
    cursor = conexion.cursor()
    cursor.execute(
        """
        INSERT INTO productos (referencia, nombre, descripcion, categoria_id, marca_id, estado)
        VALUES (%s, %s, %s, %s, %s, 'activo')
        """,
        (referencia, nombre, descripcion, categoria_id, marca_id),
    )
    conexion.commit()
    conexion.close()

    return redirect(url_for("admin_panel"))


@app.route("/producto/editar/<int:id>", methods=["POST"])
@admin_required
def editar_producto(id):
    referencia = request.form["referencia"]
    nombre = request.form["nombre"]
    descripcion = request.form.get("descripcion", "")
    categoria_id = request.form["categoria_id"]
    marca_id = request.form["marca_id"]
    estado = request.form.get("estado", "activo")

    conexion = conectar()
    cursor = conexion.cursor()
    cursor.execute(
        """
        UPDATE productos
        SET referencia=%s, nombre=%s, descripcion=%s, categoria_id=%s, marca_id=%s, estado=%s
        WHERE id=%s
        """,
        (referencia, nombre, descripcion, categoria_id, marca_id, estado, id),
    )
    conexion.commit()
    conexion.close()

    return redirect(url_for("admin_panel"))


@app.route("/producto/eliminar/<int:id>")
@admin_required
def eliminar_producto(id):
    conexion = conectar()
    cursor = conexion.cursor()
    try:
        cursor.execute("DELETE FROM productos WHERE id=%s", (id,))
        conexion.commit()
    except pymysql.err.IntegrityError:
        conexion.rollback()
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
