import os

from app import create_app

app = create_app()

if __name__ == "__main__":
    # en produccion (Render, etc.) no se define FLASK_DEBUG, asi que
    # corre sin modo debug y el servidor real es Gunicorn, no este run().
    app.run(debug=os.environ.get("FLASK_DEBUG", "") == "1")
