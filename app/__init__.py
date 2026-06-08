from flask import Flask
import os
import sqlite3
from dotenv import load_dotenv
from supabase import create_client
from openai import OpenAI

# Cargar variables de entorno
load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY")

if not all([SUPABASE_URL, SUPABASE_KEY, DEEPSEEK_API_KEY]):
    raise Exception("❌ Faltan variables de entorno (.env)")

# Clientes globales
openai_client = OpenAI(
    api_key=DEEPSEEK_API_KEY,
    base_url="https://api.deepseek.com"
)

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)


def create_app():
    """Factory para crear la aplicación Flask"""

    app = Flask(
        __name__,
        template_folder="app/templates",
        static_folder="static"
    )

    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'clave_secreta_desarrollo')

    # Crear carpetas seguras
    for folder in ["static/uploads", "static/qr", "static/audio"]:
        os.makedirs(folder, exist_ok=True)

    # Inicializar base de datos
    def init_db():
        db = get_db()
        db.execute("""
        CREATE TABLE IF NOT EXISTS experiences (
            id TEXT PRIMARY KEY,
            persona TEXT,
            title TEXT,
            description TEXT,
            image TEXT,
            qr TEXT
        )
        """)
        db.commit()
        db.close()

    init_db()

    # Registrar blueprint
    from .routes import main
    app.register_blueprint(main)

    # Hacer clientes disponibles en la app
    app.openai_client = openai_client
    app.supabase = supabase

    return app


def get_db():
    """Obtener conexión a la base de datos"""
    conn = sqlite3.connect("database.db")
    conn.row_factory = sqlite3.Row
    return conn
