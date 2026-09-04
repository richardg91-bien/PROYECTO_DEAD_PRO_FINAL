"""Acceso a la identidad estable de una PERSONA.

La identidad se resuelve por UUID o slug, nunca por nombre como identificador.
"""


def _client(app):
    client = getattr(app, "supabase", None)
    if client is None:
        raise RuntimeError("Supabase no configurado")
    return client


def get_persona_by_id(app, persona_id):
    response = (
        _client(app)
        .table("personas")
        .select("*")
        .eq("id", persona_id)
        .limit(1)
        .execute()
    )
    return response.data[0] if response.data else None


def get_persona_by_slug(app, slug):
    response = (
        _client(app)
        .table("personas")
        .select("*")
        .eq("slug", slug)
        .limit(1)
        .execute()
    )
    return response.data[0] if response.data else None
