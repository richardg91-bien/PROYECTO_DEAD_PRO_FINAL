"""Middleware de autenticación via Supabase JWT"""

import os
from functools import wraps
from flask import request, jsonify, current_app


def get_current_user():
    """
    Extrae y valida el token JWT del header Authorization.
    Retorna los datos del usuario o None si no es válido.
    """
    auth_header = request.headers.get("Authorization", "")
    if not auth_header.startswith("Bearer "):
        return None

    token = auth_header.split(" ", 1)[1].strip()
    if not token:
        return None

    try:
        # Supabase valida el JWT con su propio cliente
        user = current_app.supabase.auth.get_user(token)
        return user.user
    except Exception as e:
        print(f"⚠️ Auth error: {e}")
        return None


def login_required(f):
    """
    Decorador para rutas que requieren autenticación.
    Retorna 401 si el token falta o es inválido.
    """
    @wraps(f)
    def decorated(*args, **kwargs):
        user = get_current_user()
        if not user:
            return jsonify({
                "error": "No autorizado",
                "detail": "Token ausente o inválido"
            }), 401
        # Inyecta el usuario en kwargs para que la ruta lo use si quiere
        kwargs["current_user"] = user
        return f(*args, **kwargs)
    return decorated
