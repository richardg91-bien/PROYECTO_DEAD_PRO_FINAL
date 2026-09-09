"""Adaptador del servicio Piper existente para escenas de video historico."""

from app.voice.voice_service import sintetizar_voz


def generar_audio_escena(scene):
    """Genera el WAV de una escena usando el Piper canonico de Vision 1."""
    return sintetizar_voz(scene.narration, scene.emotion)
