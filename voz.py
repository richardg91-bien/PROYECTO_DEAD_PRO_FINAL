"""Generacion de audio TTS con gTTS.

Puede usarse como modulo importable o como script CLI:

    # Como modulo (desde voz_service.py u otro lugar del backend):
    from voz import generar_audio
    ruta = generar_audio("Hola mundo")

    # Como CLI (uso legado — preferir el modulo):
    python voz.py "Hola mundo"
"""

from __future__ import annotations

import os
import sys
import uuid


def generar_audio(texto: str, directorio: str = "static/audio") -> str:
    """Genera un archivo MP3 con el texto recibido y devuelve la ruta."""
    try:
        from gtts import gTTS
    except ImportError as exc:
        raise RuntimeError(
            "gTTS no esta instalado. Ejecuta: pip install gTTS"
        ) from exc

    os.makedirs(directorio, exist_ok=True)
    filename = f"{uuid.uuid4()}.mp3"
    ruta = os.path.join(directorio, filename)

    tts = gTTS(text=texto, lang="es")
    tts.save(ruta)
    return ruta


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Uso: python voz.py '<texto>'", file=sys.stderr)
        sys.exit(1)
    print(generar_audio(sys.argv[1]))
