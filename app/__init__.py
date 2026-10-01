import os

from flask import Flask, session, url_for

from app.services import cart_service

try:
    from dotenv import load_dotenv

    load_dotenv()
except ImportError:
    pass


def create_app():
    app = Flask(__name__)

    # Firma la sesion y los enlaces de recuperacion: en produccion
    # debe venir de SECRET_KEY (.env) con un valor largo y aleatorio.
    app.secret_key = os.environ.get("SECRET_KEY")
    if not app.secret_key:
        app.secret_key = "urbanstyle-dev"
        app.logger.warning(
            "SECRET_KEY no definida: usando clave de desarrollo. "
            "Configúrala en .env antes de desplegar."
        )
    app.config["MAX_CONTENT_LENGTH"] = 5 * 1024 * 1024  # 5 MB por subida

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
