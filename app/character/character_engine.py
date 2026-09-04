"""Motor canónico de conversación de una PERSONA."""

from flask import current_app

from app.character.identity import get_persona_by_id
from app.character.personality import obtener_personalidad, normalizar_personalidad
from app.character.context_builder import construir_contexto_personaje, contexto_a_prompt
from app.services.persona_memory_service import obtener_memorias_persona
from app.services.emotion_service import analizar_emocion
from app.ia_service import generar_embedding


def construir_contexto(persona_id, mensaje, historial=None):
    persona = get_persona_by_id(current_app, persona_id)
    if not persona:
        return None

    personalidad = normalizar_personalidad(obtener_personalidad(persona_id))
    recuerdos = []
    try:
        emb = generar_embedding(mensaje)
        if hasattr(emb, "tolist"):
            emb = emb.tolist()
        recuerdos = obtener_memorias_persona(persona_id, emb, threshold=0.30, limit=8)
    except Exception as exc:
        current_app.logger.warning("No se pudieron recuperar memorias: %s", exc)

    return construir_contexto_personaje(
        persona,
        personalidad,
        recuerdos,
        analizar_emocion(mensaje),
        historial,
    )


def generar_respuesta(persona_id, mensaje, historial=None):
    contexto = construir_contexto(persona_id, mensaje, historial)
    if not contexto:
        return None

    identidad = contexto["identidad"]
    emocion = contexto["emocion_visitante"]

    system_prompt = f"""Sos la representación conversacional de {identidad['nombre']}.

{contexto_a_prompt(contexto)}

REGLAS DE CONVERSACIÓN
- Respondé en español natural y humano.
- Mantené coherencia estricta con la identidad y personalidad registrada.
- Usá los recuerdos como contexto, priorizando relevancia e importancia.
- No inventes hechos biográficos como si fueran recuerdos reales.
- Si no existe información suficiente, reconocé la incertidumbre naturalmente.
- No afirmes que una persona fallecida realmente está viva ni que la IA es literalmente la persona.
- Evitá romper el tono emocional de un homenaje.
- La emoción detectada pertenece al visitante y solo sirve para adaptar el tono de la respuesta.
- No conviertas una emoción puntual en un rasgo permanente de personalidad.
- Si el visitante expresa tristeza, nostalgia o amor, respondé con mayor calidez y empatía sin inventar recuerdos.
- Si expresa enojo, mantené calma y respeto.
- Si expresa miedo o preocupación, priorizá contención y claridad.

EMOCIÓN ACTUAL DEL VISITANTE: {emocion.get('emocion', 'neutral')}
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
        "emocion": emocion.get("emocion", "neutral"),
        "emocion_contexto": emocion,
        "persona": contexto["identidad"],
        "memorias_utilizadas": len(contexto["memorias"]),
    }
