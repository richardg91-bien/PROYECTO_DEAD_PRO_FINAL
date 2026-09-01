"""Rutas de autenticacion: registro, login, logout y perfil."""

from flask import Blueprint, request, jsonify, current_app
from app.auth import login_required

auth_bp = Blueprint("auth", __name__, url_prefix="/api/auth")


def _auth_error_message(error):
    """Traduce errores comunes de Supabase a mensajes utiles para la UI."""
    msg = str(error)
    lower = msg.lower()

    if "already registered" in lower or "already been registered" in lower or "user already registered" in lower:
        return "Este email ya está registrado", 409
    if "signup" in lower and ("disabled" in lower or "not allowed" in lower):
        return "El registro está deshabilitado en Supabase. Activa Email signups en Authentication.", 403
    if "invalid email" in lower:
        return "Email inválido", 400
    if "password" in lower and ("weak" in lower or "short" in lower):
        return "La contraseña es demasiado débil", 400
    if "rate limit" in lower or "too many" in lower:
        return "Demasiados intentos. Probá de nuevo en unos minutos.", 429
    if "api key" in lower or "jwt" in lower:
        return "La configuración de Supabase no es válida. Revisá SUPABASE_KEY.", 500

    return "Error al registrar usuario", 500


# REGISTRO
@auth_bp.route("/register", methods=["POST"])
def register():
    """
    Body JSON: { email, password }
    Crea el usuario en Supabase Auth.
    """
    if not hasattr(current_app, "supabase") or current_app.supabase is None:
        return jsonify({"error": "Supabase no está disponible. Revisa la configuración del backend."}), 500

    data = request.get_json(silent=True) or {}
    email    = (data.get("email") or "").strip().lower()
    password = (data.get("password") or "").strip()

    # Validaciones básicas
    if not email or not password:
        return jsonify({"error": "Email y contraseña son requeridos"}), 400
    if len(password) < 6:
        return jsonify({"error": "La contraseña debe tener al menos 6 caracteres"}), 400
    if "@" not in email:
        return jsonify({"error": "Email inválido"}), 400

    try:
        res = current_app.supabase.auth.sign_up({
            "email": email,
            "password": password
        })

        if not res.user:
            return jsonify({"error": "No se pudo crear el usuario"}), 400

        return jsonify({
            "message": "Usuario creado. Revisá tu email para confirmar la cuenta.",
            "user": {
                "id":    res.user.id,
                "email": res.user.email
            }
        }), 201

    except Exception as e:
        error, status = _auth_error_message(e)
        print(f"Error register: {e}")
        return jsonify({"error": error, "detail": str(e)}), status


# ─────────────────────────────────────────
# LOGIN
# ─────────────────────────────────────────
@auth_bp.route("/login", methods=["POST"])
def login():
    """
    Body JSON: { email, password }
    Retorna access_token y refresh_token.
    """
    if not hasattr(current_app, "supabase") or current_app.supabase is None:
        return jsonify({"error": "Supabase no está disponible. Revisa la configuración del backend."}), 500

    data = request.get_json(silent=True) or {}
    email    = (data.get("email") or "").strip()
    password = (data.get("password") or "").strip()

    if not email or not password:
        return jsonify({"error": "Email y contraseña son requeridos"}), 400

    try:
        res = current_app.supabase.auth.sign_in_with_password({
            "email": email,
            "password": password
        })

        if not res.session:
            return jsonify({"error": "Credenciales incorrectas"}), 401

        return jsonify({
            "access_token":  res.session.access_token,
            "refresh_token": res.session.refresh_token,
            "user": {
                "id":    res.user.id,
                "email": res.user.email
            }
        }), 200

    except Exception as e:
        msg = str(e).lower()
        if "invalid login" in msg or "invalid credentials" in msg:
            return jsonify({"error": "Email o contraseña incorrectos"}), 401
        print(f"❌ Error login: {e}")
        return jsonify({"error": "Error al iniciar sesión", "detail": str(e)}), 500


# ─────────────────────────────────────────
# LOGOUT
# ─────────────────────────────────────────
@auth_bp.route("/logout", methods=["POST"])
@login_required
def logout(current_user=None):
    """
    Invalida el token actual en Supabase.
    Requiere Authorization: Bearer <token>
    """
    try:
        current_app.supabase.auth.sign_out()
        return jsonify({"message": "Sesión cerrada correctamente"}), 200
    except Exception as e:
        print(f"❌ Error logout: {e}")
        return jsonify({"error": "Error al cerrar sesión"}), 500


# ─────────────────────────────────────────
# PERFIL (ruta protegida de ejemplo)
# ─────────────────────────────────────────
@auth_bp.route("/me", methods=["GET"])
@login_required
def me(current_user=None):
    """
    Retorna los datos del usuario autenticado.
    Requiere Authorization: Bearer <token>
    """
    return jsonify({
        "id":    current_user.id,
        "email": current_user.email
    }), 200
