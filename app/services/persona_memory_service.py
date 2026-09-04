"""Memoria semántica canónica de una PERSONA para Visión 1."""

from flask import current_app


def _as_list(embedding):
    if hasattr(embedding, "tolist"):
        return embedding.tolist()
    return embedding


def guardar_memoria_persona(persona_id, contenido, embedding=None, tipo="conversacion", origen=None):
    """Guarda una memoria asociada inequívocamente a persona_id."""
    if not persona_id or not contenido:
        return None

    payload = {
        "persona_id": str(persona_id),
        "contenido": contenido,
        "tipo": tipo,
        "origen": origen,
    }
    if embedding is not None:
        payload["embedding"] = _as_list(embedding)

    try:
        response = current_app.supabase.table("memories").insert(payload).execute()
        return response.data[0] if response.data else None
    except Exception as exc:
        current_app.logger.exception("Error guardando memoria de persona: %s", exc)
        return None


def obtener_memorias_persona(persona_id, embedding, threshold=0.30, limit=5):
    """Recupera memorias únicamente de la persona solicitada."""
    if not persona_id or embedding is None:
        return []

    try:
        response = current_app.supabase.rpc(
            "match_persona_memories",
            {
                "query_embedding": _as_list(embedding),
                "target_persona_id": str(persona_id),
                "match_threshold": threshold,
                "match_count": limit,
            },
        ).execute()
        return response.data or []
    except Exception as exc:
        current_app.logger.exception("Error recuperando memorias de persona: %s", exc)
        return []
