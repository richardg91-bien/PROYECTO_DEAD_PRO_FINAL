"""Render tecnico de escenas con FFmpeg.

La capa visual es deliberadamente intercambiable: por ahora puede renderizar una
escena desde una imagen existente o desde un fondo neutro. El audio siempre se
sincroniza con la duracion real del WAV de Piper.
"""

import os
import shutil
import subprocess
import uuid
import wave
from pathlib import Path


def resolver_ffmpeg() -> str:
    binary = os.getenv("FFMPEG_BINARY", "ffmpeg").strip() or "ffmpeg"
    resolved = shutil.which(binary)
    if resolved:
        return resolved
    return binary


def duracion_wav(audio_path: str | Path) -> float:
    path = Path(audio_path)
    with wave.open(str(path), "rb") as wav:
        frames = wav.getnframes()
        rate = wav.getframerate()
        if rate <= 0:
            raise ValueError("WAV con frecuencia de muestreo invalida")
        return frames / float(rate)


def _output_dir() -> Path:
    path = Path(os.getenv("HISTORICAL_VIDEO_OUTPUT_DIR", "static/videos"))
    path.mkdir(parents=True, exist_ok=True)
    return path


def render_scene(audio_path: str | Path, output_path: str | Path | None = None, image_path: str | Path | None = None) -> str:
    """Crea un MP4 de una escena y devuelve su ruta.

    Si no se suministra imagen, se utiliza un fondo negro; esto permite validar
    primero el pipeline de audio/sincronizacion antes de incorporar generacion visual.
    """
    audio = Path(audio_path)
    if not audio.is_file():
        raise FileNotFoundError(f"Audio no encontrado: {audio}")

    duration = duracion_wav(audio)
    if duration <= 0:
        raise ValueError("El audio no tiene duracion valida")

    output = Path(output_path) if output_path else _output_dir() / f"scene_{uuid.uuid4().hex}.mp4"
    output.parent.mkdir(parents=True, exist_ok=True)
    ffmpeg = resolver_ffmpeg()

    if image_path:
        image = Path(image_path)
        if not image.is_file():
            raise FileNotFoundError(f"Imagen no encontrada: {image}")
        command = [ffmpeg, "-y", "-loop", "1", "-i", str(image), "-i", str(audio), "-t", f"{duration:.3f}", "-r", "30", "-c:v", "libx264", "-pix_fmt", "yuv420p", "-c:a", "aac", "-shortest", str(output)]
    else:
        command = [ffmpeg, "-y", "-f", "lavfi", "-i", "color=c=black:s=1920x1080:r=30", "-i", str(audio), "-t", f"{duration:.3f}", "-c:v", "libx264", "-pix_fmt", "yuv420p", "-c:a", "aac", "-shortest", str(output)]

    try:
        subprocess.run(command, check=True, capture_output=True, text=True, timeout=max(60, int(duration) + 30))
    except (OSError, subprocess.SubprocessError) as exc:
        raise RuntimeError(f"FFmpeg no pudo renderizar la escena: {exc}") from exc

    if not output.is_file() or output.stat().st_size == 0:
        raise RuntimeError("FFmpeg no produjo un MP4 valido")
    return str(output)
