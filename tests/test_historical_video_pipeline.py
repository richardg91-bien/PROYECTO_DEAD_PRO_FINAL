from pathlib import Path

from app.historical_video.models import HistoricalScene, HistoricalVideoPlan
from app.historical_video.pipeline import producir_video_historico


def test_producir_video_historico_orquesta_visual_y_ensamblador(tmp_path):
    scene = HistoricalScene(
        id="scene-1",
        title="Fundación de Roma",
        narration="Rómulo funda Roma según la tradición.",
        visual_prompt="Roma arcaica, reconstrucción histórica.",
    )
    plan = HistoricalVideoPlan(
        title="Rómulo y Remo",
        subject="Rómulo y Remo",
        scenes=[scene],
    )

    visual = tmp_path / "scene.png"
    visual.write_bytes(b"png")
    calls = {}

    def fake_visual_generator(received_plan, output_dir):
        calls["visual_plan"] = received_plan
        calls["visual_output_dir"] = output_dir
        return [str(visual)]

    def fake_assembler(plan, visual_paths, output_path):
        calls["assembler_plan"] = plan
        calls["visual_paths"] = visual_paths
        calls["output_path"] = output_path
        return str(output_path)

    output = tmp_path / "historia.mp4"
    result = producir_video_historico(
        plan,
        output,
        visual_output_dir=tmp_path / "visuals",
        visual_generator=fake_visual_generator,
        assembler=fake_assembler,
    )

    assert result == str(output)
    assert calls["visual_plan"] is plan
    assert calls["visual_output_dir"] == tmp_path / "visuals"
    assert calls["assembler_plan"] is plan
    assert calls["visual_paths"] == [str(visual)]
    assert calls["output_path"] == output
