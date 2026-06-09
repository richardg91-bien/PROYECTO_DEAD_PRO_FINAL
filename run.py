"""Punto de entrada de la aplicacion."""
import os

from app import create_app

if __name__ == "__main__":
    app = create_app()
    debug = os.getenv("FLASK_DEBUG", "0").lower() in {"1", "true", "yes"}
    app.run(debug=debug)
