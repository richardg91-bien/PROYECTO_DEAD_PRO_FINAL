"""Tests unitarios para guardar_imagen en app/services/upload_service.py.

Cubre: nombres sin extensión, extensiones anidadas y creación de directorios.
"""

import os
import uuid

import pytest
from werkzeug.datastructures import FileStorage

from app.services.upload_service import guardar_imagen


def _make_file(filename, content=b"contenido-de-prueba"):
    """Crea un FileStorage simulado con el nombre indicado."""
    from io import BytesIO
    return FileStorage(stream=BytesIO(content), filename=filename)


class TestGuardarImagen:

    def test_guarda_archivo_y_devuelve_nombre_unico(self, tmp_path):
        file = _make_file("foto.png")
        resultado = guardar_imagen(file, upload_folder=str(tmp_path))

        assert resultado.endswith(".png")
        assert (tmp_path / resultado).exists()
        assert (tmp_path / resultado).read_bytes() == b"contenido-de-prueba"

    def test_nombre_sin_extension_usa_jpg(self, tmp_path):
        """Un filename sin extensión recibe la extensión por defecto .jpg."""
        file = _make_file("sinextension")
        resultado = guardar_imagen(file, upload_folder=str(tmp_path))

        assert resultado.endswith(".jpg")
        assert (tmp_path / resultado).exists()

    def test_extension_anidada_usa_ultima_parte(self, tmp_path):
        """Con 'foto.tar.png' se usa la última extensión (png), no 'tar.png'."""
        file = _make_file("foto.tar.png")
        resultado = guardar_imagen(file, upload_folder=str(tmp_path))

        assert resultado.endswith(".png")
        assert not resultado.endswith(".tar.png")

    def test_crea_directorio_si_no_existe(self, tmp_path):
        """El directorio destino se crea automáticamente."""
        destino = tmp_path / "sub" / "carpeta" / "profunda"
        file = _make_file("imagen.jpg")

        resultado = guardar_imagen(file, upload_folder=str(destino))

        assert destino.is_dir()
        assert (destino / resultado).exists()

    def test_filename_none_usa_jpg(self, tmp_path):
        """Si el FileStorage no tiene filename, también cae en .jpg."""
        from io import BytesIO
        file = FileStorage(stream=BytesIO(b"data"), filename=None)

        resultado = guardar_imagen(file, upload_folder=str(tmp_path))

        assert resultado.endswith(".jpg")
        assert (tmp_path / resultado).exists()

    def test_dos_guardados_producen_nombres_distintos(self, tmp_path):
        """Dos archivos con el mismo nombre generan nombres únicos (uuid)."""
        r1 = guardar_imagen(_make_file("igual.png"), upload_folder=str(tmp_path))
        r2 = guardar_imagen(_make_file("igual.png"), upload_folder=str(tmp_path))

        assert r1 != r2

    def test_nombre_inseguro_se_sanea_pero_mantiene_extension(self, tmp_path):
        """secure_filename convierte rutas raras; la extensión se conserva."""
        file = _make_file("..\\..\\malicioso.jpg")
        resultado = guardar_imagen(file, upload_folder=str(tmp_path))

        assert resultado.endswith(".jpg")
        # No debe escaparse del directorio destino
        assert (tmp_path / resultado).exists()
