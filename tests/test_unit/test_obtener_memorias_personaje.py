"""Tests para obtener_memorias_personaje en app/services/memory_service.py.

Cubre: ruta de error del RPC, datos vacíos y filtrado por persona/None.
"""

import pytest
from unittest.mock import MagicMock

from app.services.memory_service import obtener_memorias_personaje


@pytest.fixture
def supabase_rpc_mock():
    """Cliente supabase simulado con la cadena rpc().execute()."""
    client = MagicMock()
    return client


class TestObtenerMemoriasPersonaje:

    def test_rpc_error_devuelve_lista_vacia(self, supabase_rpc_mock, monkeypatch):
        """Si el RPC lanza excepción, retorna [] en lugar de propagarla."""
        supabase_rpc_mock.rpc.side_effect = Exception("RPC connection failed")
        monkeypatch.setattr(
            "app.services.memory_service.current_app",
            MagicMock(supabase=supabase_rpc_mock),
        )

        resultado = obtener_memorias_personaje("Ana", [0.1] * 4)

        assert resultado == []
        supabase_rpc_mock.rpc.assert_called_once()

    def test_datos_vacios_devuelve_lista_vacia(self, supabase_rpc_mock, monkeypatch):
        """Si el RPC no devuelve datos, retorna []."""
        supabase_rpc_mock.rpc.return_value.execute.return_value.data = None
        monkeypatch.setattr(
            "app.services.memory_service.current_app",
            MagicMock(supabase=supabase_rpc_mock),
        )

        resultado = obtener_memorias_personaje("Ana", [0.1] * 4)

        assert resultado == []

    def test_filtrar_por_persona(self, supabase_rpc_mock, monkeypatch):
        """Solo se devuelven memorias cuya persona coincida con la solicitada."""
        supabase_rpc_mock.rpc.return_value.execute.return_value.data = [
            {"contenido": "m1", "persona": "Ana"},
            {"contenido": "m2", "persona": "Juan"},
        ]
        monkeypatch.setattr(
            "app.services.memory_service.current_app",
            MagicMock(supabase=supabase_rpc_mock),
        )

        resultado = obtener_memorias_personaje("Ana", [0.1] * 4)

        assert len(resultado) == 1
        assert resultado[0]["contenido"] == "m1"
        assert resultado[0]["persona"] == "Ana"

    def test_incluir_memorias_sin_persona(self, supabase_rpc_mock, monkeypatch):
        """Las memorias con persona None (de otros usuarios) se incluyen."""
        supabase_rpc_mock.rpc.return_value.execute.return_value.data = [
            {"contenido": "global", "persona": None},
            {"contenido": "de ana", "persona": "Ana"},
        ]
        monkeypatch.setattr(
            "app.services.memory_service.current_app",
            MagicMock(supabase=supabase_rpc_mock),
        )

        resultado = obtener_memorias_personaje("Ana", [0.1] * 4)

        assert len(resultado) == 2
        contenidos = {m["contenido"] for m in resultado}
        assert contenidos == {"global", "de ana"}

    def test_parametros_rpc_correctos(self, supabase_rpc_mock, monkeypatch):
        """El RPC recibe embedding, threshold y count tal como se pasan."""
        supabase_rpc_mock.rpc.return_value.execute.return_value.data = []
        monkeypatch.setattr(
            "app.services.memory_service.current_app",
            MagicMock(supabase=supabase_rpc_mock),
        )

        embedding = [0.5] * 8
        obtener_memorias_personaje("Ana", embedding, threshold=0.7, limit=3)

        supabase_rpc_mock.rpc.assert_called_once_with(
            "match_documents",
            {
                "query_embedding": embedding,
                "match_threshold": 0.7,
                "match_count": 3,
            },
        )
