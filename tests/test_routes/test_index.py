"""Tests para endpoints publicos principales."""

import pytest

from app import create_app


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


def test_health_route(client):
    response = client.get("/health")
    assert response.status_code == 200
    payload = response.get_json()
    assert payload["status"] == "ok"
    assert payload["service"] == "dead-pro"


def test_production_requires_secret_key(monkeypatch):
    monkeypatch.setenv("SUPABASE_URL", "https://test.supabase.co")
    monkeypatch.setenv("SUPABASE_KEY", "test-key")
    monkeypatch.delenv("SECRET_KEY", raising=False)
    monkeypatch.setenv("FLASK_ENV", "production")

    with pytest.raises(ValueError, match="SECRET_KEY"):
        create_app()
