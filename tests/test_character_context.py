from app.character.context_builder import construir_contexto_personaje, contexto_a_prompt
from app.services.emotion_service import analizar_emocion, detectar_emocion


def test_emocion_contextual_no_mutable():
    emocion = analizar_emocion("Te extraño mucho, me da nostalgia")
    assert emocion["emocion"] == "triste"
    assert 0 < emocion["intensidad"] <= 1
    assert 0 < emocion["confianza"] <= 1
    assert detectar_emocion("Estoy feliz") == "feliz"


def test_contexto_aisla_persona_y_limita_historial():
    persona = {
        "id": "persona-1",
        "nombre": "Carlos",
        "bio": "Biografía de Carlos",
        "fecha_nacimiento": None,
        "fecha_fallecimiento": None,
        "lugar_nacimiento": None,
        "lugar_fallecimiento": None,
    }
    personalidad = {
        "traits": {"amable": True},
        "values": {"familia": "alta"},
        "temperament": {"calma": True},
        "communication_style": {"tono": "cercano"},
        "humor_style": {},
        "likes": ["música"],
        "dislikes": ["mentiras"],
        "behavioral_rules": ["no inventar"],
    }
    recuerdos = [
        {"contenido": "Recuerdo de Carlos", "tipo": "familia", "importancia": 5}
    ]
    historial = [{"role": "user", "content": str(i)} for i in range(12)]

    contexto = construir_contexto_personaje(
        persona, personalidad, recuerdos,
        {"emocion": "amor", "intensidad": 0.7, "confianza": 0.8},
        historial,
    )

    assert contexto["identidad"]["id"] == "persona-1"
    assert contexto["memorias"][0]["contenido"] == "Recuerdo de Carlos"
    assert contexto["emocion_visitante"]["emocion"] == "amor"
    assert len(contexto["historial"]) == 10
    assert contexto["historial"][0]["content"] == "2"
    assert contexto["historial"][-1]["content"] == "11"

    prompt = contexto_a_prompt(contexto)
    assert "Carlos" in prompt
    assert "Recuerdo de Carlos" in prompt
    assert "amor" in prompt
