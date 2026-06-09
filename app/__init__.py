"""Factory de aplicacion Flask y configuracion global."""

import os
from flask import Flask
from flask_cors import CORS
from dotenv import load_dotenv
from supabase import create_client
from openai import OpenAI


def create_app():
    """Factory para crear la aplicacion Flask."""

    load_dotenv()

    app = Flask(
        __name__,
        template_folder="templates",
        static_folder="../static"
    )

    cors_origins = os.getenv("CORS_ORIGINS", "http://127.0.0.1:5173,http://localhost:5173")
    allowed_origins = [origin.strip() for origin in cors_origins.split(",") if origin.strip()]
    CORS(
        app,
        resources={r"/*": {"origins": allowed_origins or ["http://127.0.0.1:5173"]}},
        allow_headers=["Content-Type", "Authorization"]
    )

    # =========================
    # VARIABLES DE ENTORNO
    # =========================
    SUPABASE_URL = os.getenv("SUPABASE_URL")
    SUPABASE_KEY = os.getenv("SUPABASE_KEY")
    DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY")

    if not SUPABASE_URL or not SUPABASE_KEY:
        raise ValueError("Faltan SUPABASE_URL o SUPABASE_KEY en .env")

    if not DEEPSEEK_API_KEY:
        print("Warning: falta DEEPSEEK_API_KEY")

    # =========================
    # CLIENTES EXTERNOS
    # =========================

    app.supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

    if DEEPSEEK_API_KEY:
        app.openai_client = OpenAI(
            api_key=DEEPSEEK_API_KEY,
            base_url="https://api.deepseek.com"
        )
    else:
        app.openai_client = None

    # =========================
    # CONFIGURACIÓN APP
    # =========================
    app.config["SECRET_KEY"] = os.getenv("SECRET_KEY", "dev_secret")
    if app.config["SECRET_KEY"] == "dev_secret":
        print("Warning: usando SECRET_KEY de desarrollo. Define SECRET_KEY en produccion.")

    # Crear carpetas necesarias
    for folder in ["static/uploads", "static/qr", "static/audio"]:
        os.makedirs(folder, exist_ok=True)

    # =========================
    # REGISTRO DE RUTAS
    # =========================
    from app.routes import main
    app.register_blueprint(main)

    from app.auth_routes import auth_bp
    app.register_blueprint(auth_bp)

    return app
