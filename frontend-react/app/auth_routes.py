"""Rutas de autenticación — registro, login, logout, perfil"""

from flask import Blueprint, request, jsonify, current_app
from app.auth import login_required

auth_bp = Blueprint("auth", __name__, url_prefix="/api/auth")


# ─────────────────────────────────────────
# REGISTRO
# ─────────────────────────────────────────
@auth_bp.route("/register", methods=["POST"])
def register():
    """
    Body JSON: { email, password }
    Crea el usuario en Supabase Auth.
    """
    data = request.get_json(silent=True) or {}
    email    = (data.get("email") or "").strip()
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
        msg = str(e)
        # Supabase devuelve mensajes en inglés — los traducimos
        if "already registered" in msg.lower():
            return jsonify({"error": "Este email ya está registrado"}), 409
        print(f"❌ Error register: {e}")
        return jsonify({"error": "Error al registrar usuario"}), 500


# ─────────────────────────────────────────
# LOGIN
# ─────────────────────────────────────────
@auth_bp.route("/login", methods=["POST"])
def login():
    """
    Body JSON: { email, password }
    Retorna access_token y refresh_token.
    """
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
        return jsonify({"error": "Error al iniciar sesión"}), 500


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
