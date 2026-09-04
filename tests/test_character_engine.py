"""Pruebas unitarias del Character Engine de Visión 1."""

from types import SimpleNamespace

import pytest

from app.character import character_engine


class FakeCompletions:
    def create(self, **kwargs):
        self.kwargs = kwargs
        return SimpleNamespace(
            choices=[SimpleNamespace(message=SimpleNamespace(content="Respuesta de prueba"))]
        )


class FakeClient:
    def __init__(self):
        self.chat = SimpleNamespace(completions=FakeCompletions())


class FakeApp:
    openai_client = FakeClient()


@pytest.fixture
def contexto_base(monkeypatch):
    persona = {
        "id": "persona-1",
        "nombre": "Carlos",
        "bio": "Persona de prueba",
        "fecha_nacimiento": None,
        "fecha_fallecimiento": None,
        "lugar_nacimiento": None,
        "lugar_fallecimiento": None,
    }
    personalidad = {
        "traits": {"calma": True},
        "values": {"familia": "alta"},
        "temperament": {},
        "communication_style": {"tono": "cercano"},
        "humor_style": {},
        "likes": ["musica"],
        "dislikes": [],
        "behavioral_rules": [],
    }

    monkeypatch.setattr(character_engine, "get_persona_by_id", lambda app, pid: persona)
    monkeypatch.setattr(character_engine, "obtener_personalidad", lambda pid: personalidad)
    monkeypatch.setattr(character_engine, "generar_embedding", lambda text: [0.1, 0.2])
    monkeypatch.setattr(
        character_engine,
        "obtener_memorias_persona",
        lambda persona_id, embedding, threshold, limit: [
            {"contenido": "Le gustaba la música", "tipo": "gustos", "importancia": 5}
        ],
    )
    return persona


def test_construir_contexto_aisla_persona_y_emocion(monkeypatch, contexto_base):
    contexto = character_engine.construir_contexto(
        "persona-1", "Te extraño muchísimo!", historial=[{"role": "user", "content": "Hola"}]
    )

    assert contexto["identidad"]["id"] == "persona-1"
    assert contexto["memorias"][0]["contenido"] == "Le gustaba la música"
    assert contexto["emocion_visitante"]["emocion"] == "triste"
    assert contexto["historial"] == [{"role": "user", "content": "Hola"}]


def test_generar_respuesta_incluye_contexto_emocional(monkeypatch, contexto_base):
    fake_app = FakeApp()
    monkeypatch.setattr(character_engine, "current_app", fake_app)

    resultado = character_engine.generar_respuesta("persona-1", "Te extraño mucho")

    assert resultado["respuesta"] == "Respuesta de prueba"
    assert resultado["persona"]["id"] == "persona-1"
    assert resultado["memorias_utilizadas"] == 1
    assert resultado["emocion_contexto"]["emocion"] == "triste"

    prompt = fake_app.openai_client.chat.completions.kwargs["messages"][0]["content"]
    assert "MEMORIAS RELEVANTES" in prompt
    assert "EMOCIÓN ACTUAL DEL VISITANTE: triste" in prompt


def test_persona_inexistente_no_llama_al_llm(monkeypatch):
    fake_app = FakeApp()
    monkeypatch.setattr(character_engine, "current_app", fake_app)
    monkeypatch.setattr(character_engine, "get_persona_by_id", lambda app, pid: None)

    assert character_engine.generar_respuesta("missing", "Hola") is None
