"""Factory de aplicacion Flask y configuracion global."""

import os
from flask import Flask
from dotenv import dotenv_values

try:
    from flask_cors import CORS
except Exception:  # pragma: no cover - depende del entorno
    CORS = None

try:
    from supabase import create_client
except Exception:  # pragma: no cover - depende del entorno
    create_client = None

try:
    from openai import OpenAI
except Exception:  # pragma: no cover - depende del entorno
    OpenAI = None


def create_app():
    """Factory para crear la aplicacion Flask."""

    env_values = dotenv_values(".env") if os.path.exists(".env") else {}

    app = Flask(
        __name__,
        template_folder="templates",
        static_folder="../static"
    )

    cors_origins = os.getenv("CORS_ORIGINS", "http://127.0.0.1:5173,http://localhost:5173")
    allowed_origins = [origin.strip() for origin in cors_origins.split(",") if origin.strip()]
    if CORS is not None:
        CORS(
            app,
            resources={r"/*": {"origins": allowed_origins or ["http://127.0.0.1:5173"]}},
            allow_headers=["Content-Type", "Authorization"],
            supports_credentials=True
        )

    # =========================
    # VARIABLES DE ENTORNO
    # =========================
    SUPABASE_URL = os.getenv("SUPABASE_URL") or env_values.get("SUPABASE_URL")
    SUPABASE_KEY = os.getenv("SUPABASE_KEY") or env_values.get("SUPABASE_KEY")
    DEEPSEEK_API_KEY = os.getenv("GROQ_API_KEY") or env_values.get("GROQ_API_KEY")

    if not SUPABASE_URL or not SUPABASE_KEY:
        raise ValueError("Faltan SUPABASE_URL o SUPABASE_KEY en .env")

    if not DEEPSEEK_API_KEY:
        print("Warning: falta GROQ_API_KEY")

    # =========================
    # CLIENTES EXTERNOS
    # =========================

    if create_client is None:
        app.supabase = None
    else:
        app.supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

    if DEEPSEEK_API_KEY and OpenAI is not None:
        app.openai_client = OpenAI(
            api_key=DEEPSEEK_API_KEY,
            base_url="https://api.groq.com/openai/v1"
        )
    else:
        app.openai_client = None

    # =========================
    # CONFIGURACIÓN APP
    # =========================
    flask_env = os.getenv("FLASK_ENV", "development").lower()
    secret_key = os.getenv("SECRET_KEY")

    if flask_env == "production":
        if not secret_key:
            raise ValueError("SECRET_KEY es obligatorio cuando FLASK_ENV=production")
        app.config["SECRET_KEY"] = secret_key
    else:
        app.config["SECRET_KEY"] = secret_key or env_values.get("SECRET_KEY") or "dev_secret"
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
