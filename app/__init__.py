from flask import Flask, redirect, request, session, url_for

from app.services import cart_service


def create_app():
    app = Flask(__name__)

    app.secret_key = "urbanstyle"
    # 16 MB por subida: las imagenes de productos/categorias se comprimen
    # antes de guardarlas (ver products_service._leer_imagen)
    app.config["MAX_CONTENT_LENGTH"] = 16 * 1024 * 1024

    from app.routes.admin_routes import admin
    from app.routes.auth_routes import auth
    from app.routes.cart_routes import carrito
    from app.routes.home_routes import home
    from app.routes.products_routes import productos
    from app.routes.user_routes import usuario

    app.register_blueprint(home)
    app.register_blueprint(productos)
    app.register_blueprint(carrito)
    app.register_blueprint(auth)
    app.register_blueprint(usuario)
    app.register_blueprint(admin)

    @app.errorhandler(413)
    def archivo_muy_grande(error):
        # en el panel admin muestra el aviso en el formulario en vez de una pagina de error
        mensaje = "La imagen pesa más de 16 MB, usa una más liviana"
        if request.path.startswith("/categoria"):
            session["error_categoria"] = mensaje
            return redirect(url_for("admin.admin_panel") + "#section-categorias")
        if request.path.startswith("/producto"):
            session["error_producto"] = mensaje
            return redirect(url_for("admin.admin_panel") + "#section-productos")
        return error

    @app.context_processor
    def inject_carrito_count():
        count = 0
        if "user_id" in session:
            count = cart_service.contar_items(session["user_id"])
        return dict(carrito_count=count)

    @app.context_processor
    def inject_avatar_url():
        avatar = session.get("avatar")
        filename = f"img/avatars/{avatar}" if avatar else "img/user.png"
        return dict(avatar_url=url_for("static", filename=filename))

    return app
