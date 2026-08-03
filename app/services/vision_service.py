import requests
import os

def describir_imagen(ruta_o_url_imagen):
    """
    Llama a la API de Groq para describir una imagen.
    
    Args:
        ruta_o_url_imagen (str): Ruta local o URL pública de la imagen.
        
    Returns:
        str: Descripción en texto generada por el modelo.
        
    Raises:
        Exception: Si la llamada a la API falla o no se encuentra la clave API.
    """
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        raise Exception("No se encontró GROQ_API_KEY en las variables de entorno.")
    
    endpoint = "https://api.groq.com/openai/v1/chat/completions"
    
    prompt = f"Describe el contenido de esta imagen: {ruta_o_url_imagen}"
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    data = {
        "model": "llama-3.2-11b-vision-preview",
        "messages": [{"role": "user", "content": prompt}]
    }
    
    response = requests.post(endpoint, json=data, headers=headers)
    
    if response.status_code == 200:
        result = response.json()
        descripcion = result.get("choices", [{}])[0].get("message", {}).get("content", "")
        return descripcion.strip()
    else:
        raise Exception(f"Error en API de visión Groq: {response.status_code} - {response.text}")
