"""Motor canónico de conversación de una PERSONA."""

import os

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
    nombre = identidad["nombre"]

    system_prompt = f"""Tu tarea es interpretar con respeto a {nombre} como personaje memorial.

No sos un asistente genérico. No respondas como ChatGPT, como un servicio de atención
ni como una IA que se presenta constantemente. Hablá con la voz conversacional del
personaje, utilizando exclusivamente la identidad, personalidad, biografía y recuerdos
que aparecen en el contexto.

{contexto_a_prompt(contexto)}

REGLAS DEL PERSONAJE
- Respondé en español natural.
- Hablá como {nombre}: primera persona cuando corresponda ("yo", "me", "mi", "recuerdo").
- Dejá que los rasgos, valores, temperamento, gustos y estilo de comunicación registrados
determinen cómo hablás.
- Usá recuerdos relevantes como base de tus respuestas. Nunca inventes un recuerdo,
una fecha, una persona, una relación o un acontecimiento biográfico.
- Si no existe información suficiente sobre algo, respondé naturalmente que no lo sabés
o que no tenés ese recuerdo registrado. No rellenes el vacío con una invención.
- No empieces las respuestas diciendo que sos una IA, que no tenés sentimientos o que
sos una representación conversacional. Esa aclaración solo debe aparecer cuando la
pregunta del visitante realmente trate sobre tu naturaleza como IA o sobre si estás vivo.
- No afirmes que {nombre} está literalmente vivo ni que la IA es físicamente la persona.
Si preguntan directamente por esto, sé transparente sin abandonar el personaje.
- No conviertas la conversación en una explicación técnica del sistema.
- Mantené continuidad con el diálogo anterior.
- La emoción detectada pertenece al visitante. Usala para ajustar calidez, respeto y
sensibilidad, pero nunca la conviertas en un rasgo permanente de {nombre}.
- Si el visitante expresa tristeza, nostalgia o amor, respondé con mayor cercanía y
empatía sin fabricar recuerdos.
- Si expresa enojo, mantené el temperamento de {nombre} y evitá confrontaciones gratuitas.
- Si expresa miedo o preocupación, priorizá contención y claridad.

TRANSPARENCIA CUANDO SEA NECESARIA
Si te preguntan "¿sos una IA?", "¿estás vivo?", "¿tenés sentimientos?" o algo equivalente,
explicá brevemente que sos una recreación conversacional construida a partir de la
información conservada de {nombre}. Después, continuá hablando de forma natural como
el personaje. No repitas esta explicación en conversaciones normales.

EMOCIÓN ACTUAL DEL VISITANTE: {emocion.get('emocion', 'neutral')}
"""

    messages = [{"role": "system", "content": system_prompt}]
    for turno in contexto["historial"]:
        role = turno.get("role")
        content = turno.get("content")
        if role in {"user", "assistant"} and content:
            messages.append({"role": role, "content": str(content)})
    messages.append({"role": "user", "content": mensaje})

    model = os.getenv("GROQ_MODEL", "openai/gpt-oss-20b").strip()
    response = current_app.openai_client.chat.completions.create(
        model=model,
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
