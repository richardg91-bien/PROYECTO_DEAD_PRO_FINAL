"""Detección ligera y contextual de emociones del visitante."""

EMOCIONES = {
    "triste": ["triste", "llorar", "extraño", "extrañar", "dolor", "mal", "peor", "nostalgia", "nostálgico", "nostálgica", "te extraño"],
    "feliz": ["feliz", "alegre", "contento", "contenta", "perfecto", "excelente", "felicidades", "gracias", "orgullo"],
    "enojado": ["enojado", "enojada", "bronca", "odio", "furioso", "furiosa", "rabia", "molesto", "molesta"],
    "amor": ["amor", "amo", "querido", "querida", "te quiero", "te quise", "cariño"],
    "miedo": ["miedo", "temor", "asustado", "asustada", "terror", "preocupado", "preocupada"],
}


def analizar_emocion(texto):
    """Devuelve emoción, intensidad y confianza sin modificar estado permanente."""
    if not texto:
        return {"emocion": "neutral", "intensidad": 0.0, "confianza": 0.0}

    t = str(texto).lower()
    puntuaciones = {nombre: sum(1 for palabra in palabras if palabra in t) for nombre, palabras in EMOCIONES.items()}
    emocion, puntos = max(puntuaciones.items(), key=lambda item: item[1])
    if puntos == 0:
        return {"emocion": "neutral", "intensidad": 0.0, "confianza": 0.0}

    palabras = max(len(t.split()), 1)
    intensidad = min(1.0, 0.35 + (puntos * 0.18) + (t.count("!") * 0.08))
    confianza = min(1.0, 0.45 + (puntos * 0.12) + (puntos / palabras))
    return {"emocion": emocion, "intensidad": round(intensidad, 2), "confianza": round(confianza, 2)}


def detectar_emocion(texto):
    """Compatibilidad legacy: devuelve solamente la etiqueta emocional."""
    return analizar_emocion(texto)["emocion"]
