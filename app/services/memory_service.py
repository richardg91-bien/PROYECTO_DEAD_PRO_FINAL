"""Servicio de gestión de memoria en Supabase"""

from flask import current_app


def construir_contexto_persona(persona, memorias, perfil_texto):
    """Construye un contexto breve y vivo para que la IA hable como la persona."""
    memorias_texto = "\n".join(
        f"- {mem.get('contenido', '')}" for mem in memorias if mem.get('contenido')
    )

    return f"""
Persona: {persona}
Perfil: {perfil_texto}
Memorias relevantes:
{memorias_texto or '- Sin memorias previas'}
""".strip()


def construir_perfil_inicial(persona, descripcion, title, description):
    """Genera un perfil de personalidad corto y utilizable por la IA."""
    base = f"{persona} es una persona con presencia, energía y una forma muy expresiva de comunicarse."
    if descripcion:
        base += f" Descripción visual: {descripcion}."
    if title:
        base += f" Contexto del recuerdo: {title}."
    if description:
        base += f" Notas del registro: {description}."
    return base.strip()


def construir_prompt_memorial(persona, perfil_texto, mensaje_usuario, emocion):
    """Construye un prompt orientado a una experiencia memorial con saludo inicial y preguntas personales."""
    estilo = {
        "feliz": "responde con entusiasmo, calidez y una energía alegre.",
        "triste": "responde con ternura, calma y mucha sensibilidad.",
        "enojado": "responde con serenidad, firmeza y un tono sereno.",
    }.get((emocion or "neutral").lower(), "responde con naturalidad, cercanía y autenticidad.")

    return f"""
Eres {persona}, una presencia virtual creada para recordar y acompañar a quien visita esta memoria.
Tu objetivo es responder con calidez, respeto y naturalidad, como si fueras la misma persona.

Estado emocional del usuario: {emocion}
Perfil memorial: {perfil_texto}

Inicio de conversación:
- Saludo: inicia con un saludo breve, humano y cercano.
- Pregunta personal: si el usuario aún no te ha dado información íntima, invítale a compartir algo personal, un recuerdo, una emoción o una anécdota.
- Aprendizaje continuo: cada conversación nueva debe sumar detalles al perfil y a la memoria de {persona}.
- Estilo emocional: {estilo}

Mensaje del usuario:
{mensaje_usuario}

Responde de forma empática, animada y auténtica, sin decir que eres IA.
""".strip()


def obtener_estado_avatar(emocion):
    """Devuelve un estado visual para el avatar según la emoción detectada."""
    estado = (emocion or "neutral").lower()
    if estado in {"feliz", "alegre", "contento"}:
        return "feliz"
    if estado in {"triste", "melancolico", "sad"}:
        return "triste"
    if estado in {"enojado", "angry", "enojo"}:
        return "enojado"
    return "neutral"


def construir_url_avatar(nombre_archivo):
    """Genera una ruta de avatar a partir de la imagen subida."""
    if not nombre_archivo:
        return "/static/uploads/default_avatar.png"
    return f"/static/uploads/{nombre_archivo}"

def guardar_memoria(persona, contenido, embedding, tipo='conversacion'):
    """
    Guarda una memoria en Supabase, incluyendo el tipo de memoria.
    
    Args:
        persona (str): Nombre de la persona
        contenido (str): Contenido del recuerdo
        embedding (list): Vector embedding del contenido
        tipo (str): Tipo de memoria ('conversacion' o 'experiencia')
        
    Returns:
        bool: True si se guardó exitosamente, False si hubo error
    """
    try:
        # Convierte embedding a lista si es numpy array u otro tipo
        if hasattr(embedding, "tolist"):
            embedding = embedding.tolist()

        response = current_app.supabase.table("aria_embeddings").insert({
            "persona": persona,
            "contenido": contenido,
            "embedding": embedding,
            "tipo": tipo
        }).execute()

        # Verifica el estado de la respuesta para confirmar éxito o fallo
        if hasattr(response, "error") and response.error is None:
            return True
        elif hasattr(response, "status_code") and response.status_code in (200, 201):
            return True
        else:
            print(f"❌ ERROR guardar_memoria: {response}")
            return False

    except Exception as e:
        print(f"❌ EXCEPCION guardar_memoria: {e}")
        return False

def obtener_memorias_personaje(persona, embedding, threshold=0.5, limit=5):
    """
    Obtiene memorias semánticas relacionadas de un personaje usando función RPC en Supabase.
    
    Args:
        persona (str): Nombre del personaje.
        embedding (list): Vector embedding para búsqueda.
        threshold (float): Umbral mínimo para similitud aceptable.
        limit (int): Máximo de memorias a recuperar.
        
    Returns:
        list: Lista de memorias (diccionarios) encontradas.
    """
    try:
        response = current_app.supabase.rpc(
            "match_documents",
            {
                "query_embedding": embedding,
                "match_threshold": threshold,
                "match_count": limit
            }
        ).execute()

        # Si no hay datos, retorna lista vacía
        if not response.data:
            return []

        # Filtra por persona, excluyendo memorias de otros usuarios (opcional)
        return [mem for mem in response.data if mem.get("persona") in (None, persona)]

    except Exception as e:
        print(f"❌ ERROR obtener_memorias_personaje: {e}")
        return []
