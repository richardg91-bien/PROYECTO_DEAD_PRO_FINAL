from app.services.memory_service import (
    construir_contexto_persona,
    construir_perfil_inicial,
    construir_prompt_memorial,
    construir_url_avatar,
)


def test_construir_contexto_persona_incluye_perfil_y_memorias():
    contexto = construir_contexto_persona(
        "Camila",
        [{"contenido": "Le gusta conversar con energía"}],
        "Camila es alegre, expresiva y muy sociable"
    )

    assert "Camila" in contexto
    assert "alegre" in contexto.lower()
    assert "expresiva" in contexto.lower()
    assert "Le gusta conversar con energía" in contexto


def test_construir_perfil_inicial_sintetiza_informacion():
    perfil = construir_perfil_inicial(
        "Camila",
        "Persona sonriente y muy expresiva",
        "Recuerdo alegre",
        "Le gusta hablar con energía"
    )

    assert "Camila" in perfil
    assert "expresiva" in perfil.lower()
    assert "energía" in perfil.lower()


def test_construir_prompt_memorial_incluye_saludo_y_pregunta_personal():
    prompt = construir_prompt_memorial(
        "Lucía",
        "Perfil: alegre, cercana y muy expresiva",
        "Hola, quiero hablar contigo",
        "neutral",
    )

    assert "Lucía" in prompt
    assert "saludo" in prompt.lower()
    assert "pregunta personal" in prompt.lower()


def test_construir_url_avatar_devuelve_ruta_estatica():
    assert construir_url_avatar("foto.png") == "/static/uploads/foto.png"
