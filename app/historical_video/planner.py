"""Planificador determinista de escenas para videos historicos.

Divide una narracion en escenas y genera metadatos visuales y temporales
que pueden ser utilizados posteriormente por proveedores de imagenes IA.
"""

import re

from .models import HistoricalScene, HistoricalVideoPlan


def _split_sentences(text: str) -> list[str]:
    """Divide una narracion en frases conservando contenido util."""
    sentences = re.split(r"(?<=[.!?])\s+", text.strip())
    return [sentence.strip() for sentence in sentences if sentence.strip()]


def _duration(text: str, words_per_minute: int = 135) -> float:
    """Estima la duracion aproximada de la narracion en segundos."""
    words = len(text.split())

    if words == 0:
        return 0.0

    return round((words / words_per_minute) * 60, 2)


def _crear_visual_prompt(sentence: str, subject: str) -> str:
    """Construye un prompt visual cinematografico para una escena historica."""

    sentence_lower = sentence.lower()
    subject_lower = subject.lower()
    contenido = f"{subject_lower} {sentence_lower}"

    prompt = (
        "Escena historica cinematografica relacionada con "
        f"{subject}. "
        f"Representacion visual de: {sentence}. "
        "Realismo historico y cinematografico, iluminacion natural, "
        "composicion de pelicula historica, profundidad de campo, "
        "texturas realistas y atmosfera epica pero creible. "
        "Personajes con apariencia, vestimenta y objetos coherentes "
        "con la epoca historica representada. "
        "Arquitectura, paisaje, herramientas y materiales historicamente "
        "coherentes. "
    )

    # Nacimiento, infancia o Rea Silvia.
    if (
        "gemelos" in contenido
        or "nacimiento" in contenido
        or "nacieron" in contenido
        or "rea silvia" in contenido
    ):
        prompt += (
            "Mostrar a los hermanos gemelos como recien nacidos. "
            "Representar la tradicion legendaria de manera sobria y realista. "
            "Evitar elementos religiosos modernos o fantasia excesiva."
        )

    # Rio Tiber y abandono.
    elif (
        "tiber" in contenido
        or "tíber" in contenido
        or "rio" in contenido
        or "río" in contenido
        or "abandonados" in contenido
    ):
        prompt += (
            "Mostrar las orillas del antiguo rio Tiber, vegetacion mediterranea "
            "y terreno natural de la Italia antigua. "
            "Los elementos principales deben quedar claramente visibles."
        )

    # Loba.
    elif "loba" in contenido or "amamant" in contenido:
        prompt += (
            "Mostrar una loba junto al Tiber protegiendo y amamantando "
            "a los dos gemelos. "
            "La loba debe tener apariencia animal realista y no antropomorfica. "
            "La escena debe parecer una recreacion cinematografica "
            "de una antigua leyenda."
        )

    # Pastor y esposa.
    elif (
        "pastor" in contenido
        or "esposa" in contenido
        or "criados" in contenido
    ):
        prompt += (
            "Mostrar un entorno rural de la Italia antigua con un pastor "
            "y su esposa cuidando a los hermanos. "
            "Incluir una vivienda sencilla, animales domesticos, "
            "herramientas rurales y materiales propios de la epoca."
        )

    # Hermanos adultos y fundacion.
    elif (
        "crecieron" in contenido
        or "hermanos" in contenido
        or "fundar" in contenido
        or "ciudad" in contenido
    ):
        prompt += (
            "Mostrar a Romulo y Remo como jovenes adultos, fuertes y vestidos "
            "como hombres de la Italia antigua. "
            "Paisaje de colinas y valle cercano al Tiber, "
            "con indicios de un asentamiento primitivo."
        )

    # Conflicto entre Romulo y Remo.
    if (
        "disputa" in contenido
        or "conflicto" in contenido
        or "pelea" in contenido
        or "matar" in contenido
        or "muerte" in contenido
    ):
        prompt += (
            "Si la escena representa el conflicto entre los hermanos, "
            "mostrar tension dramatica sin gore ni violencia grafica. "
            "Utilizar expresiones faciales, postura corporal y composicion "
            "cinematografica para transmitir el conflicto."
        )

    # Fundacion de Roma.
    if (
        "roma" in contenido
        or "fundacion" in contenido
        or "fundar una ciudad" in contenido
    ):
        prompt += (
            "Mostrar un asentamiento primitivo sobre una colina del Lacio, "
            "con construcciones sencillas de madera, barro y piedra. "
            "Paisaje natural y ausencia de arquitectura imperial posterior. "
            "No representar el Coliseo ni edificios de la Roma imperial."
        )

    # Restricciones generales para IA.
    prompt += (
        " No incluir elementos modernos, edificios modernos, vehiculos, "
        "ropa moderna, armas modernas, electricidad, carreteras modernas, "
        "texto, subtitulos, logotipos ni marcas de agua. "
        "No introducir personajes o acontecimientos que contradigan "
        "la narracion proporcionada. "
        "La imagen debe representar claramente la accion principal "
        "de la escena y utilizar una composicion panoramica 16:9."
    )

    return prompt


def crear_plan_video(
    subject: str,
    title: str,
    narration: str,
    source_notes: list[str] | None = None,
    target_duration_seconds: int = 120,
) -> HistoricalVideoPlan:
    """Crea un plan determinista de escenas a partir de una narracion."""

    if not subject.strip():
        raise ValueError("El tema historico no puede estar vacio")

    if not title.strip():
        raise ValueError("El titulo no puede estar vacio")

    if not narration.strip():
        raise ValueError("La narracion no puede estar vacia")

    sentences = _split_sentences(narration)

    if not sentences:
        raise ValueError("No se encontraron escenas en la narracion")

    notes = list(source_notes or [])
    scenes = []

    for index, sentence in enumerate(sentences, start=1):
        scene_title = f"Escena {index}"

        visual_prompt = _crear_visual_prompt(
            sentence=sentence,
            subject=subject,
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