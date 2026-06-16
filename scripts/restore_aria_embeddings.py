import json
from supabase import create_client
from dotenv import load_dotenv
load_dotenv()

import os

supabase_url = os.getenv("SUPABASE_URL", "TU_SUPABASE_URL")
supabase_key = os.getenv("SUPABASE_KEY", "TU_SUPABASE_API_KEY")

supabase = create_client(supabase_url, supabase_key)

DIMENSION = 1536  # Ajusta según necesidad

def pad_vector(vec, dim=DIMENSION):
    padded = vec + [0.0] * (dim - len(vec))
    return padded[:dim]

def restore_backup():
    with open("scripts/backup_aria_embeddings.json", "r", encoding="utf-8") as f:
        datos = json.load(f)

    for registro in datos:
        embedding = registro.get("embedding", [])
        embedding = pad_vector(embedding)

        supabase.table("aria_embeddings").insert({
            "id": registro.get("id"),
            "persona": registro.get("persona"),
            "contenido": registro.get("contenido"),
            "embedding": embedding,
            "tipo": registro.get("tipo", "conversacion"),
            "created_at": registro.get("created_at")
        }).execute()

    print("Restauración completada.")

if __name__ == "__main__":
    restore_backup()
