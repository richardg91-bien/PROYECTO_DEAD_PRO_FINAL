"""Servicio de detección de emociones"""


def detectar_emocion(texto):
    """
    Detecta emoción basada en palabras clave.
    
    Args:
        texto (str): Texto a analizar
        
    Returns:
        str: Emoción detectada ('triste', 'feliz', 'enojado', 'neutral')
    """
    if not texto:
        return "neutral"
    
    t = texto.lower()

    if any(x in t for x in ["triste", "llorar", "extraño", "dolor", "mal", "peor"]):
        return "triste"
    if any(x in t for x in ["feliz", "alegre", "contento", "perfecto", "excelente"]):
        return "feliz"
    if any(x in t for x in ["enojado", "bronca", "odio", "furioso", "rabia"]):
        return "enojado"
    
    return "neutral"
