"""Persistencia de conversaciones de Visión 1.

La conversación está siempre vinculada a una PERSONA mediante persona_id.
Las rutas legacy de chat no son reemplazadas por este módulo.
"""

from flask import current_app


VALID_ROLES = {"visitor", "persona", "system"}


def crear_conversacion(persona_id, session_id, visitor_id=None, metadata=None):
    if not persona_id or not session_id:
        return None

    payload = {
        "persona_id": str(persona_id),
        "session_id": str(session_id),
        "metadata": metadata or {},
    }
    if visitor_id:
        payload["visitor_id"] = str(visitor_id)

    try:
        response = current_app.supabase.table("conversations").insert(payload).execute()
        data = response.data or []
        return data[0] if data else None
    except Exception as exc:
        print(f"ERROR crear_conversacion: {exc}")
        return None


def obtener_conversacion(conversation_id):
    if not conversation_id:
        return None

    try:
        response = (
            current_app.supabase.table("conversations")
            .select("id,persona_id,visitor_id,session_id,created_at,updated_at,metadata")
            .eq("id", str(conversation_id))
            .limit(1)
            .execute()
        )
        data = response.data or []
        return data[0] if data else None
    except Exception as exc:
        print(f"ERROR obtener_conversacion: {exc}")
        return None


def guardar_mensaje(conversation_id, role, content, emotion=None, metadata=None):
    if not conversation_id or role not in VALID_ROLES or not content:
        return None

    payload = {
        "conversation_id": str(conversation_id),
        "role": role,
        "content": str(content),
        "emotion": emotion or {},
        "metadata": metadata or {},
    }

    try:
        response = current_app.supabase.table("conversation_messages").insert(payload).execute()
        data = response.data or []
        return data[0] if data else None
    except Exception as exc:
        print(f"ERROR guardar_mensaje: {exc}")
        return None


def obtener_mensajes(conversation_id, limit=20):
    if not conversation_id:
        return []

    try:
        limit = max(1, min(int(limit), 100))
    except (TypeError, ValueError):
        limit = 20

    try:
        response = (
            current_app.supabase.table("conversation_messages")
            .select("id,conversation_id,role,content,emotion,created_at,metadata")
            .eq("conversation_id", str(conversation_id))
            .order("created_at", desc=False)
            .limit(limit)
            .execute()
        )
        return response.data or []
    except Exception as exc:
        print(f"ERROR obtener_mensajes: {exc}")
        return []
