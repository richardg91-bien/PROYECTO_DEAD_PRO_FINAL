"""Análisis emocional local del motor de IA propio.

Detecta emoción, intensidad y señales de duelo sin depender de servicios externos.
Compatible con `app.services.emotion_service.detectar_emocion` (mismas etiquetas).
"""

DUELO_PALABRAS = (
    "extraño", "te extraño", "lo extraño", "la extraño", "ya no está", "ya no esta",
    "murió", "murio", "se fue para siempre", "duele tanto", "no lo supero",
    "cuando se fue", "desde que te fuiste", "echo de menos", "me hace falta",
)

TRISTEZA = ("triste", "llorar", "llorando", "dolor", "mal", "peor", "solo", "sola",
            "vacío", "vacio", "desanimado", "deprimido", "hundido", "grita", "angustia",
            "pena", "lágrimas", "lagrimas", "desapareció", "desaparecio")
ALEGRIA = ("feliz", "alegre", "contento", "contenta", "perfecto", "excelente", "genial",
           "gracias", "gracias por", "me encanta", "quiero mucho", "hermoso", "bonito",
           "reír", "reir", "risa", "sonreír", "sonreir", "buenísimo", "buenisimo")
ENOJO = ("enojado", "bronca", "odio", "furioso", "rabia", "molesto", "enfadado",
         "injusto", "harto", "cansado de", "estafado", "indignado", "cólera", "colera")
MIEDO = ("miedo", "asusta", "terror", "ansiedad", "nervioso", "nerviosa", "pánico", "panico",
         "angustiado", "preocupado", "preocupada", "inquieto", "inquieta")
AMOR = ("te amo", "te quiero", "amor", "cariño", "cariño mío", "querido", "querida",
        "abrazo", "beso", "corazón", "corazon", "contigo", "contigo siempre")

_EMOCIONES = {
    "triste": TRISTEZA + DUELO_PALABRAS,
    "feliz": ALEGRIA,
    "enojado": ENOJO,
    "ansioso": MIEDO,
    "amoroso": AMOR,
}

# Interés/vínculo: señales de apertura emocional del usuario
APERTURA = ("siempre", "nunca olvid", "recuerdo cuando", "mi vida", "sé que", "se que",
            "siento que", "creo que", "a veces", "contigo", "de ti", "de él", "de ella")


def detectar_emocion(texto):
    """Etiqueta simple compatible con el resto de la app."""
    if not texto:
        return "neutral"
    t = texto.lower()
    for etiqueta, palabras in _EMOCIONES.items():
        if any(p in t for p in palabras):
            return etiqueta
    return "neutral"


def analizar_estado_emocional(texto):
    """Análisis rico: emoción, intensidad (0-1), señales de duelo y apertura.

    Returns:
        dict: {"emocion", "intensidad", "duelo", "apertura"}
    """
    if not texto:
        return {"emocion": "neutral", "intensidad": 0.0, "duelo": False, "apertura": 0.0}

    t = texto.lower()

    # Conteo de señales por emoción
    conteos = {etq: sum(1 for p in pals if p in t) for etq, pals in _EMOCIONES.items()}
    duelo = any(p in t for p in DUELO_PALABRAS)

    if duelo:
        emocion = "triste"
    else:
        mejor = max(conteos, key=lambda k: conteos[k])
        emocion = mejor if conteos[mejor] > 0 else "neutral"

    # Intensidad: proporción de señales emocionales + énfasis (¡!, all caps, longitud)
    senales = sum(conteos.values())
    exclamaciones = texto.count("!")
    enfasis = sum(1 for w in texto.split() if w.isupper() and len(w) > 2)
    intensidad = min(1.0, 0.15 * senales + 0.1 * exclamaciones + 0.1 * enfasis)

    apertura = min(1.0, 0.2 * sum(1 for p in APERTURA if p in t))

    return {
        "emocion": emocion,
        "intensidad": round(intensidad, 2),
        "duelo": duelo,
        "apertura": round(apertura, 2),
    }
