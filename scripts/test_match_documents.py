import os
from supabase import create_client
from dotenv import load_dotenv

load_dotenv()

supabase_url = os.getenv("SUPABASE_URL")
supabase_key = os.getenv("SUPABASE_KEY")

supabase = create_client(supabase_url, supabase_key)

def test_match_documents():
    vector_dim = 1536
    query_embedding = [0.01] * vector_dim  # Vector de prueba

    response = supabase.rpc(
        "match_documents",
        {
            "query_embedding": query_embedding,
            "match_threshold": 0.5,
            "match_count": 5
        }
    ).execute()

    data = getattr(response, "data", None)

    if not data:
        print("No se encontraron resultados.")
    else:
        print("Resultados obtenidos:")
        for row in data:
            print(row)

if __name__ == "__main__":
    test_match_documents()
