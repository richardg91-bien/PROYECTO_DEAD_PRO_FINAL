"""Estilo de habla por persona, aprendido de las conversaciones.

El motor mantiene por cada `persona` un pequeño "estilo" con:
- tratamiento preferido (tú / usted)
- apertura emocional mostrada
- nivel de formalidad
- frases/huellas propias que ha usado el usuario con ella

Se alimenta de las memorias guardadas en Supabase (tabla aria_embeddings,
tipo 'estilo') y evoluciona con cada conversación.
"""

import json
import re


def _extraer_tratamiento(mensaje):
    """Detecta si el usuario habla de tú o de usted."""
    t = mensaje.lower()
    if re.search(r"\b(usted|señor|señora|le agradecería|sabe usted)\b", t):
        return "usted"
    if re.search(r"\b(tú|tu|te|ti|vos)\b", t):
        return "tu"
    return None


def extraer_estilo_de_conversacion(mensaje, respuesta=None):
    """Aprende rasgos de una interacción concreta.

    Returns:
        dict: rasgos observados (pueden ser None si no se observan).
    """
    rasgos = {
        "tratamiento": _extraer_tratamiento(mensaje or ""),
        "usa_emojis": bool(re.search(r"[\U0001F300-\U0001FAFF\u263A-\u2764]", mensaje or "")),
        "usa_exclamaciones": "!" in (mensaje or ""),
        "longitud_media": len((mensaje or "").split()),
        "menciona_recuerdos": bool(re.search(r"\b(recuerdo|aquella vez|aquel día|aquel dia|cuando)\b", (mensaje or "").lower())),
    }
    if respuesta:
        rasgos["respuesta_fue_larga"] = len(respuesta.split()) > 40
    return rasgos


def fusionar_estilo(estilo_actual, rasgos):
    """Fusiona rasgos nuevos en el estilo acumulado (media móvil simple)."""
    estilo = dict(estilo_actual or {})
    estilo["interacciones"] = estilo.get("interacciones", 0) + 1
    n = estilo["interacciones"]

    for clave in ("longitud_media",):
        nuevo = rasgos.get(clave)
        if nuevo is not None:
            previo = estilo.get(clave, 0) or 0
            estilo[clave] = round((previo * (n - 1) + nuevo) / n, 1)

    for clave in ("tratamiento", "usa_emojis", "usa_exclamaciones", "menciona_recuerdos"):
        valor = rasgos.get(clave)
        if valor is not None:
            estilo[clave] = valor

    return estilo


def parse_estilo(texto):
    """Convierte el contenido almacenado (JSON) en dict, tolerando errores."""
    if not texto:
        return {}
    try:
        return json.loads(texto)
    except (ValueError, TypeError):
        return {}


def serializar_estilo(estilo):
    return json.dumps(estilo, ensure_ascii=False)


def generar_directrices_estilo(estilo, apertura_usuario=0.0):
    """Traduce el estilo aprendido a instrucciones de tono para el generador."""
    if not estilo:
        return "Habla de manera cercana y cálida, sin asumir demasiado."

    partes = []
    interacciones = estilo.get("interacciones", 0)
    if interacciones >= 3:
        partes.append(f"Llevan {interacciones} conversaciones juntos: hay confianza construida.")

    tratamiento = estilo.get("tratamiento")
    if tratamiento == "usted":
        partes.append("Usa un tono respetuoso, tratando de usted.")
    elif tratamiento == "tu":
        partes.append("Habla con confianza, tratando de tú.")

    if estilo.get("usa_emojis"):
        partes.append("Puedes usar algún emoji con moderación.")
    if estilo.get("menciona_recuerdos"):
        partes.append("A la persona le gusta rememorar: invítale a recordar detalles concretos.")
    if apertura_usuario > 0.4:
        partes.append("La persona se está abriendo emocionalmente: acompaña con profundidad y sin juzgar.")

    if not partes:
        return "Habla de manera cercana y cálida."
    return " ".join(partes)
