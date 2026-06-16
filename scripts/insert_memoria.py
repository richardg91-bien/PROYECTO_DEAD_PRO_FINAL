import os
from supabase import create_client
from dotenv import load_dotenv

load_dotenv()

supabase_url = os.getenv("SUPABASE_URL")
supabase_key = os.getenv("SUPABASE_KEY")

supabase = create_client(supabase_url, supabase_key)

def insertar_memoria():
    vector_dim = 1536
    vector = [0.01] * vector_dim

    data = {
        "persona": "TestUser",
        "contenido": "Memoria prueba vector completo con 1536 dimensiones",
        "embedding": vector,
        "tipo": "conversacion"
    }

    result = supabase.table("aria_embeddings").insert(data).execute()

    # Revisar respuesta adecuadamente
    if hasattr(result, "error") and result.error is None:
        print("Memoria insertada con éxito")
    elif hasattr(result, "status_code") and result.status_code in (200, 201):
        print("Memoria insertada con éxito")
    else:
        print("Error al insertar memoria:", getattr(result, "error", result))

if __name__ == "__main__":
    insertar_memoria()
