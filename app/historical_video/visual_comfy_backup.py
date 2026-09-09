"""Proveedor visual para videos historicos.

Genera imagenes 16:9 con aspecto de storyboard cinematografico.
Esta implementacion es un fallback local y no depende de servicios externos.

La arquitectura permite sustituir posteriormente este proveedor por uno
de generacion de imagenes mediante IA sin modificar el pipeline de video.
"""

import hashlib
import textwrap
import uuid
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


WIDTH = 1920
HEIGHT = 1080


def _font(size: int):
    """Carga una fuente disponible en Windows o usa la fuente por defecto."""
    candidates = [
        Path(r"C:\Windows\Fonts\arial.ttf"),
        Path(r"C:\Windows\Fonts\georgia.ttf"),
        Path(r"C:\Windows\Fonts\times.ttf"),
    ]

    for path in candidates:
        if path.is_file():
            try:
                return ImageFont.truetype(str(path), size)
            except OSError:
                pass

    return ImageFont.load_default()


def _scene_seed(scene) -> int:
    """Obtiene una semilla estable a partir de los datos de la escena."""
    value = "|".join(
        [
            str(getattr(scene, "id", "")),
            str(getattr(scene, "title", "")),
            str(getattr(scene, "narration", "")),
        ]
    )

    digest = hashlib.sha256(value.encode("utf-8")).hexdigest()
    return int(digest[:8], 16)


def _background(seed: int) -> Image.Image:
    """Crea un fondo degradado oscuro con textura cinematografica."""
    image = Image.new("RGB", (WIDTH, HEIGHT))
    pixels = image.load()

    for y in range(HEIGHT):
        factor = y / HEIGHT

        for x in range(WIDTH):
            horizontal = x / WIDTH

            noise = ((seed + x * 13 + y * 7) % 17) - 8

            r = int(18 + 25 * (1 - factor) + noise)
            g = int(20 + 20 * (1 - factor) + noise)
            b = int(24 + 15 * horizontal + noise)

            pixels[x, y] = (
                max(0, min(255, r)),
                max(0, min(255, g)),
                max(0, min(255, b)),
            )

    return image


def _draw_vignette(image: Image.Image):
    """Oscurece suavemente los bordes para dar profundidad cinematografica."""
    overlay = Image.new("RGBA", image.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)

    draw.rectangle(
        (0, 0, WIDTH, 70),
        fill=(0, 0, 0, 150),
    )

    draw.rectangle(
        (0, HEIGHT - 120, WIDTH, HEIGHT),
        fill=(0, 0, 0, 180),
    )

    draw.rectangle(
        (0, 0, 120, HEIGHT),
        fill=(0, 0, 0, 90),
    )

    draw.rectangle(
        (WIDTH - 120, 0, WIDTH, HEIGHT),
        fill=(0, 0, 0, 90),
    )

    image.alpha_composite(overlay)


