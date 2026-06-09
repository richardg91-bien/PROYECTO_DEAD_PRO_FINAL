"""Tests para servicios de emociones"""

import pytest
from app.services.emotion_service import detectar_emocion


class TestDetectarEmocion:
    """Tests para detección de emociones"""

    def test_detecta_triste(self):
        """Detecta emoción triste correctamente"""
        assert detectar_emocion("Me siento muy triste") == "triste"
        assert detectar_emocion("Estoy llorando de dolor") == "triste"
        assert detectar_emocion("Te extraño mucho") == "triste"

    def test_detecta_feliz(self):
        """Detecta emoción feliz correctamente"""
        assert detectar_emocion("¡Estoy muy feliz!") == "feliz"
        assert detectar_emocion("Me siento alegre y contento") == "feliz"
        assert detectar_emocion("¡Qué día excelente!") == "feliz"

    def test_detecta_enojado(self):
        """Detecta emoción enojado correctamente"""
        assert detectar_emocion("Estoy muy enojado") == "enojado"
        assert detectar_emocion("¡Qué bronca!") == "enojado"
        assert detectar_emocion("Te odio mucho") == "enojado"

    def test_detecta_neutral(self):
        """Detecta emoción neutral por defecto"""
        assert detectar_emocion("Hola, ¿cómo estás?") == "neutral"
        assert detectar_emocion("El clima está nublado") == "neutral"
        assert detectar_emocion("") == "neutral"

    def test_case_insensitive(self):
        """Detecta emociones sin importar mayúsculas"""
        assert detectar_emocion("TRISTE") == "triste"
        assert detectar_emocion("FELIZ") == "feliz"
        assert detectar_emocion("ENOJADO") == "enojado"
