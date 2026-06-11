import os
import uuid
from gtts import gTTS

AUDIO_FOLDER = "static/audio"


def generar_audio(texto):
    """Genera audio usando gTTS y lo guarda en static/audio/."""
    try:
        os.makedirs(AUDIO_FOLDER, exist_ok=True)

        nombre = f"{uuid.uuid4()}.mp3"
        ruta = os.path.join(AUDIO_FOLDER, nombre)

        tts = gTTS(text=texto, lang="es")
        tts.save(ruta)

        return nombre

    except Exception as e:
        print(f"❌ ERROR VOZ: {e}")
        return None
