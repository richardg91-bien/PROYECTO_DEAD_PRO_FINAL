"""Tests de integración para rutas principales"""

import pytest
from unittest.mock import patch
from io import BytesIO


class TestUploadRoute:
    """Tests para ruta de upload"""

    def test_upload_get_devuelve_formulario(self, client):
        """GET /upload devuelve formulario"""
        response = client.get('/upload')
        assert response.status_code == 200
        assert b'Subir recuerdo' in response.data

    def test_upload_sin_archivo(self, client):
        """POST /upload sin archivo retorna error"""
        data = {
            'persona': 'Juan',
            'title': 'Test',
            'description': 'Descripción de prueba'
        }
        response = client.post('/upload', data=data, content_type='multipart/form-data')
        assert response.status_code == 400

    def test_upload_sin_persona(self, client):
        """POST /upload sin persona retorna error"""
        data = {
            'image': (BytesIO(b'fake image'), 'test.jpg'),
            'title': 'Test',
            'description': 'Descripción de prueba'
        }
        response = client.post('/upload', data=data, content_type='multipart/form-data')
        assert response.status_code == 400


class TestGaleriaRoute:
    """Tests para ruta de galería"""

    def test_galeria_get_devuelve_html(self, client):
        """GET /galeria devuelve página HTML"""
        response = client.get('/galeria')
        assert response.status_code == 200

    def test_galeria_contains_data(self, client):
        """GET /galeria contiene datos"""
        response = client.get('/galeria')
        assert response.status_code == 200


class TestChatRoute:
    """Tests para ruta de chat"""

    def test_chat_get_devuelve_formulario(self, client):
        """GET /chat devuelve formulario"""
        response = client.get('/chat')
        assert response.status_code == 200

    def test_chat_post_mensaje_vacio(self, client):
        """POST /chat con mensaje vacío retorna error"""
        data = {'message': ''}
        response = client.post('/chat', data=data)
        assert response.status_code == 400


class TestIndexRoute:
    """Tests para ruta principal"""

    def test_index_devuelve_html(self, client):
        """GET / devuelve página de inicio"""
        response = client.get('/')
        assert response.status_code == 200
        assert b'Proyecto Dead' in response.data
