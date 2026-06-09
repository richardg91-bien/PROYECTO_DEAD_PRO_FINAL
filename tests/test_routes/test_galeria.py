"""Tests para APIs de experiencias."""


def test_api_experiencias_returns_supabase_data(client, app, supabase_mock):
    supabase_mock.table.return_value.select.return_value.order.return_value.execute.return_value.data = [
        {"id": "exp-1", "persona": "Juan", "title": "Recuerdo"}
    ]

    response = client.get("/api/experiencias")

    assert response.status_code == 200
    assert response.get_json()[0]["id"] == "exp-1"


def test_api_experiencia_not_found(client, supabase_mock):
    supabase_mock.table.return_value.select.return_value.eq.return_value.execute.return_value.data = []

    response = client.get("/api/experiencia/no-existe")

    assert response.status_code == 404
    assert response.get_json()["error"] == "No encontrada"


def test_api_experiencia_found(client, supabase_mock):
    supabase_mock.table.return_value.select.return_value.eq.return_value.execute.return_value.data = [
        {"id": "exp-1", "persona": "Juan", "title": "Recuerdo"}
    ]

    response = client.get("/api/experiencia/exp-1")

    assert response.status_code == 200
    assert response.get_json()["persona"] == "Juan"
