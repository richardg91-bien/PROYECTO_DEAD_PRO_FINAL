from app.historical_video.models import HistoricalScene
from app.historical_video.voice_pipeline import generar_audio_escena


def test_generar_audio_escena_reutiliza_piper(monkeypatch):
    calls = {}

    def fake_sintetizar(texto, emocion):
        calls["texto"] = texto
        calls["emocion"] = emocion
        return "/static/audio/scene_001.wav"

    monkeypatch.setattr(
        "app.historical_video.voice_pipeline.sintetizar_voz",
        fake_sintetizar,
    )

    scene = HistoricalScene(
        id="scene_001",
        title="Escena 1",
        narration="Roma crecio junto al Tiber.",
        visual_prompt="Roma antigua junto al Tiber.",
        emotion="neutral",
    )

    result = generar_audio_escena(scene)

    assert result == "/static/audio/scene_001.wav"
    assert calls == {
        "texto": "Roma crecio junto al Tiber.",
        "emocion": "neutral",
    }
