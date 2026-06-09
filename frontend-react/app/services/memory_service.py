"""Servicio de gestión de memoria en Supabase"""

from flask import current_app


def guardar_memoria(persona, contenido, embedding):
    """
    Guarda memoria en Supabase.
    
    Args:
        persona (str): Nombre de la persona
        contenido (str): Contenido del recuerdo
        embedding (list): Vector embedding del contenido
        
    Returns:
        bool: True si se guardó exitosamente, False si hubo error
    """
    try:
        if hasattr(embedding, "tolist"):
            embedding = embedding.tolist()

        current_app.supabase.table("aria_embeddings").insert({
            "persona": persona,
            "contenido": contenido,
            "embedding": embedding
        }).execute()
        
        return True

    except Exception as e:
        print(f"❌ ERROR guardar_memoria: {e}")
        return False


def obtener_memorias_personaje(persona, embedding, threshold=0.3, limit=5):
    """
    Obtiene memorias semánticas relacionadas de un personaje.
    
    Args:
        persona (str): Nombre del personaje
        embedding (list): Vector embedding para búsqueda
        threshold (float): Umbral de similitud
        limit (int): Máximo de resultados
        
    Returns:
        list: Memorias encontradas
    """
    try:
        response = current_app.supabase.rpc("match_documents", {
            "query_embedding": embedding,
            "match_threshold": threshold,
            "match_count": limit
        }).execute()
        
        return response.data or []
    
    except Exception as e:
        print(f"❌ ERROR obtener_memorias: {e}")
        return []
