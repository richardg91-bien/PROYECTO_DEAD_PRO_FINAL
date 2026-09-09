"""Construccion determinista de un primer plan de video historico.

Este modulo no inventa hechos historicos: recibe narracion y referencias ya validadas
por la capa de investigacion y las convierte en escenas renderizables.
"""

import re
from .models import HistoricalScene, HistoricalVideoPlan


def _split_sentences(text: str) -> list[str]:
    text = re.sub(r"\s+", " ", str(text or "").strip())
    if not text:
        return []
    return [part.strip() for part in re.split(r"(?<=[.!?])\s+", text) if part.strip()]


def _duration(text: str, words_per_minute: int = 135) -> float:
    words = max(1, len(text.split()))
    return round((words / words_per_minute) * 60, 2)


def crear_plan_video(
    subject: str,
    title: str,
    narration: str,
    *,
    source_notes: list[str] | None = None,
    target_duration_seconds: int = 120,
) -> HistoricalVideoPlan:
    """Divide una narracion aprobada en escenas sin alterar sus hechos."""
    sentences = _split_sentences(narration)
    notes = source_notes or []
    scenes: list[HistoricalScene] = []

    for index, sentence in enumerate(sentences, start=1):
        scene_title = f"Escena {index}"
        visual_prompt = (
            f"Recreacion historica cinematografica relacionada con: {sentence}. "
            "Mantener rigor de epoca, vestuario y arquitectura; no introducir personas "
            "o acontecimientos no mencionados en las fuentes."
        )
        scenes.append(
            HistoricalScene(
                id=f"scene_{index:03d}",
                title=scene_title,
                narration=sentence,
                visual_prompt=visual_prompt,
                duration_hint=_duration(sentence),
                source_notes=notes,
            )
        )

    return HistoricalVideoPlan(
        title=title,
        subject=subject,
        target_duration_seconds=target_duration_seconds,
        scenes=scenes,
    )
