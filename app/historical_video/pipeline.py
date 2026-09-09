"""Pipeline de produccion de videos historicos de extremo a extremo.

Orquesta la capa visual, la voz Piper existente y el ensamblador FFmpeg sin
modificar los servicios canonicos de Vision 1.
"""

from pathlib import Path

from .assembler import ensamblar_video
from .visual import generar_visuales_plan


def producir_video_historico(
    plan,
    output_path: str | Path,
    visual_output_dir: str | Path = "static/historical_visuals",
    visual_generator=generar_visuales_plan,
    assembler=ensamblar_video,
) -> str:
    """Produce un video completo a partir de un ``HistoricalVideoPlan``.

    Primero materializa exactamente un visual por escena y luego delega en el
    ensamblador existente, que sintetiza Piper, renderiza cada escena y concatena
    los MP4. Las dependencias se pueden inyectar para pruebas o futuros
    proveedores visuales.
    """
    if not plan.scenes:
        raise ValueError("El plan historico debe contener al menos una escena")

    output = Path(output_path)
    output.parent.mkdir(parents=True, exist_ok=True)

    visual_paths = visual_generator(plan, output_dir=visual_output_dir)
    if len(visual_paths) != len(plan.scenes):
        raise ValueError("El proveedor visual debe generar una imagen por escena")

    for visual_path in visual_paths:
        if not Path(visual_path).is_file():
            raise FileNotFoundError(f"Visual de escena no encontrado: {visual_path}")

    return assembler(
        plan=plan,
        visual_paths=visual_paths,
        output_path=output,
    )
