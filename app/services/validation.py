"""Servicio de validación"""

import os
from werkzeug.utils import secure_filename


ALLOWED_EXTENSIONS = {'jpg', 'jpeg', 'png', 'gif', 'webp'}
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB


def validar_archivo_imagen(file):
    """
    Valida que un archivo sea una imagen válida.
    
    Args:
        file: Objeto FileStorage de Flask
        
    Returns:
        tuple: (válido: bool, error: str o None)
    """
    if not file or not file.filename:
        return False, "No se proporcionó archivo"
    
    # Validar extensión
    filename = secure_filename(file.filename)
    if '.' not in filename:
        return False, "El archivo debe tener extensión"
    
    ext = filename.rsplit('.', 1)[1].lower()
    if ext not in ALLOWED_EXTENSIONS:
        return False, f"Extensión no permitida. Usa: {', '.join(ALLOWED_EXTENSIONS)}"
    
    # Validar tamaño
    file.seek(0, os.SEEK_END)
    file_length = file.tell()
    file.seek(0)
    
    if file_length > MAX_FILE_SIZE:
        return False, f"Archivo muy grande. Máximo: {MAX_FILE_SIZE // 1024 // 1024}MB"
    
    if file_length == 0:
        return False, "Archivo vacío"
    
    return True, None


def validar_form_upload(persona, title, description):
    """
    Valida datos del formulario de upload.
    
    Args:
        persona (str): Nombre de persona
        title (str): Título de experiencia
        description (str): Descripción
        
    Returns:
        tuple: (válido: bool, error: str o None)
    """
    if not all([persona, title, description]):
        return False, "Faltan campos requeridos (persona, title, description)"
    
    persona = persona.strip()
    title = title.strip()
    description = description.strip()
    
    if len(persona) < 2 or len(persona) > 100:
        return False, "Nombre de persona debe tener entre 2 y 100 caracteres"
    
    if len(title) < 3 or len(title) > 200:
        return False, "Título debe tener entre 3 y 200 caracteres"
    
    if len(description) < 10 or len(description) > 2000:
        return False, "Descripción debe tener entre 10 y 2000 caracteres"
    
    return True, None


def validar_mensaje_chat(mensaje):
    """
    Valida mensaje de chat.
    
    Args:
        mensaje (str): Mensaje del usuario
        
    Returns:
        tuple: (válido: bool, error: str o None)
    """
    if not mensaje or not isinstance(mensaje, str):
        return False, "Mensaje inválido"
    
    mensaje = mensaje.strip()
    
    if len(mensaje) == 0 or len(mensaje) > 5000:
        return False, "Mensaje debe tener entre 1 y 5000 caracteres"
    
    return True, None
