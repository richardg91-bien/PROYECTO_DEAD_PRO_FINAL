from pathlib import Path
from unittest.mock import patch

from app.historical_video.assembler import ensamblar_video
from app.historical_video.models import HistoricalScene, HistoricalVideoPlan


def test_ensamblar_video_genera_escenas_y_concatena(tmp_path):
    scenes = [
        HistoricalScene(
            id="s1",
            title="Uno",
            narration="Primera escena",
            visual_prompt="Escena histórica de apertura.",
        ),
        HistoricalScene(
            id="s2",
            title="Dos",
            narration="Segunda escena",
            visual_prompt="Segunda escena histórica.",
        ),
    ]
    plan = HistoricalVideoPlan(title="Prueba", subject="Evento", scenes=scenes)
    visuals = [tmp_path / "one.jpg", tmp_path / "two.jpg"]
    for visual in visuals:
        visual.write_bytes(b"image")

    audio_dir = tmp_path / "static" / "audio"
    audio_dir.mkdir(parents=True)
    audio_one = audio_dir / "one.wav"
    audio_two = audio_dir / "two.wav"
    audio_one.write_bytes(b"wav")
    audio_two.write_bytes(b"wav")

    output = tmp_path / "final.mp4"

    def fake_voice(scene):
        return f"/static/audio/{'one' if scene.id == 's1' else 'two'}.wav"

    def fake_audio_resolver(audio_url):
        return audio_one if audio_url.endswith("one.wav") else audio_two

    def fake_render(audio_path, output_path, image_path):
        Path(output_path).write_bytes(b"mp4")

    def fake_ffmpeg(command, **kwargs):
        Path(command[-1]).write_bytes(b"final-mp4")

    with patch("app.historical_video.assembler.generar_audio_escena", side_effect=fake_voice), patch(
        "app.historical_video.assembler.resolver_audio_local", side_effect=fake_audio_resolver
    ), patch("app.historical_video.assembler.render_scene", side_effect=fake_render), patch(
        "app.historical_video.assembler.subprocess.run", side_effect=fake_ffmpeg
    ):
        result = ensamblar_video(plan, visuals, output, ffmpeg_binary="ffmpeg")

    assert result == str(output)
    assert output.is_file()
    assert output.stat().st_size > 0
    assert len(list((tmp_path / "final_scenes").glob("scene_*.mp4"))) == 2
    concat = tmp_path / "final_scenes" / "concat.txt"
    assert concat.is_file()
    assert concat.read_text(encoding="utf-8").count("file '") == 2
