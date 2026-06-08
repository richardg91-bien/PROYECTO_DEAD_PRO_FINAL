"""Servicio de carga de archivos y generación de QR"""

import os
import uuid
import qrcode
from werkzeug.utils import secure_filename


def guardar_imagen(file, upload_folder="static/uploads"):
    """
    Guarda archivo de imagen con nombre único.
    
    Args:
        file: Objeto FileStorage de Flask
        upload_folder (str): Carpeta destino
        
    Returns:
        str: Nombre del archivo guardado
    """
    os.makedirs(upload_folder, exist_ok=True)
    
    uid = str(uuid.uuid4())
    filename = f"{uid}.jpg"
    filepath = os.path.join(upload_folder, filename)
    
    file.save(filepath)
    return filename


def generar_qr(url, qr_folder="static/qr"):
    """
    Genera código QR para una URL.
    
    Args:
        url (str): URL a codificar
        qr_folder (str): Carpeta destino
        
    Returns:
        str: Nombre del archivo QR generado
    """
    os.makedirs(qr_folder, exist_ok=True)
    
    uid = str(uuid.uuid4())
    qr_name = f"{uid}.png"
    qr_path = os.path.join(qr_folder, qr_name)
    
    qrcode.make(url).save(qr_path)
    return qr_name
