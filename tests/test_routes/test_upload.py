"""
Tests para POST /upload
"""
import pytest
from unittest.mock import MagicMock, patch
from io import BytesIO
from app import get_db


class TestUploadPostRoute:
    """Tests para POST /upload"""

    @patch('app.routes.render_template')
    @patch('app.routes.qrcode.make')
    @patch('app.routes.generar_embedding')
    @patch('app.routes.current_app')
    def test_upload_missing_file(self, mock_app, mock_embedding, mock_qr, mock_render, client):
        """POST /upload sin archivo retorna error"""
        data = {
            'persona': 'Juan',
            'title': 'Test',
            'description': 'Test'
        }

        response = client.post('/upload', data=data, content_type='multipart/form-data')
        assert response.status_code == 200
        assert b'No imagen' in response.data

    @patch('app.routes.render_template')
    @patch('app.routes.qrcode.make')
    @patch('app.routes.generar_embedding')
    @patch('app.routes.current_app')
    def test_upload_missing_persona(self, mock_app, mock_embedding, mock_qr, mock_render, client):
        """POST /upload sin persona retorna error"""
        data = {
            'image': (BytesIO(b'fake image data'), 'test.jpg'),
            'title': 'Test',
            'description': 'Test'
        }

        response = client.post('/upload', data=data, content_type='multipart/form-data')
        assert response.status_code == 200
        assert b'Faltan datos' in response.data

    @patch('app.routes.render_template')
    @patch('app.routes.qrcode.make')
    @patch('app.routes.generar_embedding')
    @patch('app.routes.current_app')
    def test_upload_missing_title(self, mock_app, mock_embedding, mock_qr, mock_render, client):
        """POST /upload sin title retorna error"""
        data = {
            'image': (BytesIO(b'fake image data'), 'test.jpg'),
            'persona': 'Juan',
            'description': 'Test'
        }

        response = client.post('/upload', data=data, content_type='multipart/form-data')
        assert response.status_code == 200
        assert b'Faltan datos' in response.data

    @patch('app.routes.render_template')
    @patch('app.routes.qrcode.make')
    @patch('app.routes.generar_embedding')
    @patch('app.routes.current_app')
    def test_upload_missing_description(self, mock_app, mock_embedding, mock_qr, mock_render, client):
        """POST /upload sin description retorna error"""
        data = {
            'image': (BytesIO(b'fake image data'), 'test.jpg'),
            'persona': 'Juan',
            'title': 'Test'
        }

        response = client.post('/upload', data=data, content_type='multipart/form-data')
        assert response.status_code == 200
        assert b'Faltan datos' in response.data

    @patch('app.routes.render_template')
    @patch('app.routes.qrcode.make')
    @patch('app.routes.generar_embedding')
    @patch('app.routes.current_app')
    def test_upload_saves_to_database(self, mock_app, mock_embedding, mock_qr, mock_render, client, app_context):
        """POST /upload debe guardar en BD"""
        mock_qr.return_value.save = MagicMock()
        mock_embedding.return_value = [0.1, 0.2]
        mock_app.supabase.table.return_value.insert.return_value.execute.return_value = None

        data = {
            'image': (BytesIO(b'fake image data'), 'test.jpg'),
            'persona': 'María',
            'title': 'Mi Experiencia',
            'description': 'Una descripción'
        }

        response = client.post('/upload', data=data, content_type='multipart/form-data')
        assert response.status_code == 302  # Redirección a /galeria

        # Verificar que se guardó en BD
        db = get_db()
        experiences = db.execute("SELECT * FROM experiences WHERE persona=?", ('María',)).fetchall()
        db.close()

        assert len(experiences) > 0

    @patch('app.routes.render_template')
    @patch('app.routes.qrcode.make')
    @patch('app.routes.generar_embedding')
    @patch('app.routes.current_app')
    def test_upload_calls_generar_embedding(self, mock_app, mock_embedding, mock_qr, mock_render, client):
        """POST /upload debe llamar a generar_embedding"""
        mock_qr.return_value.save = MagicMock()
        mock_embedding.return_value = [0.1]
        mock_app.supabase.table.return_value.insert.return_value.execute.return_value = None

        data = {
            'image': (BytesIO(b'fake image data'), 'test.jpg'),
            'persona': 'Juan',
            'title': 'Test',
            'description': 'Test'
        }

        response = client.post('/upload', data=data, content_type='multipart/form-data')

        # Verificar que generar_embedding fue llamado
        mock_embedding.assert_called()

    @patch('app.routes.render_template')
    @patch('app.routes.qrcode.make')
    @patch('app.routes.generar_embedding')
    @patch('app.routes.current_app')
    def test_upload_calls_supabase_insert(self, mock_app, mock_embedding, mock_qr, mock_render, client):
        """POST /upload debe llamar a guardar_memoria en Supabase"""
        mock_qr.return_value.save = MagicMock()
        mock_embedding.return_value = [0.1, 0.2]
        mock_app.supabase.table.return_value.insert.return_value.execute.return_value = None

        data = {
            'image': (BytesIO(b'fake image data'), 'test.jpg'),
            'persona': 'Carlos',
            'title': 'Experiencia',
            'description': 'Descripción'
        }

        response = client.post('/upload', data=data, content_type='multipart/form-data')

        # Verificar que Supabase insert fue llamado
        mock_app.supabase.table.assert_called_with('aria_embeddings')
