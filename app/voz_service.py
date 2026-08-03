import os
import uuid
from gtts import gTTS

AUDIO_FOLDER = "static/audio"


def adaptar_texto_a_voz(texto, emocion=None):
    """Adapta el texto para que suene más humano según la emoción detectada."""
    if not texto:
        return texto

    estado = (emocion or "neutral").lower()
    texto = texto.strip()

    if estado in {"feliz", "alegre", "contento"}:
        return f"{texto} — qué gusto hablar contigo."
    if estado in {"triste", "melancolico", "sad"}:
        return f"{texto} — gracias por estar aquí conmigo."
    if estado in {"enojado", "angry", "enojo"}:
        return f"{texto} — quiero que me escuches con calma."
    return texto


def generar_audio(texto, emocion=None):
    """Genera audio usando gTTS y lo guarda en static/audio/."""
    try:
        os.makedirs(AUDIO_FOLDER, exist_ok=True)

        nombre = f"{uuid.uuid4()}.mp3"
        ruta = os.path.join(AUDIO_FOLDER, nombre)
        texto_voz = adaptar_texto_a_voz(texto, emocion)

        tts = gTTS(text=texto_voz, lang="es")
        tts.save(ruta)

        return nombre

    except Exception as e:
        print(f"❌ ERROR VOZ: {e}")
        return None
