"""Motor canónico de conversación de una PERSONA."""

from app.character.identity import get_persona_by_id
from app.character.personality import obtener_personalidad, normalizar_personalidad
from app.services.persona_memory_service import obtener_memorias_persona
from app.services.emotion_service import detectar_emocion
from app.ia_service import generar_embedding


def construir_contexto(persona_id, mensaje, historial=None):
    persona = get_persona_by_id(__import__('flask').current_app, persona_id)
    if not persona:
        return None

    personalidad = normalizar_personalidad(obtener_personalidad(persona_id))
    recuerdos = []
    try:
        emb = generar_embedding(mensaje)
        if hasattr(emb, "tolist"):
            emb = emb.tolist()
        recuerdos = obtener_memorias_persona(persona_id, emb, threshold=0.30, limit=6)
    except Exception as exc:
        print(f"⚠️ Error recuperando memorias de persona: {exc}")

    return {
        "persona": persona,
        "personalidad": personalidad,
        "recuerdos": recuerdos,
        "emocion_visitante": detectar_emocion(mensaje),
        "historial": (historial or [])[-10:],
    }


def generar_respuesta(persona_id, mensaje, historial=None):
    from flask import current_app

    contexto = construir_contexto(persona_id, mensaje, historial)
    if not contexto:
        return None

    persona = contexto["persona"]
    personalidad = contexto["personalidad"]
    recuerdos = contexto["recuerdos"]
    emocion = contexto["emocion_visitante"]

    recuerdos_texto = "\n".join(
        f"- {item.get('contenido', '')}" for item in recuerdos if item.get("contenido")
    ) or "- No hay recuerdos relevantes registrados."

    system_prompt = f"""Sos la representación conversacional de {persona.get('nombre', 'esta persona')}.

IDENTIDAD:
{persona.get('bio') or 'No hay biografía adicional registrada.'}
Nacimiento: {persona.get('fecha_nacimiento') or 'desconocido'}
Fallecimiento: {persona.get('fecha_fallecimiento') or 'desconocido'}
Lugar de nacimiento: {persona.get('lugar_nacimiento') or 'desconocido'}
Lugar de fallecimiento: {persona.get('lugar_fallecimiento') or 'desconocido'}

PERSONALIDAD:
{personalidad}

RECUERDOS RELEVANTES:
{recuerdos_texto}

EMOCIÓN DETECTADA DEL VISITANTE: {emocion}

REGLAS:
- Respondé en español natural y humano.
- Mantené coherencia con la identidad y personalidad registrada.
- No inventes hechos biográficos como si fueran recuerdos reales.
- Si no existe información suficiente, reconocé la incertidumbre de forma natural.
- No afirmes que una persona fallecida realmente está viva ni que la IA es literalmente la persona.
- Evitá romper el tono emocional de una conversación de homenaje.
"""

    messages = [{"role": "system", "content": system_prompt}]
    for turno in contexto["historial"]:
        role = turno.get("role")
        content = turno.get("content")
        if role in {"user", "assistant"} and content:
            messages.append({"role": role, "content": str(content)})
    messages.append({"role": "user", "content": mensaje})

    response = current_app.openai_client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=messages,
        max_tokens=350,
    )
    return {
        "respuesta": response.choices[0].message.content.strip(),
        "emocion": emocion,
        "persona": persona,
    }
