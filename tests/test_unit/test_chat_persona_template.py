from pathlib import Path


def test_chat_persona_template_incluye_animacion_hablante():
    template_path = Path("app/templates/chat_persona.html")
    content = template_path.read_text(encoding="utf-8")

    assert "avatar-speaking" in content
    assert "avatar-{{ avatar_state or 'neutral' }}" in content
