"""
Tests para la función detectar_emocion()
"""
import pytest
from app.routes import detectar_emocion


class TestDetectarEmocion:
    """Suite de tests para detectar_emocion"""

    def test_detectar_emocion_sad(self):
        """Debe retornar 'triste' para palabras de tristeza"""
        assert detectar_emocion("triste") == "triste"
        assert detectar_emocion("llorar") == "triste"
        assert detectar_emocion("dolor") == "triste"

    def test_detectar_emocion_happy(self):
        """Debe retornar 'feliz' para palabras de alegría"""
        assert detectar_emocion("Estoy feliz") == "feliz"
        assert detectar_emocion("Muy alegre hoy") == "feliz"
        assert detectar_emocion("Me siento contento") == "feliz"

    def test_detectar_emocion_angry(self):
        """Debe retornar 'enojado' para palabras de enojo"""
        assert detectar_emocion("Estoy enojado") == "enojado"
        assert detectar_emocion("Tengo mucha bronca") == "enojado"
        assert detectar_emocion("Te odio") == "enojado"

    def test_detectar_emocion_neutral(self):
        """Debe retornar 'neutral' para textos sin emoción"""
        assert detectar_emocion("Hola") == "neutral"
        assert detectar_emocion("Qué tal") == "neutral"
        assert detectar_emocion("El agua es azul") == "neutral"
        assert detectar_emocion("") == "neutral"

    def test_detectar_emocion_case_insensitive(self):
        """Debe detectar emociones sin importar mayúsculas"""
        assert detectar_emocion("TRISTE") == "triste"
        assert detectar_emocion("FELIZ") == "feliz"
        assert detectar_emocion("ENOJADO") == "enojado"
        assert detectar_emocion("TrIsTE") == "triste"

    def test_detectar_emocion_mixed_emotions(self):
        """Cuando hay múltiples emociones, retorna la primera detectada (basada en orden en listas)"""
        # 'triste' aparece en la lista antes que 'feliz'
        resultado = detectar_emocion("llorar de alegría")
        # Como "llorar" está en triste y "alegre" está en feliz, retorna triste
        assert resultado == "triste"

    def test_detectar_emocion_partial_match(self):
        """Debe detectar palabras dentro de textos más largos"""
        assert detectar_emocion("La película fue triste") == "triste"
        assert detectar_emocion("Me siento muy feliz hoy") == "feliz"
        assert detectar_emocion("Estoy enojado con todo") == "enojado"

    def test_detectar_emocion_all_keywords(self):
        """Debe reconocer todos los keywords de cada emoción"""
        # Tristeza
        assert detectar_emocion("triste") == "triste"
        assert detectar_emocion("llorar") == "triste"
        assert detectar_emocion("extraño") == "triste"
        assert detectar_emocion("dolor") == "triste"

        # Felicidad
        assert detectar_emocion("feliz") == "feliz"
        assert detectar_emocion("alegre") == "feliz"
        assert detectar_emocion("contento") == "feliz"

        # Enojo
        assert detectar_emocion("enojado") == "enojado"
        assert detectar_emocion("bronca") == "enojado"
        assert detectar_emocion("odio") == "enojado"
