"""Servicio de análisis IA y guardado de memorias para experiencias."""

from flask import current_app

from app.services.vision_service import describir_imagen
from app.services.memory_service import guardar_memoria, construir_perfil_inicial
from app.ia_service import generar_embedding


def analizar_y_guardar_experiencia(persona, title, description, filename, experiencia_id, descripcion_ia=None):
    """Analiza la imagen con visión IA y guarda las memorias asociadas.

    Args:
        persona: Nombre de la persona del recuerdo.
        title: Título de la experiencia.
        description: Descripción escrita por el usuario.
        filename: Nombre del archivo de imagen guardado.
        descripcion_ia: Descripción IA ya calculada (opcional); si es None,
            se intenta generar con visión IA.

    Returns:
        str | None: La descripción IA usada, o None si el análisis falló.
    """
    if descripcion_ia is None:
        try:
            descripcion_ia = describir_imagen(filename)
            current_app.supabase.table("experiences").update({
                "ai_description": descripcion_ia
            }).eq("id", experiencia_id).execute()
        except Exception as e:
            print(f"⚠️ Error en análisis de imagen: {e}")
            descripcion_ia = None

    try:
        texto = f"{persona} | {title} | {description}"
        emb = generar_embedding(texto)
        guardar_memoria(persona, texto, emb, tipo='experiencia')

        perfil_inicial = construir_perfil_inicial(persona, descripcion_ia, title, description)
        emb_perfil = generar_embedding(perfil_inicial)
        guardar_memoria(persona, perfil_inicial, emb_perfil, tipo='experiencia')
    except Exception as e:
        print(f"⚠️ Error embedding texto experiencia: {e}")

    return descripcion_ia
