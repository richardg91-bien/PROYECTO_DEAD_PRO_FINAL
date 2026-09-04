"""API canónica person-centric de Visión 1."""

import uuid
from flask import Blueprint, current_app, jsonify, request

from app.auth import login_required
from app.character.identity import get_persona_by_id, get_persona_by_slug
from app.character.character_engine import generar_respuesta
from app.character.conversation import crear_conversacion, obtener_conversacion, guardar_mensaje, obtener_mensajes

persona_bp = Blueprint("persona", __name__, url_prefix="/api/personas")


def _valid_uuid(value):
    try:
        return str(uuid.UUID(str(value)))
    except (ValueError, AttributeError, TypeError):
        return None


def _session_id(value):
    value = str(value or "").strip()
    if not value or len(value) > 200:
        return str(uuid.uuid4())
    return value


@persona_bp.get("/<persona_id>")
def api_persona(persona_id):
    persona_id = _valid_uuid(persona_id)
    if not persona_id:
        return jsonify({"error": "ID de persona inválido"}), 400
    try:
        persona = get_persona_by_id(current_app, persona_id)
    except Exception as exc:
        print(f"❌ Error persona: {exc}")
        return jsonify({"error": "Error interno"}), 500
    if not persona:
        return jsonify({"error": "Persona no encontrada"}), 404
    return jsonify(persona)


@persona_bp.get("/<persona_id>/experiencias")
def api_persona_experiencias(persona_id):
    persona_id = _valid_uuid(persona_id)
    if not persona_id:
        return jsonify({"error": "ID de persona inválido"}), 400
    if not get_persona_by_id(current_app, persona_id):
        return jsonify({"error": "Persona no encontrada"}), 404
    try:
        response = (current_app.supabase.table("experiences")
            .select("id,persona_id,title,description,image,created_at,ai_description,qr")
            .eq("persona_id", persona_id).order("created_at", desc=True).execute())
        return jsonify(response.data or [])
    except Exception as exc:
        print(f"❌ Error experiencias persona: {exc}")
        return jsonify({"error": "Error interno"}), 500


@persona_bp.get("/slug/<slug>")
def api_persona_slug(slug):
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
@login_required
def api_persona_create(current_user=None):
    data = request.get_json(silent=True) or {}
    nombre = (data.get("nombre") or "").strip()
    slug = (data.get("slug") or "").strip().lower()
    if not nombre or not slug:
        return jsonify({"error": "nombre y slug son obligatorios"}), 400
    if len(nombre) > 200 or len(slug) > 120:
        return jsonify({"error": "nombre o slug demasiado largo"}), 400
    payload = {
        "owner_id": str(current_user.id), "nombre": nombre, "slug": slug,
        "bio": data.get("bio"), "fecha_nacimiento": data.get("fecha_nacimiento"),
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


@persona_bp.post("/<persona_id>/conversations")
def api_conversation_create(persona_id):
    persona_id = _valid_uuid(persona_id)
    if not persona_id:
        return jsonify({"error": "ID de persona inválido"}), 400
    if not get_persona_by_id(current_app, persona_id):
        return jsonify({"error": "Persona no encontrada"}), 404
    data = request.get_json(silent=True) or {}
    session_id = _session_id(data.get("session_id"))
    conversation = crear_conversacion(persona_id, session_id, metadata={"channel": "qr_web"})
    if not conversation:
        return jsonify({"error": "No se pudo crear la conversación"}), 500
    return jsonify({"conversation": conversation, "session_id": session_id}), 201


@persona_bp.get("/conversations/<conversation_id>")
def api_conversation(conversation_id):
    conversation_id = _valid_uuid(conversation_id)
    if not conversation_id:
        return jsonify({"error": "Conversación inválida"}), 400
    session_id = request.args.get("session_id")
    if not session_id:
        return jsonify({"error": "session_id es obligatorio"}), 400
    conversation = obtener_conversacion(conversation_id, session_id)
    if not conversation:
        return jsonify({"error": "Conversación no encontrada"}), 404
    return jsonify({**conversation, "mensajes": obtener_mensajes(conversation_id, session_id=session_id)})


@persona_bp.post("/<persona_id>/chat")
def api_persona_chat(persona_id):
    persona_id = _valid_uuid(persona_id)
    if not persona_id:
        return jsonify({"error": "ID de persona inválido"}), 400
    data = request.get_json(silent=True) or {}
    message = (data.get("message") or "").strip()
    conversation_id = _valid_uuid(data.get("conversation_id"))
    session_id = _session_id(data.get("session_id"))
    historial = data.get("historial") or []

    if not message:
        return jsonify({"error": "El mensaje es obligatorio"}), 400
    if len(message) > 5000:
        return jsonify({"error": "Mensaje demasiado largo"}), 400
    if not get_persona_by_id(current_app, persona_id):
        return jsonify({"error": "Persona no encontrada"}), 404
    if not current_app.openai_client:
        return jsonify({"error": "IA no configurada en el servidor"}), 503

    if conversation_id:
        conversation = obtener_conversacion(conversation_id, session_id)
        if not conversation or conversation.get("persona_id") != persona_id:
            return jsonify({"error": "Conversación inválida"}), 400
    else:
        conversation = crear_conversacion(persona_id, session_id, metadata={"channel": "qr_web"})
        if not conversation:
            return jsonify({"error": "No se pudo iniciar la conversación"}), 500
        conversation_id = conversation["id"]

    try:
        resultado = generar_respuesta(persona_id, message, historial)
        if not resultado:
            return jsonify({"error": "Persona no encontrada"}), 404
        emocion = resultado["emocion"]
        guardar_mensaje(conversation_id, "visitor", message, emotion={"detected": emocion})
        guardar_mensaje(conversation_id, "persona", resultado["respuesta"], emotion={"visitor": emocion})
        return jsonify({"conversation_id": conversation_id, "session_id": session_id,
                        "persona": resultado["persona"], "respuesta": resultado["respuesta"],
                        "emocion": emocion, "audio": None})
    except Exception as exc:
        print(f"❌ Error Character Engine: {exc}")
        return jsonify({"error": "No se pudo generar la respuesta"}), 500
