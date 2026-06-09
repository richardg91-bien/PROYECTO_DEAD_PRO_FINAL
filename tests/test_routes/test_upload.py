"""Tests para upload protegido."""

from io import BytesIO
from unittest.mock import patch


def test_upload_get_authenticated(client, auth_headers):
    response = client.get("/upload", headers=auth_headers)
    assert response.status_code == 200


def test_upload_missing_file(client, auth_headers):
    data = {
        "persona": "Juan",
        "title": "Recuerdo",
        "description": "Descripcion de prueba suficientemente larga",
    }

    response = client.post("/upload", data=data, headers=auth_headers, content_type="multipart/form-data")

    assert response.status_code == 400


def test_upload_calls_supabase_insert(client, auth_headers, supabase_mock):
    data = {
        "image": (BytesIO(b"fake image data"), "test.png"),
        "persona": "Carlos",
        "title": "Experiencia",
        "description": "Descripcion de prueba suficientemente larga",
    }

    with patch("app.routes.generar_embedding", return_value=[0.1, 0.2]), patch(
        "app.routes.guardar_memoria", return_value=True
    ):
        response = client.post("/upload", data=data, headers=auth_headers, content_type="multipart/form-data")

    assert response.status_code == 302
    supabase_mock.table.assert_any_call("experiences")
