"""Orquestacion de escenas y ensamblado final de un video historico."""

from pathlib import Path
import subprocess

from .render import render_scene
from .voice_pipeline import generar_audio_escena


def ensamblar_video(plan, visual_paths, output_path, ffmpeg_binary="ffmpeg"):
    """Genera cada escena y concatena los MP4 en el orden del plan.

    ``visual_paths`` debe contener exactamente una imagen por escena.
    """
    if len(visual_paths) != len(plan.scenes):
        raise ValueError("Debe existir una imagen por cada escena")

    output = Path(output_path)
    output.parent.mkdir(parents=True, exist_ok=True)
    scene_dir = output.parent / f"{output.stem}_scenes"
    scene_dir.mkdir(parents=True, exist_ok=True)

    scene_files = []
    for index, (scene, visual_path) in enumerate(zip(plan.scenes, visual_paths), start=1):
        audio_url = generar_audio_escena(scene)
        if not audio_url:
            raise RuntimeError(f"Piper no genero audio para la escena {scene.id}")

        audio_path = Path(audio_url.lstrip("/").replace("/", str(Path.sep)))
        if not audio_path.is_file():
            raise FileNotFoundError(f"Audio no encontrado: {audio_path}")

        scene_output = scene_dir / f"scene_{index:03d}.mp4"
        render_scene(
            visual_path=visual_path,
            audio_path=audio_path,
            output_path=scene_output,
            ffmpeg_binary=ffmpeg_binary,
        )
        scene_files.append(scene_output)

    concat_file = scene_dir / "concat.txt"
    concat_file.write_text(
        "".join(f"file '{path.resolve().as_posix()}'\n" for path in scene_files),
        encoding="utf-8",
    )

    command = [
        ffmpeg_binary,
        "-y",
        "-f", "concat",
        "-safe", "0",
        "-i", str(concat_file),
        "-c", "copy",
        str(output),
    ]
    subprocess.run(command, check=True, capture_output=True, text=True)
    return str(output)
