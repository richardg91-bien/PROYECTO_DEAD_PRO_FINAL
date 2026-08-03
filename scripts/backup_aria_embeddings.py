import json
from supabase import create_client
from dotenv import load_dotenv
load_dotenv()

import os

supabase_url = os.getenv("SUPABASE_URL", "TU_SUPABASE_URL")
supabase_key = os.getenv("SUPABASE_KEY", "TU_SUPABASE_API_KEY")

supabase = create_client(supabase_url, supabase_key)

def backup_aria_embeddings():
    response = supabase.table("aria_embeddings").select("*").execute()
    datos = response.data
    with open("scripts/backup_aria_embeddings.json", "w", encoding="utf-8") as f:
        json.dump(datos, f, ensure_ascii=False, indent=4)
    print(f"Backup completado, {len(datos)} registros guardados.")

if __name__ == "__main__":
    backup_aria_embeddings()
