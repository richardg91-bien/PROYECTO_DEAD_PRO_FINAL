"""API person-centric de Visión 1.

Estas rutas son nuevas y no sustituyen las rutas legacy existentes.
"""

import uuid
from flask import Blueprint, current_app, jsonify, request

from app.character.identity import get_persona_by_id, get_persona_by_slug

persona_bp = Blueprint("persona", __name__, url_prefix="/api/personas")


@persona_bp.get("/<persona_id>")
def api_persona(persona_id):
    """Devuelve una persona pública por UUID."""
    try:
        uuid.UUID(str(persona_id))
    except (ValueError, AttributeError):
        return jsonify({"error": "ID de persona inválido"}), 400

    try:
        persona = get_persona_by_id(current_app, persona_id)
    except Exception as exc:
        print(f"❌ Error persona: {exc}")
        return jsonify({"error": "Error interno"}), 500

    if not persona:
        return jsonify({"error": "Persona no encontrada"}), 404

    return jsonify(persona)


@persona_bp.get("/slug/<slug>")
def api_persona_slug(slug):
    """Devuelve una persona pública por slug."""
    if not slug or len(slug) > 120:
        return jsonify({"error": "Slug inválido"}), 400

    try:
        persona = get_persona_by_slug(current_app, slug)
    except Exception as exc:
        print(f"❌ Error persona por slug: {exc}")
        return jsonify({"error": "Error interno"}), 500

    if not persona:
        return jsonify({"error": "Persona no encontrada"}), 404

    return jsonify(persona)


@persona_bp.post("")
def api_persona_create():
    """Crea una PERSONA cuando el backend recibe un usuario autenticado.

    La autorización definitiva se mantiene en Supabase RLS. Esta primera etapa
    solamente valida los campos y evita crear personas sin owner_id.
    """
    data = request.get_json(silent=True) or {}
    owner_id = data.get("owner_id")
    nombre = (data.get("nombre") or "").strip()
    slug = (data.get("slug") or "").strip().lower()

    if not owner_id or not nombre or not slug:
        return jsonify({"error": "owner_id, nombre y slug son obligatorios"}), 400

    try:
        uuid.UUID(str(owner_id))
    except (ValueError, AttributeError):
        return jsonify({"error": "owner_id inválido"}), 400

    if len(nombre) > 200 or len(slug) > 120:
        return jsonify({"error": "nombre o slug demasiado largo"}), 400

    payload = {
        "owner_id": str(owner_id),
        "nombre": nombre,
        "slug": slug,
        "bio": data.get("bio"),
        "fecha_nacimiento": data.get("fecha_nacimiento"),
        "fecha_fallecimiento": data.get("fecha_fallecimiento"),
        "lugar_nacimiento": data.get("lugar_nacimiento"),
        "lugar_fallecimiento": data.get("lugar_fallecimiento"),
        "foto_principal": data.get("foto_principal"),
        "visibilidad": data.get("visibilidad", "publica"),
    }

    try:
        response = current_app.supabase.table("personas").insert(payload).execute()
    except Exception as exc:
        print(f"❌ Error creando persona: {exc}")
        return jsonify({"error": "No se pudo crear la persona"}), 500

    if not response.data:
        return jsonify({"error": "No se pudo crear la persona"}), 500

    return jsonify(response.data[0]), 201
