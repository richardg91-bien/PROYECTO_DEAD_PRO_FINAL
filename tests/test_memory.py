import pytest
from app.services.memory_service import guardar_memoria, obtener_memorias_personaje

def test_guardar_y_obtener_memoria(app):
    with app.app_context():
        persona = "TestUser"
        contenido = "Mensaje de prueba"
        embedding = [0.01] * 1536

        exito = guardar_memoria(persona, contenido, embedding, tipo='conversacion')
        assert exito

        memorias = obtener_memorias_personaje(persona, embedding)
        assert any(m['contenido'] == contenido for m in memorias)

def test_api_chat(client, auth_headers):
    response = client.post("/api/chat/TestUser", json={
        "message": "Hola",
        "historial": []
    }, headers=auth_headers)
    assert response.status_code == 200
    data = response.get_json()
    assert "respuesta" in data
    assert "emocion" in data
