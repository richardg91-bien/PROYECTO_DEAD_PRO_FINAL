"""Perfil de voz de la IA propia — diseño de voz "calma elegante y confiable".

Traducción técnica de la búsqueda:
- calm / low arousal        → stability alta (0.80), sin urgencia
- warm professionalism      → voz femenina cálida (Aria/Emma/Luna)
- soft prosody              → suavizado de puntuación y finales de frase
- pausas naturales          → elipsis y comas insertadas (natural breaks)
- speech rate lenta-media   → speed 0.9x

Motor preferente: ElevenLabs (eleven_multilingual_v2, soporta español).
Sin clave configurada, se degrada a gTTS local manteniendo el texto suavizado.
"""

# Voz por defecto: Aria (femenina, calmada, profesional). Cambiable por .env:
#   Emma  → pFZP5JQG7iQjIQuC4Bku (británica, elegante, formal)
#   Aria  → 9BWtsMINqrJLrRacOk9x (cálida, profesional, segura)
#   Luna / Serena: buscar ID en el catálogo de ElevenLabs
VOICE_ID_DEFAULT = "9BWtsMINqrJLrRacOk9x"
MODEL_ID = "eleven_multilingual_v2"

# Ajustes clave (diseño psicológico de la voz confiable):
#   pausada, predecible, suave en finales, sin emociones fuertes.
VOICE_SETTINGS = {
    "stability": 0.80,          # 70–85%: calm / low arousal
    "similarity_boost": 0.60,   # 50–70%: fidelidad cálida
    "style": 0.10,              # style exaggeration bajo
    "use_speaker_boost": True,
    "speed": 0.90,              # speech rate lenta-media
}

# Prompt de estilo (para motores que acepten instrucciones o para logs/auditoría)
SYSTEM_PROMPT_VOZ = (
    "You are a calm, elegant and trustworthy female assistant. "
    "Speak slowly and clearly. Use soft tone and natural pauses. "
    "Avoid excitement or urgency. Be warm, professional and reassuring."
)


def ajustes_por_afinidad(afinidad=None):
    """Modula la voz según el vínculo acumulado con la persona.

    El diseño base (calma, elegancia) nunca se rompe; solo se intensifica
    la cercanía emocional a medida que crece la afinidad:

    - afinidad baja  (<0.3): voz más neutra y contenida (recién se conocen)
    - afinidad media (0.3-0.6): el diseño base
    - afinidad alta  (>0.6): un punto más cálida y expresiva (cómplices)

    Returns:
        tuple[dict, str]: (voice_settings ajustados, matiz de tono descriptivo)
    """
    ajustes = dict(VOICE_SETTINGS)
    if afinidad is None:
        return ajustes, "neutral"

    try:
        afinidad = float(afinidad)
    except (TypeError, ValueError):
        return ajustes, "neutral"

    if afinidad < 0.3:
        # Contenida: máxima estabilidad, mínima expresividad
        ajustes["stability"] = 0.85
        ajustes["style"] = 0.05
        return ajustes, "contenida"
    if afinidad > 0.6:
        # Cómplices: un poco más de calidez sin perder la calma
        ajustes["stability"] = 0.72
        ajustes["style"] = 0.18
        ajustes["speed"] = 0.92
        return ajustes, "cálida"
    return ajustes, "neutral"


def matiz_textual_por_afinidad(afinidad=None):
    """Frase de cierre sutil según el vínculo (coherencia emocional voz-texto)."""
    if isinstance(afinidad, (int, float)) and afinidad > 0.6:
        return "Siempre es un placer conversar contigo."
    if isinstance(afinidad, (int, float)) and afinidad < 0.3:
        return "Es un gusto conocerte."
    return ""


def suavizar_prosodia(texto):
    """Suaviza la entonación del texto para una voz calmada y humana.

    - Convierte exclamaciones en afirmaciones suaves (sin energía agresiva).
    - Añade pausas naturales (comas/elipsis) al inicio y en enumeraciones.
    - Termina con punto suave, nunca con signos agresivos.
    """
    if not texto:
        return texto

    t = texto.strip()

    # Sin energía agresiva: "¡...!" → frase llana
    while "¡" in t and "!" in t:
        inicio = t.index("¡")
        fin = t.index("!")
        t = t[:inicio] + t[inicio + 1:fin] + t[fin + 1:]
    t = t.replace("!", ".").replace("¡", "")

    # Pausas naturales en enumeraciones y contrastes (respira entre ideas)
    t = t.replace(". ", "… ", 1)

    # Pausa contemplativa tras saludos y conectores de apertura
    for apertura in ("Hola", "Te escucho", "Gracias", "Mira", "Claro"):
        if t.startswith(apertura):
            t = t[:len(apertura)] + "…" + t[len(apertura):].lstrip(",")
            break

    # Final suave: los finales de frase definen la percepción de calma
    if t and t[-1] in ".?!":
        t = t[:-1] + "."
    return t
