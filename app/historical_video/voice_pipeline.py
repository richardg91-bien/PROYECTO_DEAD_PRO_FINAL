"""Adaptador del servicio de voz existente para escenas de video histórico."""

from pathlib import Path
from urllib.parse import urlparse

from app.voz_service import generar_audio


def generar_audio_escena(scene):
    """Genera el audio de una escena usando el servicio de voz existente."""
    nombre = generar_audio(scene.narration)

    if not nombre:
        return None

    return f"/static/audio/{nombre}"


def resolver_audio_local(audio_url: str) -> Path:
    """Convierte la URL pública de audio en una ruta local segura."""
    if not audio_url:
        raise ValueError("URL de audio vacía")

    parsed = urlparse(audio_url)
    path = parsed.path or audio_url

    filename = Path(path).name

    if not filename or filename in {".", ".."}:
        raise ValueError("URL de audio inválida")

    output_dir = Path.cwd() / "static" / "audio"
    output_dir = output_dir.resolve()

    resolved = (output_dir / filename).resolve()

    if resolved.parent != output_dir:
        raise ValueError("Ruta de audio fuera del directorio permitido")

    return resolved