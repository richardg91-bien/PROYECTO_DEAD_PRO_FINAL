"""
Tests para rutas que interactúan con base de datos
"""
import pytest
from unittest.mock import patch
from app import get_db


class TestGaleriaDatabase:
    """Tests para GET /galeria"""

    @patch('app.routes.render_template')
    def test_galeria_empty_database(self, mock_render, client):
        """GET /galeria con BD vacía"""
        mock_render.return_value = "OK"
        response = client.get('/galeria')
        assert response.status_code == 200

    @patch('app.routes.render_template')
    def test_galeria_with_experiences(self, mock_render, client, sample_experiences):
        """GET /galeria con múltiples experiencias"""
        mock_render.return_value = "OK"
        response = client.get('/galeria')
        assert response.status_code == 200

    @patch('app.routes.render_template')
    def test_galeria_calls_render_template(self, mock_render, client):
        """GET /galeria debe llamar a render_template"""
        mock_render.return_value = "OK"
        response = client.get('/galeria')
        mock_render.assert_called_once()
        # Verificar que se pasa el nombre de template correcto
        assert mock_render.call_args[0][0] == 'galeria.html'


class TestExperienciaRoute:
    """Tests para GET /experiencia/<id>"""

    @patch('app.routes.render_template')
    def test_experiencia_found(self, mock_render, client, sample_experience):
        """GET /experiencia/<id> con ID válido"""
        mock_render.return_value = "OK"
        response = client.get(f'/experiencia/{sample_experience}')
        assert response.status_code == 200
        mock_render.assert_called_once()

    def test_experiencia_not_found(self, client):
        """GET /experiencia/<id> con ID inválido"""
        response = client.get('/experiencia/uuid-inexistente')
        assert response.status_code == 200
        assert b'no encontrada' in response.data

    @patch('app.routes.render_template')
    def test_experiencia_verifica_datos_en_bd(self, mock_render, client, app_context, sample_experience):
        """Verificar que experiencia existe en BD"""
        db = get_db()
        exp = db.execute("SELECT * FROM experiences WHERE id=?", (sample_experience,)).fetchone()
        db.close()

        assert exp is not None
        assert exp['persona'] == 'Juan'
        assert exp['title'] == 'Test Title'

    @patch('app.routes.render_template')
    def test_experiencia_multiple_records(self, mock_render, client, app_context):
        """Crear múltiples experiencias y verificar búsqueda"""
        db = get_db()

        # Crear dos experiencias
        db.execute(
            "INSERT INTO experiences VALUES (?,?,?,?,?,?)",
            ('exp-1', 'Persona1', 'Título 1', 'Desc 1', 'img1.jpg', 'qr1.png')
        )
        db.execute(
            "INSERT INTO experiences VALUES (?,?,?,?,?,?)",
            ('exp-2', 'Persona2', 'Título 2', 'Desc 2', 'img2.jpg', 'qr2.png')
        )
        db.commit()

        # Obtener exp1
        exp1 = db.execute("SELECT * FROM experiences WHERE id=?", ('exp-1',)).fetchone()
        # Obtener exp2
        exp2 = db.execute("SELECT * FROM experiences WHERE id=?", ('exp-2',)).fetchone()

        db.close()

        assert exp1['persona'] == 'Persona1'
        assert exp2['persona'] == 'Persona2'
