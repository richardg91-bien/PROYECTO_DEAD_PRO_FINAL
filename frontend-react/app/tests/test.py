from sentence_transformers import SentenceTransformer

model = SentenceTransformer('all-MiniLM-L6-v2')

emb = model.encode("hola mundo")
print(len(emb))



SUPABASE_URL = "https://lrzpujlewhksygypxxry.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImxyenB1amxld2hrc3lneXB4eHJ5Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3Nzk5ODI2NTcsImV4cCI6MjA5NTU1ODY1N30.VvjJetAy5MRm1iqazxK1gNjH6lQ5qHFEqW3Gti57x1o"


