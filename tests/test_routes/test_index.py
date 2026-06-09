"""Tests para endpoints publicos principales."""


def test_index_route(client):
    response = client.get("/")
    assert response.status_code == 200
    assert b"Proyecto Dead" in response.data


def test_api_test_route(client):
    response = client.get("/api/test")
    assert response.status_code == 200
    assert response.get_json()["status"] == "ok"


def test_upload_requires_auth(client):
    response = client.get("/upload")
    assert response.status_code == 401


def test_chat_requires_auth(client):
    response = client.get("/chat")
    assert response.status_code == 401


def test_admin_requires_auth(client):
    response = client.get("/admin")
    assert response.status_code == 401
