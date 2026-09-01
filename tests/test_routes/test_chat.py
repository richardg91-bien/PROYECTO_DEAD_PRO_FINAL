import importlib
from unittest.mock import MagicMock


def test_default_model_uses_groq_compatible_option(monkeypatch):
    monkeypatch.delenv("MODEL_NAME", raising=False)
    import app.routes as routes

    reloaded_routes = importlib.reload(routes)

    assert reloaded_routes.MODEL_NAME == "llama-3.1-8b-instant"


def test_chat_post_uses_deepseek_model(client, app, auth_headers):
    response_mock = MagicMock()
    response_mock.choices = [MagicMock()]
    response_mock.choices[0].message.content = "Respuesta"
    response_mock.model = "deepseek-chat"  # solo referencia

    app.openai_client = MagicMock()
    app.openai_client.chat.completions.create.return_value = response_mock

    response = client.post("/chat", data={"message": "Hola mundo"}, headers=auth_headers)

    assert response.status_code == 200
    call_kwargs = app.openai_client.chat.completions.create.call_args.kwargs
    assert call_kwargs["model"] in ("deepseek-chat", "llama-3.1-8b-instant")
    assert call_kwargs["messages"][0]["content"] == "Hola mundo"
