"""Render tecnico de escenas historicas con FFmpeg.

La capa visual es intercambiable y el audio puede ser MP3, WAV u otro formato
compatible con FFmpeg. El renderer utiliza la duracion real del archivo de audio
para sincronizar la escena.
"""

import os
import shutil
import subprocess
import uuid
from pathlib import Path


def resolver_ffmpeg() -> str:
    binary = os.getenv("FFMPEG_BINARY", "ffmpeg").strip() or "ffmpeg"
    resolved = shutil.which(binary)

    if resolved:
        return resolved

    return binary


def duracion_audio(audio_path: str | Path) -> float:
    """Obtiene la duracion real de un archivo de audio mediante FFmpeg."""
    path = Path(audio_path)

    if not path.is_file():
        raise FileNotFoundError(f"Audio no encontrado: {path}")

    ffmpeg = resolver_ffmpeg()

    command = [
        ffmpeg,
        "-i",
        str(path),
        "-f",
        "null",
        "-",
    ]

    try:
        result = subprocess.run(
            command,
            check=False,
            capture_output=True,
            text=True,
            timeout=60,
        )
    except (OSError, subprocess.SubprocessError) as exc:
        raise RuntimeError(
            f"No se pudo analizar la duracion del audio: {exc}"
        ) from exc

    # FFmpeg suele escribir la informacion de duracion en stderr.
    import re

    match = re.search(
        r"Duration:\s*(\d+):(\d+):(\d+(?:\.\d+)?)",
        result.stderr,
    )

    if not match:
        raise RuntimeError(
            f"FFmpeg no pudo determinar la duracion del audio: {path}"
        )

    hours = int(match.group(1))
    minutes = int(match.group(2))
    seconds = float(match.group(3))

    duration = hours * 3600 + minutes * 60 + seconds

    if duration <= 0:
        raise ValueError("El audio no tiene duracion valida")

    return duration


def duracion_wav(audio_path: str | Path) -> float:
    """Compatibilidad con el nombre anterior; ahora acepta cualquier audio."""
    return duracion_audio(audio_path)


def _output_dir() -> Path:
    path = Path(
        os.getenv(
            "HISTORICAL_VIDEO_OUTPUT_DIR",
            "static/videos",
        )
    )

    path.mkdir(parents=True, exist_ok=True)

    return path


def render_scene(
    audio_path: str | Path,
    output_path: str | Path | None = None,
    image_path: str | Path | None = None,
) -> str:
    """Crea un MP4 de una escena sincronizado con su audio."""

    audio = Path(audio_path)

    if not audio.is_file():
        raise FileNotFoundError(
            f"Audio no encontrado: {audio}"
        )

    duration = duracion_audio(audio)

    output = (
        Path(output_path)
        if output_path
        else _output_dir() / f"scene_{uuid.uuid4().hex}.mp4"
    )

    output.parent.mkdir(parents=True, exist_ok=True)

    ffmpeg = resolver_ffmpeg()

    if image_path:
        image = Path(image_path)

        if not image.is_file():
            raise FileNotFoundError(
                f"Imagen no encontrada: {image}"
            )

        command = [
            ffmpeg,
            "-y",
            "-loop",
            "1",
            "-i",
            str(image),
            "-i",
            str(audio),
            "-t",
            f"{duration:.3f}",
            "-r",
            "30",
            "-c:v",
            "libx264",
            "-pix_fmt",
            "yuv420p",
            "-c:a",
            "aac",
            "-shortest",
            str(output),
        ]

    else:
        command = [
            ffmpeg,
            "-y",
            "-f",
            "lavfi",
            "-i",
            "color=c=black:s=1920x1080:r=30",
            "-i",
            str(audio),
            "-t",
            f"{duration:.3f}",
            "-c:v",
            "libx264",
            "-pix_fmt",
            "yuv420p",
            "-c:a",
            "aac",
            "-shortest",
            str(output),
        ]

    try:
        subprocess.run(
            command,
            check=True,
            capture_output=True,
            text=True,
            timeout=max(60, int(duration) + 30),
        )

    except (OSError, subprocess.SubprocessError) as exc:
        raise RuntimeError(
            f"FFmpeg no pudo renderizar la escena: {exc}"
        ) from exc

    if not output.is_file() or output.stat().st_size == 0:
        raise RuntimeError(
            "FFmpeg no produjo un MP4 valido"
        )

    return str(output)