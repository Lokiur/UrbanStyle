from flask import Flask, session

from app.services import cart_service


def create_app():
    app = Flask(__name__)

    app.secret_key = "urbanstyle"
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

    return app
