"""Factory de aplicación Flask y configuración global"""

import os
from flask import Flask
from flask_cors import CORS
from dotenv import load_dotenv
from supabase import create_client
from openai import OpenAI


def create_app():
    """Factory para crear la aplicación Flask"""

    # 🔥 cargar variables de entorno
    load_dotenv()

    app = Flask(
        __name__,
        template_folder="templates",
        static_folder="../static"
    )

    CORS(app)

    # =========================
    # VARIABLES DE ENTORNO
    # =========================
    SUPABASE_URL = os.getenv("SUPABASE_URL")
    SUPABASE_KEY = os.getenv("SUPABASE_KEY")
    DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY")

    # 🔥 VALIDACIÓN
    if not SUPABASE_URL or not SUPABASE_KEY:
        raise ValueError("❌ Faltan SUPABASE_URL o SUPABASE_KEY en .env")

    if not DEEPSEEK_API_KEY:
        print("⚠️ Warning: falta DEEPSEEK_API_KEY")

    # =========================
    # CLIENTES EXTERNOS
    # =========================

    # Supabase
    app.supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

    # OpenAI / DeepSeek
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

    # Crear carpetas necesarias
    for folder in ["static/uploads", "static/qr", "static/audio"]:
        os.makedirs(folder, exist_ok=True)

    # =========================
    # REGISTRO DE RUTAS
    # =========================
    from app.routes import main
    app.register_blueprint(main)

    return app