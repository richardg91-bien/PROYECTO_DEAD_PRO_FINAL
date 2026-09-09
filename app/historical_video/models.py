"""Modelos de dominio para planificar un video historico antes del render."""

from dataclasses import asdict, dataclass, field
from typing import Any


@dataclass
class HistoricalScene:
    """Una escena audiovisual derivada del guion."""

    id: str
    title: str
    narration: str
    visual_prompt: str
    emotion: str = "neutral"
    duration_hint: float | None = None
    source_notes: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class HistoricalVideoPlan:
    """Plan serializable que conecta investigacion, narracion y escenas."""

    title: str
    subject: str
    language: str = "es"
    target_duration_seconds: int = 120
    scenes: list[HistoricalScene] = field(default_factory=list)
    disclaimer: str = "Recreacion audiovisual basada en fuentes historicas."

    def to_dict(self) -> dict[str, Any]:
        data = asdict(self)
        data["scenes"] = [scene.to_dict() for scene in self.scenes]
        return data
