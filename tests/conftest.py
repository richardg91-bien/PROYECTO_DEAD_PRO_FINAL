"""
Configuración de tests y fixtures compartidas
"""
import pytest
import sqlite3
import os
import tempfile
from unittest.mock import MagicMock, patch
from app import create_app, get_db


@pytest.fixture
def app(tmp_path, monkeypatch):
    """Crea una instancia de app para testing"""
    # Cambiar directorios a temporal
    monkeypatch.chdir(tmp_path)

    # Crear directorios necesarios
    (tmp_path / "app" / "templates").mkdir(parents=True, exist_ok=True)
    (tmp_path / "static" / "uploads").mkdir(parents=True, exist_ok=True)
    (tmp_path / "static" / "qr").mkdir(parents=True, exist_ok=True)

    app = create_app()
    app.config['TESTING'] = True

    # Usar BD temporal para tests
    with app.app_context():
        # Inicializar BD
        db = get_db()
        db.execute("""
        CREATE TABLE IF NOT EXISTS experiences (
            id TEXT PRIMARY KEY,
            persona TEXT,
            title TEXT,
            description TEXT,
            image TEXT,
            qr TEXT
        )
        """)
        db.commit()
        db.close()

        yield app


@pytest.fixture
def client(app):
    """Cliente de prueba para hacer requests"""
    return app.test_client()


@pytest.fixture
def app_context(app):
    """Context de app para ejecutar código dentro de app context"""
    with app.app_context():
        yield app


@pytest.fixture
def sample_experience(app_context):
    """Crea una experiencia de prueba en BD"""
    db = get_db()
    db.execute(
        "INSERT INTO experiences VALUES (?,?,?,?,?,?)",
        ('test-uuid-123', 'Juan', 'Test Title', 'Test Description', 'test.jpg', 'test-qr.png')
    )
    db.commit()
    db.close()
    return 'test-uuid-123'


@pytest.fixture
def sample_experiences(app_context):
    """Crea múltiples experiencias de prueba en BD"""
    db = get_db()
    experiences = [
        ('uuid-1', 'María', 'Título 1', 'Descripción 1', 'img1.jpg', 'qr1.png'),
        ('uuid-2', 'Carlos', 'Título 2', 'Descripción 2', 'img2.jpg', 'qr2.png'),
        ('uuid-3', 'Ana', 'Título 3', 'Descripción 3', 'img3.jpg', 'qr3.png'),
    ]

    for exp in experiences:
        db.execute(
            "INSERT INTO experiences VALUES (?,?,?,?,?,?)",
            exp
        )
    db.commit()
    db.close()

    return experiences


@pytest.fixture
def mock_openai_response():
    """Mock para respuesta de OpenAI"""
    mock_response = MagicMock()
    mock_response.choices = [MagicMock()]
    mock_response.choices[0].message.content = "Respuesta de prueba de IA"
    return mock_response


@pytest.fixture
def mock_supabase_insert():
    """Mock para inserción en Supabase"""
    with patch('app.routes.current_app.supabase') as mock_supabase:
        mock_supabase.table.return_value.insert.return_value.execute.return_value = None
        yield mock_supabase


@pytest.fixture
def mock_supabase_match():
    """Mock para búsqueda semántica en Supabase"""
    mock_response_data = [
        {'contenido': 'Recuerdo 1', 'similarity': 0.9},
        {'contenido': 'Recuerdo 2', 'similarity': 0.85},
    ]

    with patch('app.routes.current_app.supabase') as mock_supabase:
        mock_rpc = MagicMock()
        mock_rpc.execute.return_value.data = mock_response_data
        mock_supabase.rpc.return_value = mock_rpc
        yield mock_supabase


@pytest.fixture
def mock_generar_audio():
    """Mock para generación de audio"""
    with patch('app.routes.generar_audio') as mock_audio:
        mock_audio.return_value = 'static/audio/test-uuid.mp3'
        yield mock_audio


@pytest.fixture
def mock_generar_embedding():
    """Mock para generación de embeddings"""
    with patch('app.routes.generar_embedding') as mock_embedding:
        mock_embedding.return_value = [0.1, 0.2, 0.3, 0.4, 0.5]
        yield mock_embedding


@pytest.fixture
def tmp_upload_dir(tmp_path):
    """Directorio temporal para uploads"""
    upload_dir = tmp_path / "static" / "uploads"
    upload_dir.mkdir(parents=True)
    return upload_dir
