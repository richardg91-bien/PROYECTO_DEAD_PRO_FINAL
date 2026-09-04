import pytest

from app.character.conversation import obtener_conversacion, obtener_mensajes


class _RPC:
    def __init__(self):
        self.calls = []

    def rpc(self, name, params):
        self.calls.append((name, params))
        return self

    def execute(self):
        return type("Response", (), {"data": []})()


class _App:
    def __init__(self):
        self.supabase = _RPC()


@pytest.fixture
def app(monkeypatch):
    fake = _App()
    monkeypatch.setattr("app.character.conversation.current_app", fake)
    return fake


def test_conversation_lookup_requires_session_for_public_path(app):
    assert obtener_conversacion("11111111-1111-1111-1111-111111111111", "session-a") is None
    assert app.supabase.calls[0][0] == "get_conversation_for_session"
    assert app.supabase.calls[0][1]["target_session_id"] == "session-a"


def test_messages_lookup_uses_exact_session_and_bounded_limit(app):
    assert obtener_mensajes("11111111-1111-1111-1111-111111111111", limit=999, session_id="session-b") == []
    name, params = app.supabase.calls[0]
    assert name == "get_conversation_messages_for_session"
    assert params["target_session_id"] == "session-b"
    assert params["message_limit"] == 100
