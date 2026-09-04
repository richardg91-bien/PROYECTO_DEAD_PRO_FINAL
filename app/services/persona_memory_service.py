"""Memoria semántica canónica de una PERSONA para Visión 1."""

from flask import current_app


def _as_list(embedding):
    if hasattr(embedding, "tolist"):
        return embedding.tolist()
    return embedding


def guardar_memoria_persona(persona_id, contenido, embedding=None, tipo="conversacion", origen=None, importancia=3):
    """Guarda una memoria asociada inequívocamente a persona_id."""
    if not persona_id or not contenido:
        return None
    payload = {"persona_id": str(persona_id), "contenido": str(contenido).strip(), "tipo": tipo, "origen": origen, "importancia": max(1, min(5, int(importancia or 3)))}
    if embedding is not None:
        payload["embedding"] = _as_list(embedding)
    try:
        response = current_app.supabase.table("memories").insert(payload).execute()
        return response.data[0] if response.data else None
    except Exception as exc:
        current_app.logger.exception("Error guardando memoria de persona: %s", exc)
        return None


def obtener_memorias_persona(persona_id, embedding=None, threshold=0.30, limit=5):
    """Recupera memorias sólo de la persona solicitada."""
    if not persona_id:
        return []
    try:
        if embedding is not None:
            response = current_app.supabase.rpc("match_persona_memories", {"query_embedding": _as_list(embedding), "target_persona_id": str(persona_id), "match_threshold": threshold, "match_count": limit}).execute()
        else:
            response = (current_app.supabase.table("memories").select("id,persona_id,contenido,tipo,importancia,origen,created_at,updated_at").eq("persona_id", str(persona_id)).order("created_at", desc=True).limit(limit).execute())
        return response.data or []
    except Exception as exc:
        current_app.logger.exception("Error recuperando memorias de persona: %s", exc)
        return []


def actualizar_memoria_persona(persona_id, memoria_id, contenido=None, tipo=None, importancia=None):
    """Actualiza una memoria sólo si pertenece a la PERSONA indicada."""
    payload = {}
    if contenido is not None:
        contenido = str(contenido).strip()
        if not contenido:
            return None
        payload["contenido"] = contenido
    if tipo is not None:
        payload["tipo"] = tipo
    if importancia is not None:
        payload["importancia"] = max(1, min(5, int(importancia)))
    if not payload:
        return None
    try:
        response = current_app.supabase.table("memories").update(payload).eq("id", str(memoria_id)).eq("persona_id", str(persona_id)).execute()
        return response.data[0] if response.data else None
    except Exception as exc:
        current_app.logger.exception("Error actualizando memoria de persona: %s", exc)
        return None


def eliminar_memoria_persona(persona_id, memoria_id):
    """Elimina una memoria sólo si pertenece a la PERSONA indicada."""
    try:
        response = current_app.supabase.table("memories").delete().eq("id", str(memoria_id)).eq("persona_id", str(persona_id)).execute()
        return bool(response.data)
    except Exception as exc:
        current_app.logger.exception("Error eliminando memoria de persona: %s", exc)
        return False
