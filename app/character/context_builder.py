"""Construcción del contexto canónico que recibe el Character Engine."""


def _lista(valor):
    if isinstance(valor, list):
        return valor
    if valor is None:
        return []
    return [valor]


def _seccion_personalidad(personalidad):
    p = personalidad or {}
    return {
        "rasgos": p.get("traits") or {},
        "valores": p.get("values") or {},
        "temperamento": p.get("temperament") or {},
        "comunicacion": p.get("communication_style") or {},
        "humor": p.get("humor_style") or {},
        "gustos": _lista(p.get("likes")),
        "disgustos": _lista(p.get("dislikes")),
        "reglas": _lista(p.get("behavioral_rules")),
    }


def construir_contexto_personaje(persona, personalidad, recuerdos, emocion_visitante, historial=None):
    """Devuelve un contexto estable y serializable para el prompt del LLM.

    La emoción del visitante es contextual y no altera la personalidad permanente.
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
        "personalidad": _seccion_personalidad(personalidad),
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
