# app/ia.py

def generar_embedding(texto):
    # EMBEDDING SIMULADO (para desarrollo)
    # Convierte texto en vector falso pero consistente

    import hashlib

    hash_obj = hashlib.sha256(texto.encode()).hexdigest()

    # convertimos hash en números
    vector = [int(hash_obj[i:i+2], 16) / 255 for i in range(0, 64, 2)]

    return vector