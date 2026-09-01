import pytest
from unittest.mock import MagicMock, patch
from app import create_app


def test_chat_post_uses_deepseek_model(client, app, auth_headers):
    response_mock = MagicMock()
    response_mock.choices = [MagicMock()]
    response_mock.choices[0].message.content = "Respuesta"
    response_mock.model = "llama-3.1-8b-instant"

    app.openai_client = MagicMock()
    app.openai_client.chat.completions.create.return_value = response_mock

    response = client.post("/chat", data={"message": "Hola mundo"}, headers=auth_headers)

    assert response.status_code == 200
    call_kwargs = app.openai_client.chat.completions.create.call_args.kwargs
    # El modelo por defecto es llama-3.1-8b-instant (Groq), no deepseek-chat
    assert call_kwargs["model"] == "llama-3.1-8b-instant"
    assert call_kwargs["messages"][0]["content"] == "Hola mundo"
