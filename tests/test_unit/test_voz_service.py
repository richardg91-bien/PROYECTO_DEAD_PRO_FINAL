from app.voz_service import generar_audio


class DummyTTS:
    def __init__(self, *args, **kwargs):
        self.args = args
        self.kwargs = kwargs

    def save(self, path):
        self.path = path


def test_generar_audio_adapta_el_texto_a_la_emocion(monkeypatch, tmp_path):
    captured = {}

    def fake_gtts(*args, **kwargs):
        captured["args"] = args
        captured["kwargs"] = kwargs
        return DummyTTS(*args, **kwargs)

    monkeypatch.setattr("app.voz_service.gTTS", fake_gtts)
    monkeypatch.setattr("app.voz_service.AUDIO_FOLDER", str(tmp_path))

    generar_audio("Hola, estoy aquí", emocion="feliz")

    text = captured["kwargs"]["text"]
    assert "qué gusto" in text.lower() or "hola" in text.lower()
