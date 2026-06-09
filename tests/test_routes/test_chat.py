"""Tests para rutas de chat protegidas."""

from unittest.mock import MagicMock


def test_chat_get_authenticated(client, auth_headers):
    response = client.get("/chat", headers=auth_headers)
    assert response.status_code == 200


def test_chat_post_without_ai_configured(client, auth_headers):
    response = client.post("/chat", data={"message": "Hola"}, headers=auth_headers)
    assert response.status_code == 500
    assert "IA no configurada".encode() in response.data


def test_chat_post_uses_deepseek_model(client, app, auth_headers):
    response_mock = MagicMock()
    response_mock.choices[0].message.content = "Respuesta"
    app.openai_client = MagicMock()
    app.openai_client.chat.completions.create.return_value = response_mock

    response = client.post("/chat", data={"message": "Hola mundo"}, headers=auth_headers)

    assert response.status_code == 200
    call_kwargs = app.openai_client.chat.completions.create.call_args.kwargs
    assert call_kwargs["model"] == "deepseek-chat"
    assert call_kwargs["messages"][0]["content"] == "Hola mundo"
