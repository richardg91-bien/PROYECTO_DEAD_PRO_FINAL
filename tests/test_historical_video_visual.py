from app.historical_video.models import HistoricalScene, HistoricalVideoPlan
from app.historical_video.visual import generar_visual_escena, generar_visuales_plan


def _scene(scene_id):
    return HistoricalScene(
        id=scene_id,
        title="Escena",
        narration="Una escena histórica.",
        visual_prompt="Arquitectura y vestuario de época.",
    )


def test_generar_visual_escena(tmp_path):
    path = generar_visual_escena(_scene("scene_001"), output_dir=tmp_path)
    assert path.endswith(".png")
    assert tmp_path.joinpath(path.split("/")[-1]).is_file() or __import__("pathlib").Path(path).is_file()


def test_generar_visuales_plan_preserves_order(tmp_path):
    plan = HistoricalVideoPlan(title="Demo", subject="Roma", scenes=[_scene("scene_001"), _scene("scene_002")])
    paths = generar_visuales_plan(plan, output_dir=tmp_path)
    assert len(paths) == 2
    assert "scene_001" in paths[0]
    assert "scene_002" in paths[1]
