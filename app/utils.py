import cloudinary.uploader

def subir_imagen(ruta):
    resultado = cloudinary.uploader.upload(ruta)
    return resultado["secure_url"]