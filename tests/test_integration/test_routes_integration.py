"""Pruebas de integracion basicas con servicios externos mockeados."""


def test_protected_routes_reject_missing_token(client):
    assert client.get("/upload").status_code == 401
    assert client.get("/chat").status_code == 401
    assert client.get("/admin").status_code == 401


def test_debug_route_reports_clients(client):
    response = client.get("/debug")
    assert response.status_code == 200
    assert response.get_json()["supabase"] is True


def test_auth_me_with_token(client, auth_headers):
    response = client.get("/api/auth/me", headers=auth_headers)
    assert response.status_code == 200
    assert response.get_json()["email"] == "test@example.com"
