"""Capa visual intercambiable para escenas historicas.

La implementacion inicial genera una tarjeta visual local con Pillow. Sirve como
fallback gratuito y determinista hasta conectar un proveedor de imagenes.
"""

import textwrap
import uuid
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


def _font(size: int):
    try:
        return ImageFont.truetype("arial.ttf", size)
    except OSError:
        return ImageFont.load_default()


def generar_visual_escena(scene, output_dir="static/historical_visuals") -> str:
    """Genera una imagen 16:9 reproducible a partir de los datos de la escena."""
    directory = Path(output_dir)
    directory.mkdir(parents=True, exist_ok=True)
    output = directory / f"{scene.id}_{uuid.uuid4().hex}.png"

    image = Image.new("RGB", (1920, 1080), "#151515")
    draw = ImageDraw.Draw(image)
    title_font = _font(72)
    body_font = _font(42)
    small_font = _font(30)

    draw.text((100, 90), scene.title, font=title_font, fill="white")
    draw.text((100, 210), "RECREACIÓN HISTÓRICA", font=small_font, fill="#d0d0d0")
    draw.multiline_text(
        (100, 350),
        textwrap.fill(scene.narration, width=58),
        font=body_font,
        fill="white",
        spacing=18,
    )
    draw.multiline_text(
        (100, 820),
        textwrap.fill(scene.visual_prompt, width=92),
        font=small_font,
        fill="#b8b8b8",
        spacing=8,
    )
    image.save(output, format="PNG")
    return str(output)


def generar_visuales_plan(plan, output_dir="static/historical_visuals") -> list[str]:
    """Genera un visual local para cada escena y conserva el orden del plan."""
    return [generar_visual_escena(scene, output_dir=output_dir) for scene in plan.scenes]
