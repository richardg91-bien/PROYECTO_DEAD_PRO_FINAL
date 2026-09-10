from app.historical_video.models import HistoricalScene
from app.historical_video.voice_pipeline import generar_audio_escena


def test_generar_audio_escena_delega_al_servicio_de_voz(monkeypatch):
    calls = {}

    def fake_generar_audio(texto):
        calls["texto"] = texto
        return "scene_001.mp3"

    monkeypatch.setattr(
        "app.historical_video.voice_pipeline.generar_audio",
        fake_generar_audio,
    )

    scene = HistoricalScene(
        id="scene_001",
        title="Escena 1",
        narration="Roma creció junto al Tíber.",
        visual_prompt="Roma antigua junto al Tíber.",
        emotion="neutral",
    )

    result = generar_audio_escena(scene)

    assert result == "/static/audio/scene_001.mp3"
    assert calls == {"texto": "Roma creció junto al Tíber."}
