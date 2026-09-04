"""Síntesis de voz de una PERSONA mediante Piper TTS.

El servicio es opcional: si Piper no está instalado o configurado, devuelve None
sin romper la conversación. La emoción del visitante solo ajusta la prosodia.
"""

import os
import shutil
import subprocess
import sys
import uuid
from pathlib import Path

from flask import current_app


PROSODIA = {
    "neutral": {"length_scale": 1.0, "noise_scale": 0.667, "noise_w_scale": 0.8},
    "triste": {"length_scale": 1.12, "noise_scale": 0.58, "noise_w_scale": 0.7},
    "amor": {"length_scale": 1.06, "noise_scale": 0.62, "noise_w_scale": 0.72},
    "feliz": {"length_scale": 0.92, "noise_scale": 0.72, "noise_w_scale": 0.9},
    "enojado": {"length_scale": 0.94, "noise_scale": 0.70, "noise_w_scale": 0.86},
    "miedo": {"length_scale": 1.08, "noise_scale": 0.60, "noise_w_scale": 0.72},
}


def _config():
    binary = os.getenv("PIPER_BINARY", "piper").strip()
    model = os.getenv("PIPER_MODEL", "").strip()
    return binary, model


def _resolver_piper(binary):
    """Resuelve Piper de forma fiable dentro del .venv, especialmente en Windows."""
    candidate = Path(binary)
    if candidate.is_file():
        return str(candidate)

    resolved = shutil.which(binary)
    if resolved:
        return resolved

    if os.name == "nt":
        scripts_dir = Path(sys.executable).resolve().parent
        for name in ("piper.exe", "piper"):
            candidate = scripts_dir / name
            if candidate.is_file():
                return str(candidate)

    return binary


def _audio_dir():
    configured = os.getenv("PIPER_OUTPUT_DIR", "").strip()
    if configured:
        path = Path(configured)
    else:
        path = Path(current_app.root_path).parent / "static" / "audio"
    path.mkdir(parents=True, exist_ok=True)
    return path


def sintetizar_voz(texto, emocion="neutral"):
    """Genera WAV y devuelve su URL pública relativa, o None si no está disponible."""
    texto = str(texto or "").strip()
    if not texto:
        return None

    binary, model = _config()
    if not model:
        current_app.logger.info("Piper no configurado: PIPER_MODEL está vacío")
        return None

    binary = _resolver_piper(binary)
    prosodia = PROSODIA.get(str(emocion or "neutral").lower(), PROSODIA["neutral"])
    filename = f"persona_{uuid.uuid4().hex}.wav"
    output_path = _audio_dir() / filename

    command = [
        binary,
        "--model", model,
        "--output_file", str(output_path),
        "--length_scale", str(prosodia["length_scale"]),
        "--noise_scale", str(prosodia["noise_scale"]),
        "--noise_w_scale", str(prosodia["noise_w_scale"]),
    ]

    try:
        subprocess.run(
            command,
            input=texto,
            text=True,
            capture_output=True,
            check=True,
            timeout=30,
        )
    except (OSError, subprocess.SubprocessError) as exc:
        current_app.logger.warning("Piper no pudo sintetizar voz: %s", exc)
        output_path.unlink(missing_ok=True)
        return None

    if not output_path.is_file() or output_path.stat().st_size == 0:
        current_app.logger.warning("Piper no produjo un archivo de audio válido")
        output_path.unlink(missing_ok=True)
        return None

    return f"/static/audio/{filename}"
