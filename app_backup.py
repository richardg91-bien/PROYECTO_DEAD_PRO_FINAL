from flask import Flask, render_template, request, redirect
import os
import uuid
import qrcode
import sqlite3
from  app.ia_service import generar_embedding
from supabase import create_client

app = Flask(__name__, 
            template_folder="app/templates",)

# =========================
# SUPABASE
# =========================
SUPABASE_URL = "https://lrzpujlewhksygypxxry.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImxyenB1amxld2hrc3lneXB4eHJ5Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3Nzk5ODI2NTcsImV4cCI6MjA5NTU1ODY1N30.VvjJetAy5MRm1iqazxK1gNjH6lQ5qHFEqW3Gti57x1o"
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

try:
    test = supabase.table("aria_embeddings").select("*").limit(1).execute()
    print("✅ SUPABASE CONECTADO")
except Exception as e:
    print("❌ ERROR SUPABASE:", e)

# =========================
# CARPETAS
# =========================
UPLOAD_FOLDER = "static/uploads"
QR_FOLDER = "static/qr"

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(QR_FOLDER, exist_ok=True)

# =========================
# SQLITE
# =========================
def get_db():
    conn = sqlite3.connect("database.db")
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db()
    conn.execute("""
    CREATE TABLE IF NOT EXISTS experiences (
        id TEXT PRIMARY KEY,
        title TEXT,
        description TEXT,
        image TEXT,
        qr TEXT
    )
    """)
    conn.commit()
    conn.close()

init_db()

# =========================
# ROUTES
# =========================
@app.route("/")
def index():
    return render_template("index.html")


# =========================
# UPLOAD
# =========================
@app.route("/upload", methods=["GET", "POST"])
def upload():

    print("\n========================")
    print("🔥 METHOD:", request.method)
    print("========================\n")

    if request.method == "GET":
        print("🟢 GET -> formulario")
        return render_template("upload.html")

    print("🟡 POST -> procesando")

    file = request.files.get("image")
    title = request.form.get("title")
    description = request.form.get("description")

    print("📦 FILE:", file.filename if file else None)
    print("📦 TITLE:", title)
    print("📦 DESCRIPTION:", description)

    if not file or file.filename == "":
        return "No imagen"

    if not title or not description:
        return "Faltan datos"

    uid = str(uuid.uuid4())

    filename = uid + ".jpg"
    filepath = os.path.join(UPLOAD_FOLDER, filename)
    file.save(filepath)

    print("💾 imagen guardada")

    qr_url = request.host_url + "experiencia/" + uid
    qr_name = uid + ".png"
    qrcode.make(qr_url).save(os.path.join(QR_FOLDER, qr_name))

    print("📌 QR creado")

    conn = get_db()
    conn.execute("""
        INSERT INTO experiences (id, title, description, image, qr)
        VALUES (?, ?, ?, ?, ?)
    """, (uid, title, description, filename, qr_name))
    conn.commit()
    conn.close()

    print("🗄️ SQLite OK")

    # =========================
    # EMBEDDINGS SUPABASE
    # =========================
    try:
        text = f"{title} {description}"
        embedding = generar_embedding(text)

        if hasattr(embedding, "tolist"):
            embedding = embedding.tolist()

        print("🚀 enviando a supabase...")

        supabase.table("aria_embeddings").insert({
            "origen": "experiencia",
            "contenido": text,
            "embedding": embedding
        }).execute()

        print("✅ embedding guardado")

    except Exception as e:
        print("❌ ERROR SUPABASE:", e)

    return redirect("/galeria", code=303)


# =========================
# GALERIA
# =========================
@app.route("/galeria")
def galeria():
    conn = get_db()
    data = conn.execute("SELECT * FROM experiences").fetchall()
    conn.close()
    return render_template("galeria.html", data=data)


# =========================
# EXPERIENCIA
# =========================
@app.route("/experiencia/<id>")
def experiencia(id):
    conn = get_db()
    item = conn.execute("SELECT * FROM experiences WHERE id=?", (id,)).fetchone()
    conn.close()

    if not item:
        return "No existe"

    return render_template("experiencia.html", item=item)


# =========================
# CHAT IA (MEMORIA)
# =========================
@app.route("/chat", methods=["GET", "POST"])
def chat():

    if request.method == "GET":
        return render_template("chat.html")

    message = request.form.get("message")

    embedding = generar_embedding(message)

    if hasattr(embedding, "tolist"):
        embedding = embedding.tolist()

    response = supabase.rpc(
        "match_documents",
        {
            "query_embedding": embedding,
            "match_threshold": 0.3,
            "match_count": 5
        }
    ).execute()

    results = response.data or []

    contexto = "\n".join([
        f"- {r['contenido']} ({r['origen']})"
        for r in results
    ])

    if contexto:
        answer = f"🧠 Encontré esto:\n\n{contexto}"
    else:
        answer = "No encontré información relacionada."

    return render_template("chat.html", answer=answer, message=message)


# =========================
# IA SEARCH
# =========================
@app.route("/buscar_ia", methods=["GET", "POST"])
def buscar_ia():

    if request.method == "GET":
        return render_template("buscar_ia.html")

    query = request.form.get("query")

    embedding = generar_embedding(query)

    if hasattr(embedding, "tolist"):
        embedding = embedding.tolist()

    response = supabase.rpc(
        "match_documents",
        {
            "query_embedding": embedding,
            "match_threshold": 0.3,
            "match_count": 5
        }
    ).execute()

    return render_template("resultados_ia.html", resultados=response.data)


# =========================
# RUN
# =========================
if __name__ == "__main__":
    app.run(debug=True)