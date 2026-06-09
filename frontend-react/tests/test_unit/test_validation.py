"""Tests para servicios de validación"""

import pytest
from app.services.validation import (
    validar_archivo_imagen,
    validar_form_upload,
    validar_mensaje_chat
)


class TestValidarFormUpload:
    """Tests para validación de formulario de upload"""

    def test_valida_form_correcto(self):
        """Valida formulario con datos correctos"""
        valido, error = validar_form_upload("Juan", "Mi recuerdo", "Esta es una descripción muy bonita y larga")
        assert valido is True
        assert error is None

    def test_rechaza_persona_vacia(self):
        """Rechaza nombre de persona vacío"""
        valido, error = validar_form_upload("", "Título", "Descripción")
        assert valido is False
        assert "campos requeridos" in error.lower()

    def test_rechaza_persona_muy_corta(self):
        """Rechaza nombre de persona muy corto"""
        valido, error = validar_form_upload("J", "Título", "Descripción larga")
        assert valido is False
        assert "entre 2" in error.lower()

    def test_rechaza_persona_muy_larga(self):
        """Rechaza nombre de persona muy largo"""
        valido, error = validar_form_upload("J" * 101, "Título", "Descripción larga")
        assert valido is False
        assert "100" in error

    def test_rechaza_titulo_muy_corto(self):
        """Rechaza título muy corto"""
        valido, error = validar_form_upload("Juan", "ab", "Descripción larga")
        assert valido is False
        assert "título" in error.lower()

    def test_rechaza_descripcion_muy_corta(self):
        """Rechaza descripción muy corta"""
        valido, error = validar_form_upload("Juan", "Título", "Desc")
        assert valido is False
        assert "descripción" in error.lower()


class TestValidarMensajeChat:
    """Tests para validación de mensajes de chat"""

    def test_valida_mensaje_correcto(self):
        """Valida mensaje correcto"""
        valido, error = validar_mensaje_chat("Hola, ¿cómo estás?")
        assert valido is True
        assert error is None

    def test_rechaza_mensaje_vacio(self):
        """Rechaza mensaje vacío"""
        valido, error = validar_mensaje_chat("")
        assert valido is False

    def test_rechaza_mensaje_none(self):
        """Rechaza mensaje None"""
        valido, error = validar_mensaje_chat(None)
        assert valido is False

    def test_rechaza_mensaje_muy_largo(self):
        """Rechaza mensaje muy largo"""
        valido, error = validar_mensaje_chat("x" * 5001)
        assert valido is False
        assert "5000" in error
