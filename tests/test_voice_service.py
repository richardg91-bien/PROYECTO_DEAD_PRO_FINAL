"""Pruebas del servicio Piper de Visión 1."""

from pathlib import Path
from types import SimpleNamespace

from app.voice import voice_service


class FakeLogger:
    def info(self, *args, **kwargs):
        pass

    def warning(self, *args, **kwargs):
        pass


class FakeApp:
    root_path = "/tmp/project/app"
    logger = FakeLogger()


def test_voice_not_configured_returns_none(monkeypatch):
    monkeypatch.delenv("PIPER_MODEL", raising=False)
    monkeypatch.setattr(voice_service, "current_app", FakeApp())
    assert voice_service.sintetizar_voz("Hola", "neutral") is None


def test_voice_builds_emotional_piper_command(monkeypatch, tmp_path):
    calls = {}
    monkeypatch.setenv("PIPER_MODEL", "/models/persona.onnx")
    monkeypatch.setenv("PIPER_BINARY", "piper")
    monkeypatch.setenv("PIPER_OUTPUT_DIR", str(tmp_path))
    monkeypatch.setattr(voice_service, "current_app", FakeApp())

    def fake_run(command, **kwargs):
        calls["command"] = command
        calls["kwargs"] = kwargs
        output = Path(command[command.index("--output_file") + 1])
        output.write_bytes(b"RIFF-test")
        return SimpleNamespace(returncode=0)

    monkeypatch.setattr(voice_service.subprocess, "run", fake_run)
    result = voice_service.sintetizar_voz("Te extraño", "triste")

    assert result.startswith("/static/audio/persona_")
    assert result.endswith(".wav")
    command = calls["command"]
    assert command[0] == "piper"
    assert command[command.index("--model") + 1] == "/models/persona.onnx"
    assert command[command.index("--length_scale") + 1] == "1.12"
    assert calls["kwargs"]["input"] == "Te extraño"
    assert calls["kwargs"]["check"] is True
    assert calls["kwargs"]["timeout"] == 30
