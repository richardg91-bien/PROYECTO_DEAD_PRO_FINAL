"""Adaptador del servicio Piper existente para escenas de video historico."""

import os
from pathlib import Path
from urllib.parse import urlparse

from app.voice.voice_service import sintetizar_voz


def generar_audio_escena(scene):
    """Genera el WAV de una escena usando el Piper canonico de Vision 1."""
    return sintetizar_voz(scene.narration, scene.emotion)


def resolver_audio_local(audio_url: str) -> Path:
    """Convierte la URL publica de Piper en una ruta local segura.

    El servicio canonico devuelve URLs como ``/static/audio/nombre.wav``.
    La ruta fisica real se obtiene desde ``PIPER_OUTPUT_DIR`` para respetar
    exactamente la configuracion existente de Vision 1.
    """
    if not audio_url:
        raise ValueError("URL de audio vacia")

    parsed = urlparse(audio_url)
    path = parsed.path or audio_url
    filename = Path(path).name
    if not filename or filename in {".", ".."}:
        raise ValueError("URL de audio invalida")

    configured_dir = os.getenv("PIPER_OUTPUT_DIR", "static/audio").strip() or "static/audio"
    output_dir = Path(configured_dir)
    if not output_dir.is_absolute():
        output_dir = Path.cwd() / output_dir

    resolved = (output_dir / filename).resolve()
    root = output_dir.resolve()
    if resolved.parent != root:
        raise ValueError("Ruta de audio fuera del directorio permitido")
    return resolved
