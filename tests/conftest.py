"""Fixtures de prueba para la app Flask actual."""

from types import SimpleNamespace
from unittest.mock import MagicMock, patch
import pytest

from app import create_app

@pytest.fixture
def supabase_mock():
    client = MagicMock()
    client.auth.get_user.return_value = SimpleNamespace(
        user=SimpleNamespace(id="user-1", email="test@example.com")
    )
    client.table.return_value.insert.return_value.execute.return_value.error = None
    client.table.return_value.insert.return_value.execute.return_value.status_code = 201
    
    # Simulación de datos para obtener memorias semánticas (RPC)
    client.rpc.return_value.execute.return_value.data = [
        {
            "contenido": "Mensaje de prueba",
            "persona": "TestUser",
            "embedding": [0.01] * 1536,
            "tipo": "conversacion"
        }
    ]
    
    return client

@pytest.fixture
def mock_openai_response():
    response = MagicMock()
    response.choices = [MagicMock()]
    response.choices[0].message.content = "Respuesta de prueba de IA"
    # Para que pase test que espera alguno de estos modelos:
    response.model = "deepseek-chat"
    return response

@pytest.fixture
def app(supabase_mock, monkeypatch, mock_openai_response, request):
    monkeypatch.setenv("SUPABASE_URL", "https://test.supabase.co")
    monkeypatch.setenv("SUPABASE_KEY", "test-key")
    monkeypatch.setenv("SECRET_KEY", "test-secret")
    monkeypatch.delenv("DEEPSEEK_API_KEY", raising=False)

    with patch("app.create_client", return_value=supabase_mock), \
         patch("app.OpenAI") as mock_openai_class:

        if "no_ai" in request.keywords:
            mock_instance = None  # Simula ausencia de IA
        else:
            mock_instance = mock_openai_class.return_value
            mock_instance.chat.completions.create.return_value = mock_openai_response

        flask_app = create_app()
        flask_app.openai_client = mock_instance
        flask_app.config.update(TESTING=True)
        yield flask_app

@pytest.fixture
def client(app):
    return app.test_client()

@pytest.fixture
def auth_headers():
    return {"Authorization": "Bearer test-token"}

# Registrar marcador 'no_ai' para evitar advertencias de pytest
def pytest_configure(config):
    config.addinivalue_line("markers", "no_ai: tests que simulan IA no configurada")
