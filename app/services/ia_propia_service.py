"""Puente entre la app Flask y el motor de IA propio.

Prioridad: motor propio (local, empático, evolutivo) → Groq como respaldo.

Uso principal: `generar_respuesta_propia(persona, mensaje, historial)`.
"""

from flask import current_app

from app.ia_core import get_motor
from app.ia_core.emociones import analizar_estado_emocional
from app.ia_core.estilo import (
    extraer_estilo_de_conversacion,
    fusionar_estilo,
    parse_estilo,
    serializar_estilo,
)
from app.ia_core.evolucion import (
    cargar_estado,
    guardar_estado,
    extraer_aprendizajes,
)


def _cargar_estilo(persona):
    try:
        res = current_app.supabase.table("aria_embeddings").select("contenido").match({
            "persona": persona, "tipo": "estilo"
        }).limit(1).execute()
        if res.data:
            return parse_estilo(res.data[0]["contenido"])
    except Exception as e:
        print(f"⚠️ Estilo: no se pudo cargar: {e}")
    return {}


def _guardar_estilo(persona, estilo):
    try:
        current_app.supabase.table("aria_embeddings").insert({
            "persona": persona,
            "contenido": serializar_estilo(estilo),
            "embedding": [0.0] * 8,
            "tipo": "estilo",
        }).execute()
    except Exception as e:
        print(f"⚠️ Estilo: no se pudo guardar: {e}")


def _hubo_respuesta_a_pregunta(historial, mensaje):
    """Determina si el usuario respondió con sustancia a una pregunta previa."""
    if not historial:
        return None
    ultima_ia = next((m for m in reversed(historial) if m.get("rol") in ("ia", "assistant")), None)
    if not ultima_ia:
        return None
    texto_ia = ultima_ia.get("texto") or ""
    if "?" not in texto_ia:
        return None
    return len((mensaje or "").split()) >= 3


def generar_respuesta_propia(persona, mensaje, historial=None, memorias=None, perfil=None):
    """Genera respuesta con el motor propio y registra la evolución.

    Returns:
        dict: {"respuesta", "emocion", "intensidad", "duelo", "nivel", "nombre_nivel", "motor": "propio"}
    """
    historial = historial or []

    # 1. Cargar estado de evolución y estilo aprendido
    estado_evolucion = cargar_estado(persona)
    estilo = _cargar_estilo(persona)

    # 2. Detectar si responde a una pregunta previa (para evolucionar)
    respondio_pregunta = _hubo_respuesta_a_pregunta(historial, mensaje)

    # 3. Aprender cosas nuevas del mensaje
    for dato in extraer_aprendizajes(mensaje):
        estado_evolucion.aprender(dato)

    # 4. Generar respuesta con el motor
    motor = get_motor(evolucion=estado_evolucion)
    resultado = motor.responder(mensaje, memorias=memorias, perfil=perfil,
                                estilo=estilo, historial=historial)

    # 5. Evolucionar con esta interacción y persistir
    estado_emocional = analizar_estado_emocional(mensaje)
    estado_evolucion.registrar_interaccion(estado_emocional, respondio_pregunta)
    guardar_estado(estado_evolucion)

    # 6. Evolucionar estilo de habla
    rasgos = extraer_estilo_de_conversacion(mensaje, resultado["respuesta"])
    nuevo_estilo = fusionar_estilo(estilo, rasgos)
    _guardar_estilo(persona, nuevo_estilo)

    resultado["nivel"] = estado_evolucion.nivel
    resultado["nombre_nivel"] = estado_evolucion.nombre_nivel
    resultado["motor"] = "propio"
    return resultado


def responder_con_respaldo(persona, mensaje, historial=None, memorias=None, perfil=None):
    """Motor propio primero; si falla todo, intenta Groq como último recurso.

    Returns:
        tuple[dict | None, str]: (resultado, motor_usado) — motor_usado ∈ {"propio", "groq", "ninguno"}
    """
    try:
        resultado = generar_respuesta_propia(persona, mensaje, historial=historial,
                                             memorias=memorias, perfil=perfil)
        if resultado.get("respuesta"):
            return resultado, "propio"
    except Exception as e:
        print(f"⚠️ Motor propio falló, usando respaldo: {e}")

    # Respaldo: Groq
    try:
        from app.routes import responder_con_ia
        cliente = getattr(current_app, "openai_client", None)
        if cliente:
            contexto = (perfil or "")
            if memorias:
                contexto += "\n" + "\n".join(m.get("contenido", "") for m in memorias[:3])
            prompt = (
                f"Eres {persona}. Responde con empatía y calidez, en español.\n"
                f"Contexto: {contexto}\nMensaje: {mensaje}"
            )
            respuesta = responder_con_ia(cliente, prompt)
            if respuesta:
                return {"respuesta": respuesta, "emocion": "neutral", "motor": "groq"}, "groq"
    except Exception as e:
        print(f"⚠️ Respaldo Groq falló: {e}")

    return None, "ninguno"
