"""Factory de aplicacion Flask y configuracion global."""

import os
from types import SimpleNamespace
from flask import Flask
from dotenv import dotenv_values, load_dotenv

try:
    from flask_cors import CORS
except Exception:  # pragma: no cover - depende del entorno
    CORS = None

try:
    from supabase import create_client
except Exception:  # pragma: no cover - depende del entorno
    create_client = None

try:
    import requests
except Exception:  # pragma: no cover - depende del entorno
    requests = None


# Compatibilidad con tests previos que patchan app.OpenAI
OpenAI = None


class GroqApiError(Exception):
    def __init__(self, message, status_code=None, code=None, body=None):
        super().__init__(message)
        self.status_code = status_code
        self.code = code
        self.body = body


class GroqChatClient:
    def __init__(self, api_key):
        self.api_key = api_key
        self.chat = type("Chat", (), {"completions": self.Completions(self)})()

    class Completions:
        def __init__(self, parent):
            self.parent = parent

        def create(self, model, messages):
            if requests is None:
                raise RuntimeError("requests no está disponible")

            response = requests.post(
                "https://api.groq.com/openai/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {self.parent.api_key}",
                    "Content-Type": "application/json",
                },
                json={"model": model, "messages": messages},
                timeout=60,
            )

            try:
                body = response.json()
            except ValueError:
                body = None

            if not response.ok:
                error_body = body.get("error", {}) if isinstance(body, dict) else {}
                raise GroqApiError(
                    error_body.get("message") or response.text or "Error al comunicarse con Groq",
                    status_code=response.status_code,
                    code=error_body.get("code"),
                    body=body,
                )

            choice = body["choices"][0]
            return SimpleNamespace(
                choices=[SimpleNamespace(message=SimpleNamespace(content=choice["message"]["content"]))]
            )


def create_app():
    """Factory para crear la aplicacion Flask."""

    # Validación temprana de FLASK_ENV en producción
    flask_env = os.getenv("FLASK_ENV", "development").lower()
    if flask_env == "production":
        secret_key = os.getenv("SECRET_KEY")
        if not secret_key:
            raise ValueError("SECRET_KEY es obligatorio cuando FLASK_ENV=production")

    load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), "..", ".env"), override=False)
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
    GROQ_API_KEY = os.getenv("GROQ_API_KEY") or env_values.get("GROQ_API_KEY")

    if not SUPABASE_URL or not SUPABASE_KEY:
        raise ValueError("Faltan SUPABASE_URL o SUPABASE_KEY en .env")

    if not GROQ_API_KEY:
        print("Warning: falta GROQ_API_KEY")

    # =========================
    # CLIENTES EXTERNOS
    # =========================

    app.supabase = None
    if create_client is not None and SUPABASE_URL and SUPABASE_KEY:
        try:
            app.supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
        except Exception as exc:
            print(f"Warning: no se pudo inicializar Supabase: {exc}")
            app.supabase = None

    if GROQ_API_KEY and requests is not None:
        app.groq_client = GroqChatClient(GROQ_API_KEY)
        app.openai_client = app.groq_client
    else:
        app.groq_client = None
        app.openai_client = None

    # =========================
    # CONFIGURACIÓN APP
    # =========================
    flask_env = os.getenv("FLASK_ENV", "development").lower()
    secret_key = os.getenv("SECRET_KEY")

    # En modo production, SECRET_KEY ya fue validado arriba
    if flask_env == "production":
        app.config["SECRET_KEY"] = secret_key
    else:
        app.config["SECRET_KEY"] = secret_key or env_values.get("SECRET_KEY") or "dev_secret"
        if app.config["SECRET_KEY"] == "dev_secret":
            print("Warning: usando SECRET_KEY de desarrollo. Define SECRET_KEY en produccion.")

    # =========================
    # REGISTRO DE RUTAS
    # =========================
    from app.routes import main
    app.register_blueprint(main)

    from app.auth_routes import auth_bp
    app.register_blueprint(auth_bp)

    return app
