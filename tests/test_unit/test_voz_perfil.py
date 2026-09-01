"""Tests del perfil y servicio de voz (diseño: calma, elegancia, confianza)."""

from types import SimpleNamespace

from app.voz_perfil import (
    VOICE_SETTINGS,
    ajustes_por_afinidad,
    matiz_textual_por_afinidad,
    suavizar_prosodia,
)
from app.voz_service import adaptar_texto_a_voz, generar_audio


class TestPerfilVoz:
    def test_ajustes_calmados(self):
        """Stability alta, estilo bajo, velocidad lenta-media."""
        assert VOICE_SETTINGS["stability"] >= 0.70
        assert VOICE_SETTINGS["stability"] <= 0.85
        assert VOICE_SETTINGS["style"] <= 0.2
        assert 0.85 <= VOICE_SETTINGS["speed"] <= 0.95

    def test_quita_energia_agresiva(self):
        """Las exclamaciones se convierten en frases llanas."""
        resultado = suavizar_prosodia("¡Hola! ¡Qué gusto verte!")
        assert "!" not in resultado
        assert "¡" not in resultado

    def test_final_suave(self):
        assert suavizar_prosodia("¿cómo estás?").endswith(".")

    def test_pausa_tras_saludo(self):
        resultado = suavizar_prosodia("Hola, te estaba esperando")
        assert "Hola…" in resultado


class TestAdaptarTextoAVoz:
    def test_mantiene_emocion_y_suaviza(self):
        texto = adaptar_texto_a_voz("¡Estoy feliz!", emocion="feliz")
        assert "qué gusto" in texto
        assert "!" not in texto

    def test_texto_vacio(self):
        assert adaptar_texto_a_voz("") == ""


class TestVozAdaptativa:
    def test_afinidad_baja_mas_contenida(self):
        ajustes, matiz = ajustes_por_afinidad(0.1)
        assert matiz == "contenida"
        assert ajustes["stability"] > VOICE_SETTINGS["stability"]
        assert ajustes["style"] < VOICE_SETTINGS["style"]

    def test_afinidad_alta_mas_calida(self):
        ajustes, matiz = ajustes_por_afinidad(0.8)
        assert matiz == "cálida"
        assert ajustes["stability"] < VOICE_SETTINGS["stability"]
        assert ajustes["style"] > VOICE_SETTINGS["style"]

    def test_afinidad_media_mantiene_diseno_base(self):
        ajustes, matiz = ajustes_por_afinidad(0.45)
        assert matiz == "neutral"
        assert ajustes == VOICE_SETTINGS

    def test_sin_afinidad_mantiene_base(self):
        ajustes, _ = ajustes_por_afinidad(None)
        assert ajustes == VOICE_SETTINGS

    def test_matiz_textual_por_vinculo(self):
        assert "placer" in matiz_textual_por_afinidad(0.8)
        assert "gusto conocerte" in matiz_textual_por_afinidad(0.1)
        assert matiz_textual_por_afinidad(0.45) == ""

    def test_texto_incluye_matiz_de_vinculo(self):
        texto = adaptar_texto_a_voz("Hola", afinidad=0.9)
        assert "conversar contigo" in texto

    def test_elevenlabs_recibe_ajustes_ajustados(self, monkeypatch, tmp_path):
        """Con afinidad alta, ElevenLabs recibe la voz más cálida."""
        captured = {}

        def fake_post(url, headers=None, json=None, timeout=None):
            captured["json"] = json
            return SimpleNamespace(status_code=200, content=b"x")

        monkeypatch.setenv("ELEVENLABS_API_KEY", "test-key")
        monkeypatch.setattr("app.voz_service.requests.post", fake_post)
        monkeypatch.setattr("app.voz_service.AUDIO_FOLDER", str(tmp_path))

        generar_audio("Hola", afinidad=0.9)

        settings = captured["json"]["voice_settings"]
        assert settings["stability"] == 0.72  # cálida, no la base 0.80


class TestGenerarAudio:
    def test_fallback_gtts_sin_clave(self, monkeypatch, tmp_path):
        """Sin ELEVENLABS_API_KEY usa gTTS local."""
        captured = {}

        class DummyTTS:
            def __init__(self, *a, **kw):
                captured["kwargs"] = kw

            def save(self, path):
                captured["path"] = path

        monkeypatch.delenv("ELEVENLABS_API_KEY", raising=False)
        monkeypatch.setattr("app.voz_service.gTTS", DummyTTS)
        monkeypatch.setattr("app.voz_service.AUDIO_FOLDER", str(tmp_path))

        nombre = generar_audio("Hola, estoy aquí", emocion="feliz")

        assert nombre and nombre.endswith(".mp3")
        assert "qué gusto" in captured["kwargs"]["text"]
        assert "!" not in captured["kwargs"]["text"]

    def test_usa_elevenlabs_con_clave(self, monkeypatch, tmp_path):
        """Con clave, llama a ElevenLabs con los ajustes del diseño de voz."""
        captured = {}

        def fake_post(url, headers=None, json=None, timeout=None):
            captured["url"] = url
            captured["headers"] = headers
            captured["json"] = json
            return SimpleNamespace(status_code=200, content=b"audio-bytes")

        monkeypatch.setenv("ELEVENLABS_API_KEY", "test-key")
        monkeypatch.setattr("app.voz_service.requests.post", fake_post)
        monkeypatch.setattr("app.voz_service.AUDIO_FOLDER", str(tmp_path))

        from app.voz_perfil import MODEL_ID, VOICE_SETTINGS

        nombre = generar_audio("Te escucho con calma")

        assert nombre and nombre.endswith(".mp3")
        assert "text-to-speech" in captured["url"]
        assert captured["headers"]["xi-api-key"] == "test-key"
        assert captured["json"]["model_id"] == MODEL_ID
        assert captured["json"]["voice_settings"] == VOICE_SETTINGS
        assert (tmp_path / nombre).read_bytes() == b"audio-bytes"

    def test_elevenlabs_fallando_cae_a_gtts(self, monkeypatch, tmp_path):
        """Si ElevenLabs falla, se degrada a gTTS sin romper la app."""

        def fake_post(*a, **kw):
            return SimpleNamespace(status_code=500, text="error")

        class DummyTTS:
            def __init__(self, *a, **kw):
                pass

            def save(self, path):
                open(path, "wb").close()

        monkeypatch.setenv("ELEVENLABS_API_KEY", "test-key")
        monkeypatch.setattr("app.voz_service.requests.post", fake_post)
        monkeypatch.setattr("app.voz_service.gTTS", DummyTTS)
        monkeypatch.setattr("app.voz_service.AUDIO_FOLDER", str(tmp_path))

        nombre = generar_audio("Hola")
        assert nombre and nombre.endswith(".mp3")

    def test_texto_vacio_devuelve_none(self):
        assert generar_audio("") is None
