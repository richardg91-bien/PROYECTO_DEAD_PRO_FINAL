"""Construcción del contexto canónico que recibe el Character Engine."""


def _lista(valor):
    if isinstance(valor, list):
        return valor
    if valor is None:
        return []
    return [valor]


def construir_contexto_personaje(persona, personalidad, recuerdos, emocion_visitante, historial=None):
    """Devuelve contexto estable para que el LLM interprete a la PERSONA.

    La identidad y personalidad son permanentes. La emoción del visitante
    solo modifica el tono contextual de la conversación.
    """
    return {
        "identidad": {
            "id": persona.get("id"),
            "nombre": persona.get("nombre") or "esta persona",
            "bio": persona.get("bio") or "",
            "fecha_nacimiento": persona.get("fecha_nacimiento"),
            "fecha_fallecimiento": persona.get("fecha_fallecimiento"),
            "lugar_nacimiento": persona.get("lugar_nacimiento"),
            "lugar_fallecimiento": persona.get("lugar_fallecimiento"),
        },
        "personalidad": {
            "rasgos": (personalidad or {}).get("traits") or {},
            "valores": (personalidad or {}).get("values") or {},
            "temperamento": (personalidad or {}).get("temperament") or {},
            "comunicacion": (personalidad or {}).get("communication_style") or {},
            "humor": (personalidad or {}).get("humor_style") or {},
            "gustos": _lista((personalidad or {}).get("likes")),
            "disgustos": _lista((personalidad or {}).get("dislikes")),
            "reglas": _lista((personalidad or {}).get("behavioral_rules")),
        },
        "memorias": recuerdos or [],
        "emocion_visitante": emocion_visitante or {
            "emocion": "neutral", "intensidad": 0.0, "confianza": 0.0
        },
        "historial": (historial or [])[-10:],
    }


def contexto_a_prompt(contexto):
    identidad = contexto["identidad"]
    personalidad = contexto["personalidad"]
    memorias = contexto["memorias"]
    emocion = contexto["emocion_visitante"]

    recuerdos_texto = "\n".join(
        f"- {m.get('contenido', '')} [tipo={m.get('tipo', 'otro')}; importancia={m.get('importancia', 3)}/5]"
        for m in memorias if m.get("contenido")
    ) or "- No hay recuerdos relevantes registrados."

    return f"""IDENTIDAD
Nombre: {identidad['nombre']}
Biografía: {identidad['bio'] or 'No registrada.'}
Nacimiento: {identidad['fecha_nacimiento'] or 'desconocido'}
Fallecimiento: {identidad['fecha_fallecimiento'] or 'desconocido'}
Lugar de nacimiento: {identidad['lugar_nacimiento'] or 'desconocido'}
Lugar de fallecimiento: {identidad['lugar_fallecimiento'] or 'desconocido'}

PERSONALIDAD
Rasgos: {personalidad['rasgos']}
Valores: {personalidad['valores']}
Temperamento: {personalidad['temperamento']}
Comunicación: {personalidad['comunicacion']}
Humor: {personalidad['humor']}
Gustos: {personalidad['gustos']}
Disgustos: {personalidad['disgustos']}
Reglas: {personalidad['reglas']}

MEMORIAS RELEVANTES
{recuerdos_texto}

ESTADO CONTEXTUAL DEL VISITANTE
Emoción: {emocion.get('emocion', 'neutral')}
Intensidad: {emocion.get('intensidad', 0.0)}
Confianza: {emocion.get('confianza', 0.0)}
"""
