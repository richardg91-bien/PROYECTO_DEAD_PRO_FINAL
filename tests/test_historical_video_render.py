import wave

from app.historical_video.render import duracion_wav


def test_duracion_wav(tmp_path):
    audio = tmp_path / "scene.wav"
    with wave.open(str(audio), "wb") as wav:
        wav.setnchannels(1)
        wav.setsampwidth(2)
        wav.setframerate(16000)
        wav.writeframes(b"\x00\x00" * 16000 * 2)

    assert duracion_wav(audio) == 2.0
