"""Punto de entrada de la aplicacion."""

import os

from app import create_app

if __name__ == "__main__":
    app = create_app()
    debug = os.getenv("FLASK_DEBUG", "0").lower() in {"1", "true", "yes"}
    host  = os.getenv("FLASK_HOST", "127.0.0.1")
    port  = int(os.getenv("FLASK_PORT", "5000"))
    app.run(host=host, port=port, debug=debug)
