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
        allow_headers=["Content-Type", "Authorization"],
        supports_credentials=True
    )

    # =========================
    # VARIABLES DE ENTORNO
    # =========================
    SUPABASE_URL = os.getenv("SUPABASE_URL")
    SUPABASE_KEY = os.getenv("SUPABASE_KEY")
    DEEPSEEK_API_KEY = os.getenv("GROQ_API_KEY")

    if not SUPABASE_URL or not SUPABASE_KEY:
        raise ValueError("Faltan SUPABASE_URL o SUPABASE_KEY en .env")

    if not DEEPSEEK_API_KEY:
        print("Warning: falta GROQ_API_KEY")

    # =========================
    # CLIENTES EXTERNOS
    # =========================

    app.supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

    if DEEPSEEK_API_KEY:
        app.openai_client = OpenAI(
            api_key=DEEPSEEK_API_KEY,
            base_url="https://api.groq.com/openai/v1"
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

    # Visión 1: API person-centric nueva. Las rutas legacy siguen activas.
    from app.persona_routes import persona_bp
    app.register_blueprint(persona_bp)

    # Visión 1: voz opcional y protegida por la conversación person-centric.
    from app.voice.routes import voice_bp
    app.register_blueprint(voice_bp)

    return app
