"""Servicio de gestión de memoria en Supabase"""

from flask import current_app

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
