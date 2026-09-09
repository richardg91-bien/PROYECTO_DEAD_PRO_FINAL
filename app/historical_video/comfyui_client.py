"""Cliente minimo para generar imagenes historicas mediante ComfyUI local.

El cliente usa solamente la API HTTP local de ComfyUI. No modifica Vision 1,
no requiere una API de pago y permite mantener Pillow como fallback.
"""

from __future__ import annotations

import json
import os
import random
import time
import urllib.error
import urllib.parse
import urllib.request
import uuid
from pathlib import Path


class ComfyUIError(RuntimeError):
    """Error producido al comunicarse con ComfyUI."""


def _base_url() -> str:
    return os.getenv("COMFYUI_URL", "http://127.0.0.1:8188").rstrip("/")


def _request(path: str, payload=None, timeout: float = 30.0):
    url = f"{_base_url()}{path}"
    data = None
    headers = {"Accept": "application/json"}
    if payload is not None:
        data = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        headers["Content-Type"] = "application/json"
    request = urllib.request.Request(url, data=data, headers=headers)
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            return response.read()
    except urllib.error.URLError as exc:
        raise ComfyUIError(f"No se pudo contactar ComfyUI en {_base_url()}: {exc}") from exc


def comprobar_comfyui() -> bool:
    """Comprueba que la API local de ComfyUI responde."""
    _request("/system_stats")
    return True


def _workflow(prompt: str, negative_prompt: str, seed: int, filename_prefix: str):
    """Construye un workflow API minimo compatible con SD 1.5."""
    checkpoint = os.getenv(
        "COMFYUI_CHECKPOINT",
        "v1-5-pruned-emaonly-fp16.safetensors",
    )
    steps = int(os.getenv("COMFYUI_STEPS", "15"))
    cfg = float(os.getenv("COMFYUI_CFG", "7"))
    sampler = os.getenv("COMFYUI_SAMPLER", "euler")
    scheduler = os.getenv("COMFYUI_SCHEDULER", "normal")
    width = int(os.getenv("COMFYUI_WIDTH", "512"))
    height = int(os.getenv("COMFYUI_HEIGHT", "512"))

    return {
        "1": {
            "class_type": "CheckpointLoaderSimple",
            "inputs": {"ckpt_name": checkpoint},
        },
        "2": {
            "class_type": "CLIPTextEncode",
            "inputs": {"text": prompt, "clip": ["1", 1]},
        },
        "3": {
            "class_type": "CLIPTextEncode",
            "inputs": {"text": negative_prompt, "clip": ["1", 1]},
        },
        "4": {
            "class_type": "EmptyLatentImage",
            "inputs": {"width": width, "height": height, "batch_size": 1},
        },
        "5": {
            "class_type": "KSampler",
            "inputs": {
                "seed": seed,
                "steps": steps,
                "cfg": cfg,
                "sampler_name": sampler,
                "scheduler": scheduler,
                "denoise": 1.0,
                "model": ["1", 0],
                "positive": ["2", 0],
                "negative": ["3", 0],
                "latent_image": ["4", 0],
            },
        },
        "6": {
            "class_type": "VAEDecode",
            "inputs": {"samples": ["5", 0], "vae": ["1", 2]},
        },
        "7": {
            "class_type": "SaveImage",
            "inputs": {"filename_prefix": filename_prefix, "images": ["6", 0]},
        },
    }


def generar_imagen(
    prompt: str,
    output_path: str | Path,
    negative_prompt: str | None = None,
    timeout_seconds: int = 300,
) -> str:
    """Genera una imagen con ComfyUI y la copia al path solicitado."""
    if not prompt.strip():
        raise ValueError("El prompt visual no puede estar vacio")

    output = Path(output_path)
    output.parent.mkdir(parents=True, exist_ok=True)
    negative = negative_prompt or (
        "modern, modern buildings, cars, electricity, modern clothes, technology, "
        "text, letters, logo, watermark, cartoon, anime, fantasy, distorted, "
        "deformed, blurry, low quality"
    )
    seed = random.randint(0, 2**63 - 1)
    prefix = f"historical_{uuid.uuid4().hex}"
    workflow = _workflow(prompt, negative, seed, prefix)

    response = json.loads(_request("/prompt", {"prompt": workflow}, timeout=30.0))
    prompt_id = response.get("prompt_id")
    if not prompt_id:
        raise ComfyUIError(f"ComfyUI no devolvio prompt_id: {response}")

    deadline = time.monotonic() + timeout_seconds
    history = None
    while time.monotonic() < deadline:
        try:
            history = json.loads(_request(f"/history/{prompt_id}", timeout=10.0))
        except ComfyUIError:
            history = None
        if history and prompt_id in history:
            break
        time.sleep(1.0)
    else:
        raise ComfyUIError(f"Tiempo agotado esperando la generacion {prompt_id}")

    entry = history[prompt_id]
    status = entry.get("status", {})
    if status.get("status_str") == "error" or status.get("completed") is False:
        raise ComfyUIError(f"ComfyUI fallo la generacion: {status}")

    images = []
    for node_output in entry.get("outputs", {}).values():
        images.extend(node_output.get("images", []))
    if not images:
        raise ComfyUIError("ComfyUI termino pero no devolvio ninguna imagen")

    image = images[0]
    query = urllib.parse.urlencode(
        {
            "filename": image["filename"],
            "subfolder": image.get("subfolder", ""),
            "type": image.get("type", "output"),
        }
    )
    data = _request(f"/view?{query}", timeout=60.0)
    output.write_bytes(data)
    return str(output)
