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
    return client


@pytest.fixture
def app(supabase_mock, monkeypatch):
    monkeypatch.setenv("SUPABASE_URL", "https://test.supabase.co")
    monkeypatch.setenv("SUPABASE_KEY", "test-key")
    monkeypatch.setenv("SECRET_KEY", "test-secret")
    monkeypatch.delenv("DEEPSEEK_API_KEY", raising=False)

    with patch("app.create_client", return_value=supabase_mock), patch("app.OpenAI"):
        flask_app = create_app()
        flask_app.config.update(TESTING=True)
        yield flask_app


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture
def auth_headers():
    return {"Authorization": "Bearer test-token"}


@pytest.fixture
def mock_openai_response():
    response = MagicMock()
    response.choices = [MagicMock()]
    response.choices[0].message.content = "Respuesta de prueba de IA"
    return response
