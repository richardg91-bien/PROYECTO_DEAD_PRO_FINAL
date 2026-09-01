import os
import uuid

import requests
from gtts import gTTS

from app.voz_perfil import (
    MODEL_ID,
    VOICE_ID_DEFAULT,
    ajustes_por_afinidad,
    matiz_textual_por_afinidad,
    suavizar_prosodia,
)

AUDIO_FOLDER = "static/audio"
ELEVENLABS_URL = "https://api.elevenlabs.io/v1/text-to-speech/{voice_id}"


def _clave_elevenlabs():
    return os.getenv("ELEVENLABS_API_KEY") or ""


def _voice_id():
    return os.getenv("ELEVENLABS_VOICE_ID") or VOICE_ID_DEFAULT


def adaptar_texto_a_voz(texto, emocion=None, afinidad=None):
    """Adapta el texto para que suene más humano según emoción y vínculo."""
    if not texto:
        return texto

    estado = (emocion or "neutral").lower()
    texto = texto.strip()

    if estado in {"feliz", "alegre", "contento"}:
        texto = f"{texto} — qué gusto hablar contigo."
    elif estado in {"triste", "melancolico", "sad"}:
        texto = f"{texto} — gracias por estar aquí conmigo."
    elif estado in {"enojado", "angry", "enojo"}:
        texto = f"{texto} — quiero que me escuches con calma."

    # Coherencia emocional: el cierre refleja la confianza construida
    matiz = matiz_textual_por_afinidad(afinidad)
    if matiz and not texto.endswith(matiz):
        texto = f"{texto} {matiz}"

    # Diseño de voz: soft prosody + pausas naturales, siempre
    return suavizar_prosodia(texto)


def _generar_audio_elevenlabs(texto, ruta, afinidad=None):
    """Genera el audio con ElevenLabs; la voz se modula según la afinidad."""
    voice_id = _voice_id()
    url = ELEVENLABS_URL.format(voice_id=voice_id)
    ajustes, _matiz = ajustes_por_afinidad(afinidad)

    response = requests.post(
        url,
        headers={
            "xi-api-key": _clave_elevenlabs(),
            "Content-Type": "application/json",
            "Accept": "audio/mpeg",
        },
        json={
            "text": texto,
            "model_id": MODEL_ID,
            "voice_settings": ajustes,
        },
        timeout=60,
    )

    if response.status_code != 200:
        raise RuntimeError(f"ElevenLabs respondió {response.status_code}: {response.text[:200]}")

    with open(ruta, "wb") as f:
        f.write(response.content)
    return True


def generar_audio(texto, emocion=None, afinidad=None):
    """Genera el audio de la respuesta y lo guarda en static/audio/.

    La voz se modula según la afinidad acumulada con la persona:
    más contenida al principio, más cálida cuando hay confianza.

    Args:
        texto (str): texto a sintetizar.
        emocion (str | None): emoción detectada en la conversación.
        afinidad (float | None): 0-1, vínculo IA-persona (evolución).
    """
    if not texto:
        return None

    try:
        os.makedirs(AUDIO_FOLDER, exist_ok=True)

        nombre = f"{uuid.uuid4()}.mp3"
        ruta = os.path.join(AUDIO_FOLDER, nombre)
        texto_voz = adaptar_texto_a_voz(texto, emocion, afinidad)

        if _clave_elevenlabs():
            try:
                _generar_audio_elevenlabs(texto_voz, ruta, afinidad=afinidad)
                return nombre
            except Exception as e:
                print(f"⚠️ VOZ: ElevenLabs falló, usando gTTS local: {e}")

        tts = gTTS(text=texto_voz, lang="es")
        tts.save(ruta)

        return nombre

    except Exception as e:
        print(f"❌ ERROR VOZ: {e}")
        return None