def _draw_scene_symbol(draw, scene, seed: int):
    """Dibuja una composicion visual sencilla relacionada con la escena.

    No pretende sustituir una imagen historica real. Es el fallback local
    mientras se conecta un proveedor de imagenes IA.
    """

    title = str(getattr(scene, "title", "")).lower()
    narration = str(getattr(scene, "narration", "")).lower()
    text = f"{title} {narration}"

    center_x = WIDTH // 2
    center_y = 520

    # Rio / agua
    if "tíber" in text or "tiber" in text or "río" in text or "rio" in text:
        for i in range(8):
            y = 400 + i * 45
            draw.arc(
                (
                    250 + i * 20,
                    y,
                    1670 - i * 20,
                    y + 100,
                ),
                0,
                180,
                fill=(100, 125, 145),
                width=5,
            )

    # Loba
    if "loba" in text:
        body = (center_x - 240, center_y - 80, center_x + 240, center_y + 120)
        draw.ellipse(body, outline=(175, 175, 165), width=12)

        draw.ellipse(
            (center_x + 150, center_y - 170, center_x + 330, center_y),
            outline=(175, 175, 165),
            width=12,
        )

        draw.polygon(
            [
                (center_x + 190, center_y - 160),
                (center_x + 160, center_y - 260),
                (center_x + 230, center_y - 190),
            ],
            outline=(175, 175, 165),
        )

        # Gemelos
        for offset in (-80, 80):
            draw.ellipse(
                (
                    center_x + offset - 40,
                    center_y + 80,
                    center_x + offset + 40,
                    center_y + 160,
                ),
                outline=(205, 190, 165),
                width=8,
            )

    # Hermanos / personas
    elif (
        "hermanos" in text
        or "pastor" in text
        or "remo" in text
        or "rómulo" in text
        or "romulo" in text
    ):
        for offset in (-150, 150):
            draw.ellipse(
                (
                    center_x + offset - 55,
                    center_y - 220,
                    center_x + offset + 55,
                    center_y - 110,
                ),
                outline=(190, 180, 160),
                width=10,
            )

            draw.line(
                (
                    center_x + offset,
                    center_y - 110,
                    center_x + offset,
                    center_y + 180,
                ),
                fill=(190, 180, 160),
                width=14,
            )

            draw.line(
                (
                    center_x + offset,
                    center_y,
                    center_x + offset - 120,
                    center_y + 100,
                ),
                fill=(190, 180, 160),
                width=10,
            )

            draw.line(
                (
                    center_x + offset,
                    center_y,
                    center_x + offset + 120,
                    center_y + 100,
                ),
                fill=(190, 180, 160),
                width=10,
            )

    # Ciudad / fundacion de Roma
    if "ciudad" in text or "roma" in text or "fundar" in text:
        base_y = 770

        for i in range(7):
            x = 430 + i * 180
            height = 120 + ((seed + i * 31) % 180)

            draw.rectangle(
                (
                    x,
                    base_y - height,
                    x + 120,
                    base_y,
                ),
                outline=(155, 145, 125),
                width=8,
            )

        draw.line(
            (300, base_y, 1620, base_y),
            fill=(170, 155, 130),
            width=10,
        )

    # Disputa
    if "disputa" in text or "matar" in text or "muerte" in text:
        draw.line(
            (
                center_x - 120,
                center_y,
                center_x + 120,
                center_y,
            ),
            fill=(180, 150, 125),
            width=8,
        )

        draw.line(
            (
                center_x - 80,
                center_y - 100,
                center_x + 80,
                center_y + 100,
            ),
            fill=(180, 150, 125),
            width=8,
        )


def generar_visual_escena(
    scene,
    output_dir="static/historical_visuals",
) -> str:
    """Genera un visual cinematografico local para una escena."""

    directory = Path(output_dir)
    directory.mkdir(parents=True, exist_ok=True)

    seed = _scene_seed(scene)

    image = _background(seed).convert("RGBA")
    draw = ImageDraw.Draw(image)

    title_font = _font(76)
    subtitle_font = _font(34)
    body_font = _font(40)
    small_font = _font(28)

    _draw_scene_symbol(draw, scene, seed)

    title = str(getattr(scene, "title", "Escena historica"))
    narration = str(getattr(scene, "narration", ""))
    visual_prompt = str(getattr(scene, "visual_prompt", ""))

    draw.text(
        (100, 70),
        title,
        font=title_font,
        fill=(235, 225, 205, 255),
    )

    draw.text(
        (100, 165),
        "RECREACION HISTORICA",
        font=subtitle_font,
        fill=(175, 165, 145, 255),
    )

    # Narracion breve en la parte inferior.
    narration_text = textwrap.fill(narration, width=72)

    draw.multiline_text(
        (100, 800),
        narration_text,
        font=body_font,
        fill=(230, 225, 215, 255),
        spacing=12,
    )

    # Prompt visual como informacion tecnica discreta.
    if visual_prompt:
        prompt_text = textwrap.fill(
            visual_prompt,
            width=110,
        )

        draw.multiline_text(
            (100, 970),
            prompt_text,
            font=small_font,
            fill=(145, 140, 130, 255),
            spacing=5,
        )

    _draw_vignette(image)

    filename = f"{scene.id}_{uuid.uuid4().hex}.png"
    output = directory / filename

    image.convert("RGB").save(
        output,
        format="PNG",
        optimize=True,
    )

    return str(output)


def generar_visuales_plan(
    plan,
    output_dir="static/historical_visuals",
) -> list[str]:
    """Genera exactamente un visual por cada escena del plan."""

    return [
        generar_visual_escena(
            scene,
            output_dir=output_dir,
        )
        for scene in plan.scenes
    ]