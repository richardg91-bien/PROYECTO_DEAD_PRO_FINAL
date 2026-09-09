"""Generacion de contenido historico verificable para el pipeline audiovisual.

Este modulo no inventa hechos: recibe el contenido narrativo y lo transforma en
un plan de escenas. La investigacion y validacion de fuentes queda separada de
la renderizacion.
"""

from dataclasses import dataclass

from .planner import crear_plan_video


@dataclass(frozen=True)
class HistoricalSource:
    title: str
    reference: str
    notes: str = ""


def crear_video_historico(
    subject: str,
    narration: str,
    title: str | None = None,
    sources: list[HistoricalSource] | None = None,
    target_duration_seconds: int = 120,
):
    """Construye el plan audiovisual a partir de una narracion ya validada.

    Las fuentes se incorporan como notas de procedencia de cada escena.
    """
    if not subject.strip():
        raise ValueError("El tema historico no puede estar vacio")
    if not narration.strip():
        raise ValueError("La narracion no puede estar vacia")

    source_notes = []
    for source in sources or []:
        line = f"{source.title}: {source.reference}"
        if source.notes:
            line += f" ({source.notes})"
        source_notes.append(line)

    return crear_plan_video(
        subject=subject,
        title=title or f"Historia de {subject}",
        narration=narration,
        source_notes=source_notes,
        target_duration_seconds=target_duration_seconds,
    )
