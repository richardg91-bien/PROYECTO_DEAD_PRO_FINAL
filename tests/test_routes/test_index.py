"""
Tests para rutas GET simples - solo verifican que retornen 200
"""
import pytest
from unittest.mock import patch


class TestRoutesGet:
    """Tests para rutas GET"""

    @patch('app.routes.render_template')
    def test_index_route(self, mock_render, client):
        """GET / debe retornar 200"""
        mock_render.return_value = "OK"
        response = client.get('/')
        assert response.status_code == 200

    @patch('app.routes.render_template')
    def test_upload_get_route(self, mock_render, client):
        """GET /upload debe retornar 200"""
        mock_render.return_value = "OK"
        response = client.get('/upload')
        assert response.status_code == 200

    @patch('app.routes.render_template')
    def test_chat_get_route(self, mock_render, client):
        """GET /chat debe retornar 200"""
        mock_render.return_value = "OK"
        response = client.get('/chat')
        assert response.status_code == 200

    @patch('app.routes.render_template')
    def test_buscar_ia_get_route(self, mock_render, client):
        """GET /buscar_ia debe retornar 200"""
        mock_render.return_value = "OK"
        response = client.get('/buscar_ia')
        assert response.status_code == 200

    @patch('app.routes.render_template')
    def test_chat_persona_get_route(self, mock_render, client):
        """GET /chat_persona/<nombre> debe retornar 200"""
        mock_render.return_value = "OK"
        response = client.get('/chat_persona/Juan')
        assert response.status_code == 200

    @patch('app.routes.render_template')
    def test_galeria_get_route(self, mock_render, client):
        """GET /galeria debe retornar 200"""
        mock_render.return_value = "OK"
        response = client.get('/galeria')
        assert response.status_code == 200
        # Verificar que render_template fue llamado
        mock_render.assert_called_once()

    @patch('app.routes.render_template')
    def test_experiencia_get_route_found(self, mock_render, client, sample_experience):
        """GET /experiencia/<id> con ID válido debe retornar 200"""
        mock_render.return_value = "OK"
        response = client.get(f'/experiencia/{sample_experience}')
        assert response.status_code == 200

    @patch('app.routes.render_template')
    def test_experiencia_get_route_not_found(self, mock_render, client):
        """GET /experiencia/<id> con ID inválido retorna error"""
        response = client.get('/experiencia/invalid-id')
        assert response.status_code == 200
        assert b'no encontrada' in response.data

    @patch('app.routes.render_template')
    def test_admin_route(self, mock_render, client):
        """GET /admin debe retornar 200"""
        mock_render.return_value = "OK"
        response = client.get('/admin')
        assert response.status_code == 200
