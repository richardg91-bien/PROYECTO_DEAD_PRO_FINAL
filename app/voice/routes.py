"""Rutas públicas de voz asociadas a conversaciones de una PERSONA."""

from flask import Blueprint, current_app, jsonify, request

from app.character.identity import get_persona_by_id
from app.character.conversation import obtener_conversacion, obtener_mensajes
from app.voice.voice_service import sintetizar_voz

voice_bp = Blueprint("voice", __name__, url_prefix="/api/personas")


@voice_bp.post("/<persona_id>/voice")
def api_persona_voice(persona_id):
    """Sintetiza únicamente la última respuesta persistida de la PERSONA.

    El texto no lo proporciona el navegador: se recupera de la conversación
    protegida por session_id para evitar que el endpoint se convierta en un
    sintetizador arbitrario de texto de terceros.
    """
    persona = get_persona_by_id(current_app, persona_id)
    if not persona:
        return jsonify({"error": "Persona no encontrada"}), 404

    data = request.get_json(silent=True) or {}
    conversation_id = str(data.get("conversation_id") or "").strip()
    session_id = str(data.get("session_id") or "").strip()
    if not conversation_id or not session_id:
        return jsonify({"error": "conversation_id y session_id son obligatorios"}), 400

    conversation = obtener_conversacion(conversation_id, session_id)
    if not conversation or str(conversation.get("persona_id")) != str(persona_id):
        return jsonify({"error": "Conversación inválida"}), 404

    mensajes = obtener_mensajes(conversation_id, limit=20, session_id=session_id)
    ultimo = next((m for m in reversed(mensajes) if m.get("role") == "persona" and m.get("content")), None)
    if not ultimo:
        return jsonify({"error": "No hay una respuesta de la persona para sintetizar"}), 404

    emotion = (ultimo.get("emotion") or {}).get("visitor", "neutral")
    audio_url = sintetizar_voz(ultimo["content"], emotion)
    if not audio_url:
        return jsonify({"audio": None, "available": False}), 200

    return jsonify({"audio": audio_url, "available": True, "emotion": emotion}), 200
