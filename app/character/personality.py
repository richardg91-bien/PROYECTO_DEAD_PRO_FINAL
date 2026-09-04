"""Acceso a la personalidad canónica de una PERSONA."""

from flask import current_app


def obtener_personalidad(persona_id):
    """Devuelve la personalidad estructurada de una persona o valores vacíos."""
    try:
        response = (
            current_app.supabase
            .table("personalities")
            .select(
                "id,persona_id,traits,values,temperament,"
                "communication_style,humor_style,likes,dislikes,"
                "behavioral_rules,created_at,updated_at"
            )
            .eq("persona_id", persona_id)
            .limit(1)
            .execute()
        )
        data = response.data or []
        return data[0] if data else None
    except Exception as exc:
        print(f"ERROR obtener_personalidad: {exc}")
        return None


def normalizar_personalidad(personalidad):
    """Normaliza la personalidad para consumo seguro por Character Engine."""
    if not personalidad:
        return {
            "traits": {},
            "values": {},
            "temperament": {},
            "communication_style": {},
            "humor_style": {},
            "likes": [],
            "dislikes": [],
            "behavioral_rules": [],
        }

    return {
        "traits": personalidad.get("traits") or {},
        "values": personalidad.get("values") or {},
        "temperament": personalidad.get("temperament") or {},
        "communication_style": personalidad.get("communication_style") or {},
        "humor_style": personalidad.get("humor_style") or {},
        "likes": personalidad.get("likes") or [],
        "dislikes": personalidad.get("dislikes") or [],
        "behavioral_rules": personalidad.get("behavioral_rules") or [],
    }
