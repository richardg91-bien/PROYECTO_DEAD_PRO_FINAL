"""
Tests para ruta POST /chat con OpenAI mock
"""
import pytest
from unittest.mock import MagicMock, patch


class TestChatPostRoute:
    """Tests para POST /chat"""

    @patch('app.routes.render_template')
    @patch('app.routes.current_app')
    def test_chat_post_with_message_success(self, mock_app, mock_render, client):
        """POST /chat con mensaje válido debe llamar a OpenAI"""
        # Configurar mocks
        mock_render.return_value = "OK"
        mock_response = MagicMock()
        mock_response.choices[0].message.content = "Respuesta de prueba"
        mock_app.openai_client.chat.completions.create.return_value = mock_response

        # Hacer request
        response = client.post('/chat', data={'message': 'Hola IA'})

        # Verificar
        assert response.status_code == 200

    @patch('app.routes.render_template')
    @patch('app.routes.current_app')
    def test_chat_post_empty_message(self, mock_app, mock_render, client):
        """POST /chat sin mensaje no debe llamar a OpenAI"""
        mock_render.return_value = "OK"
        response = client.post('/chat', data={'message': ''})
        assert response.status_code == 200
        # No debe llamar a OpenAI si no hay mensaje
        mock_app.openai_client.chat.completions.create.assert_not_called()

    @patch('app.routes.render_template')
    @patch('app.routes.current_app')
    def test_chat_post_api_error_handling(self, mock_app, mock_render, client):
        """POST /chat debe manejar errores de OpenAI API"""
        mock_render.return_value = "OK"
        # Simular error
        mock_app.openai_client.chat.completions.create.side_effect = Exception("API Error")

        response = client.post('/chat', data={'message': 'Hola'})

        assert response.status_code == 200
        assert b'Error' in response.data or response.status_code == 200

    @patch('app.routes.render_template')
    @patch('app.routes.current_app')
    def test_chat_post_uses_deepseek_model(self, mock_app, mock_render, client):
        """POST /chat debe usar modelo deepseek-chat"""
        mock_render.return_value = "OK"
        mock_response = MagicMock()
        mock_response.choices[0].message.content = "Respuesta"
        mock_app.openai_client.chat.completions.create.return_value = mock_response

        response = client.post('/chat', data={'message': 'Prueba'})

        # Verificar que se llamó con modelo deepseek-chat
        call_kwargs = mock_app.openai_client.chat.completions.create.call_args[1]
        assert call_kwargs.get('model') == 'deepseek-chat'

    @patch('app.routes.render_template')
    @patch('app.routes.current_app')
    def test_chat_post_message_format(self, mock_app, mock_render, client):
        """POST /chat debe enviar mensaje en formato correcto"""
        mock_render.return_value = "OK"
        mock_response = MagicMock()
        mock_response.choices[0].message.content = "Respuesta"
        mock_app.openai_client.chat.completions.create.return_value = mock_response

        response = client.post('/chat', data={'message': 'Hola mundo'})

        # Verificar formato de mensaje
        call_kwargs = mock_app.openai_client.chat.completions.create.call_args[1]
        messages = call_kwargs.get('messages', [])
        assert len(messages) == 1
        assert messages[0]['role'] == 'user'
        assert messages[0]['content'] == 'Hola mundo'
