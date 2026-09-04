"""Persistencia de conversaciones de Visión 1."""

import uuid

from flask import current_app

VALID_ROLES = {"visitor", "persona", "system"}


def crear_conversacion(persona_id, session_id, visitor_id=None, metadata=None):
    if not persona_id or not session_id:
        return None

    conversation_id = str(uuid.uuid4())
    payload = {
        "id": conversation_id,
        "persona_id": str(persona_id),
        "session_id": str(session_id),
        "metadata": metadata or {},
    }
    if visitor_id:
        payload["visitor_id"] = str(visitor_id)

    try:
        response = current_app.supabase.table("conversations").insert(
            payload, returning="minimal"
        ).execute()
        if response is None:
            return None
        return payload
    except Exception as exc:
        print(f"ERROR crear_conversacion: {exc}")
        return None


def obtener_conversacion(conversation_id, session_id=None):
    if not conversation_id:
        return None
    try:
        if session_id:
            response = current_app.supabase.rpc("get_conversation_for_session", {
                "target_conversation_id": str(conversation_id),
                "target_session_id": str(session_id),
            }).execute()
        else:
            response = current_app.supabase.table("conversations").select(
                "id,persona_id,visitor_id,session_id,created_at,updated_at,metadata"
            ).eq("id", str(conversation_id)).limit(1).execute()
        data = response.data or []
        return data[0] if data else None
    except Exception as exc:
        print(f"ERROR obtener_conversacion: {exc}")
        return None


def guardar_mensaje(conversation_id, role, content, emotion=None, metadata=None):
    if not conversation_id or role not in VALID_ROLES or not content:
        return None

    message_id = str(uuid.uuid4())
    payload = {
        "id": message_id,
        "conversation_id": str(conversation_id),
        "role": role,
        "content": str(content),
        "emotion": emotion or {},
        "metadata": metadata or {},
    }

    try:
        # Los mensajes del visitante pasan por el cliente público y RLS.
        # Las respuestas generadas por Character Engine se escriben con el
        # cliente server-only, que usa SUPABASE_SERVICE_ROLE_KEY y nunca llega
        # al navegador. Así mantenemos RLS para el tráfico público sin permitir
        # que un visitante fabrique mensajes con role=persona.
        client = current_app.supabase
        if role in {"persona", "system"}:
            client = getattr(current_app, "supabase_admin", None)
            if client is None:
                current_app.logger.error(
                    "No se puede persistir role=%s: falta SUPABASE_SERVICE_ROLE_KEY",
                    role,
                )
                return None

        response = client.table("conversation_messages").insert(
            payload, returning="minimal"
        ).execute()
        if response is None:
            return None
        return payload
    except Exception as exc:
        print(f"ERROR guardar_mensaje: {exc}")
        return None


def obtener_mensajes(conversation_id, limit=20, session_id=None):
    if not conversation_id:
        return []
    try:
        limit = max(1, min(int(limit), 100))
    except (TypeError, ValueError):
        limit = 20
    try:
        if session_id:
            response = current_app.supabase.rpc("get_conversation_messages_for_session", {
                "target_conversation_id": str(conversation_id),
                "target_session_id": str(session_id),
                "message_limit": limit,
            }).execute()
        else:
            response = current_app.supabase.table("conversation_messages").select(
                "id,conversation_id,role,content,emotion,created_at,metadata"
            ).eq("conversation_id", str(conversation_id)).order("created_at", desc=False).limit(limit).execute()
        return response.data or []
    except Exception as exc:
        print(f"ERROR obtener_mensajes: {exc}")
        return []
