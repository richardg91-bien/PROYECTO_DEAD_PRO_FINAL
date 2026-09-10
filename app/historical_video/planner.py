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

    # ------------------------------------------------------------------
    # DIRECCION ARTISTICA BASE
    # ------------------------------------------------------------------
    #
    # Importante:
    # Evitamos utilizar "Roma antigua" como elemento visual principal,
    # porque modelos como SD 1.5 tienden a asociarlo con Coliseo,
    # ruinas monumentales, legionarios y arquitectura imperial.
    #
    # En su lugar describimos directamente:
    # - Lacio rural
    # - siglo VIII a.C.
    # - comunidad italica primitiva
    # - personas reales
    # - naturaleza
    # - construcciones sencillas
    #
    prompt = (
        "Photorealistic cinematic historical scene set in rural Latium, "
        "central Italy, approximately 800 BCE, during the early Iron Age. "
        "Show real living human beings with natural human faces, realistic "
        "skin, realistic hair, realistic anatomy and natural body proportions. "
        "The environment is a small, poor and undeveloped Italic rural community "
        "surrounded by wild vegetation, wooded hills, grassland and natural terrain. "
        "Primitive huts made from wooden branches, mud, reeds and thatch may appear "
        "in the background. "
        "People wear simple rough wool tunics, leather belts and simple leather "
        "sandals appropriate for an early Italic community. "
        "Primitive bronze or iron-age tools and simple weapons only when required "
        "by the narration. "
        "Natural sunlight, realistic atmospheric perspective, cinematic framing, "
        "documentary photography, realistic textures, natural colors, believable "
        "historical environment, dramatic but realistic lighting, shallow depth "
        "of field when appropriate, widescreen cinematic composition, 16:9. "
        f"Main historical subject: {subject}. "
        f"Visual action represented: {sentence}. "
    )

    # ------------------------------------------------------------------
    # NACIMIENTO / INFANCIA / REA SILVIA
    # ------------------------------------------------------------------
    if (
        "gemelos" in contenido
        or "nacimiento" in contenido
        or "nacieron" in contenido
        or "rea silvia" in contenido
    ):
        prompt += (
            "If the narration concerns the birth or infancy of the twins, "
            "show newborn human babies in a humble ancient Italic setting. "
            "Use realistic human proportions and natural skin. "
            "The scene must feel like a serious historical drama rather than "
            "a fantasy illustration. "
            "Use simple woven cloth and primitive natural materials. "
        )

    # ------------------------------------------------------------------
    # RIO TIBER / ABANDONO
    # ------------------------------------------------------------------
    elif (
        "tiber" in contenido
        or "tíber" in contenido
        or "rio" in contenido
        or "río" in contenido
        or "abandonados" in contenido
    ):
        prompt += (
            "Show a completely natural ancient river landscape. "
            "The Tiber is represented as a wild river surrounded by reeds, "
            "mud, grasses, trees and undeveloped riverbanks. "
            "No city is visible. No monumental architecture is visible. "
            "The landscape must look ancient, rural and untouched. "
        )

    # ------------------------------------------------------------------
    # LOBA
    # ------------------------------------------------------------------
    elif "loba" in contenido or "amamant" in contenido:
        prompt += (
            "Show a real adult she-wolf with anatomically correct natural animal "
            "features protecting the two newborn human twins near the river. "
            "The wolf must look like a real wild animal, not a statue, sculpture, "
            "mythological creature or fantasy animal. "
            "The babies must look like real human infants. "
            "Use a restrained cinematic interpretation of the legendary episode. "
        )

    # ------------------------------------------------------------------
    # PASTOR / ESPOSA / CRIANZA
    # ------------------------------------------------------------------
    elif (
        "pastor" in contenido
        or "esposa" in contenido
        or "criados" in contenido
        or "criados por" in contenido
    ):
        prompt += (
            "Show a poor rural Italic shepherd family caring for the children. "
            "Include a simple primitive hut made from wood, mud, reeds and thatch, "
            "domestic animals, sheep, simple wooden tools and natural materials. "
            "The people should look like ordinary rural inhabitants of the period, "
            "not soldiers, nobles or imperial Romans. "
        )

    # ------------------------------------------------------------------
    # ROMULO Y REMO ADULTOS / CRECIMIENTO
    # ------------------------------------------------------------------
    elif (
        "crecieron" in contenido
        or "hermanos" in contenido
        or "fundar" in contenido
        or "ciudad" in contenido
    ):
        prompt += (
            "Show Romulus and Remus as two real young adult twin brothers. "
            "They should have similar facial characteristics while remaining "
            "clearly recognizable as two different living human individuals. "
            "They are strong rural young men from an early Italic community. "
            "They wear simple rough wool tunics, leather belts and leather sandals. "
            "Their clothing is practical and primitive, without military uniforms "
            "or imperial Roman equipment. "
            "Place them primarily in a natural landscape of wooded hills, grass, "
            "river valley and primitive huts. "
            "Keep the visual focus on the two brothers rather than architecture. "
        )

    # ------------------------------------------------------------------
    # CONFLICTO ENTRE LOS HERMANOS
    # ------------------------------------------------------------------
    if (
        "disputa" in contenido
        or "conflicto" in contenido
        or "pelea" in contenido
        or "matar" in contenido
        or "muerte" in contenido
    ):
        prompt += (
            "If the scene represents conflict between the brothers, show dramatic "
            "tension through facial expressions, body language, distance between "
            "the characters and cinematic composition. "
            "Do not show gore or graphic violence. "
            "Keep both brothers visually consistent and dressed as early Italic "
            "rural warriors rather than Roman imperial soldiers. "
        )

    # ------------------------------------------------------------------
    # FUNDACION / ASENTAMIENTO PRIMITIVO
    # ------------------------------------------------------------------
    if (
        "roma" in contenido
        or "fundacion" in contenido
        or "fundar una ciudad" in contenido
    ):
        prompt += (
            "If a settlement is required, show only a very small primitive "
            "hilltop settlement of early Italic people. "
            "Use wooden huts, mud walls, thatched roofs, rough uncut stones, "
            "dirt paths and simple wooden fences. "
            "The settlement must look like a small prehistoric or early Iron Age "
            "village, not a city. "
            "Do not show monumental architecture. "
            "The surrounding landscape must dominate the image. "
        )

    # ------------------------------------------------------------------
    # NEGATIVE PROMPT / RESTRICCIONES
    # ------------------------------------------------------------------
    #
    # Se incluyen en ingles porque el modelo SD 1.5 suele responder mejor
    # a este tipo de restricciones.
    #
    prompt += (
        "ABSOLUTELY AVOID: "
        "statue, sculpture, stone statue, marble statue, bronze statue, "
        "monument, bust, carved figure, museum artifact, classical sculpture, "
        "painting, drawing, illustration, fantasy art, CGI character, "
        "Colosseum, amphitheater, Roman forum, monumental temple, palace, "
        "marble columns, giant arches, monumental ruins, Roman ruins, "
        "imperial Roman architecture, Roman Empire, imperial Rome, "
        "Roman legionary, centurion, Roman legion, legion armor, "
        "lorica segmentata, imperial helmet, large legionary shield, "
        "Roman military uniform, gladiator, "
        "modern buildings, modern city, roads, electricity, vehicles, "
        "modern clothing, modern weapons, technology, "
        "text, letters, subtitles, logo, watermark. "
        "Do not introduce historical elements from later Roman periods. "
        "Do not transform the people into statues or sculptures. "
        "The subjects must be living real human beings. "
        "The image must focus on the main action described by the narration. "
        "Wide cinematic 16:9 composition."
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