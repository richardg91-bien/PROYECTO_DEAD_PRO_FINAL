from flask import Flask, render_template, request, redirect
import os, uuid, sqlite3, qrcode
from dotenv import load_dotenv
from supabase import create_client
from openai import OpenAI

# servicios externos
from voz_service import generar_audio
from app.ia_service import generar_embedding

# =========================
# ENV
# =========================
load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY")

if not all([SUPABASE_URL, SUPABASE_KEY, DEEPSEEK_API_KEY]):
    raise Exception("❌ Faltan variables de entorno (.env)")

client = OpenAI(
    api_key=DEEPSEEK_API_KEY,
    base_url="https://api.deepseek.com"
)

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

# =========================
# APP
# =========================
app = Flask(__name__, template_folder="app/templates")

# =========================
# CARPETAS SEGURAS
# =========================
for folder in ["static/uploads", "static/qr", "static/audio"]:
    os.makedirs(folder, exist_ok=True)

# =========================
# DB
# =========================
def get_db():
    conn = sqlite3.connect("database.db")
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    db = get_db()
    db.execute("""
    CREATE TABLE IF NOT EXISTS experiences (
        id TEXT PRIMARY KEY,
        persona TEXT,
        title TEXT,
        description TEXT,
        image TEXT,
        qr TEXT
    )
    """)
    db.commit()
    db.close()

init_db()

# =========================
# UTILIDADES
# =========================
def detectar_emocion(texto):
    t = texto.lower()

    if any(x in t for x in ["triste", "llorar", "extraño", "dolor"]):
        return "triste"
    if any(x in t for x in ["feliz", "alegre", "contento"]):
        return "feliz"
    if any(x in t for x in ["enojado", "bronca", "odio"]):
        return "enojado"
    return "neutral"


def guardar_memoria(persona, contenido, embedding):
    try:
        if hasattr(embedding, "tolist"):
            embedding = embedding.tolist()

        supabase.table("aria_embeddings").insert({
            "persona": persona,
            "contenido": contenido,
            "embedding": embedding
        }).execute()

    except Exception as e:
        print("❌ ERROR memoria:", e)


# =========================
# HOME
# =========================
@app.route("/")
def index():
    return render_template("index.html")


# =========================
# UPLOAD (FIX QR CRÍTICO)
# =========================
@app.route("/upload", methods=["GET", "POST"])
def upload():

    if request.method == "GET":
        return render_template("upload.html")

    file = request.files.get("image")
    persona = request.form.get("persona")
    title = request.form.get("title")
    desc = request.form.get("description")

    if not file or not file.filename:
        return "❌ No imagen"

    if not persona or not title or not desc:
        return "❌ Faltan datos"

    uid = str(uuid.uuid4())

    filename = f"{uid}.jpg"
    filepath = os.path.join("static/uploads", filename)

    file.save(filepath)

    # 🔥 FIX CRÍTICO DEL QR (evita Not Found)
    qr_url = f"{request.host_url.rstrip('/')}/experiencia/{uid}"

    qr_name = f"{uid}.png"
    qr_path = os.path.join("static/qr", qr_name)

    qrcode.make(qr_url).save(qr_path)

    # DB
    db = get_db()
    db.execute(
        "INSERT INTO experiences VALUES (?,?,?,?,?,?)",
        (uid, persona, title, desc, filename, qr_name)
    )
    db.commit()
    db.close()

    # MEMORIA INICIAL
    try:
        texto = f"{persona} | {title} | {desc}"
        emb = generar_embedding(texto)
        guardar_memoria(persona, texto, emb)
    except Exception as e:
        print("❌ ERROR embedding:", e)

    return redirect("/galeria")


# =========================
# GALERIA
# =========================
@app.route("/galeria")
def galeria():
    db = get_db()
    data = db.execute("SELECT * FROM experiences").fetchall()
    db.close()
    return render_template("galeria.html", data=data)


# =========================
# EXPERIENCIA (IMPORTANTE)
# =========================
@app.route("/experiencia/<id>")
def experiencia(id):
    db = get_db()
    item = db.execute(
        "SELECT * FROM experiences WHERE id=?",
        (id,)
    ).fetchone()
    db.close()

    if not item:
        return "❌ Experiencia no encontrada"

    return render_template("experiencia.html", item=item)


# =========================
# CHAT PERSONA (MEMORIA VIVA)
# =========================
@app.route("/chat_persona/<nombre>", methods=["GET", "POST"])
def chat_persona(nombre):

    if request.method == "GET":
        return render_template("chat_persona.html", persona=nombre)

    msg = request.form.get("message", "").strip()

    if not msg:
        return render_template("chat_persona.html", persona=nombre)

    emocion = detectar_emocion(msg)

    # embedding usuario
    emb = generar_embedding(msg)
    if hasattr(emb, "tolist"):
        emb = emb.tolist()

    # memoria semántica
    response = supabase.rpc("match_documents", {
        "query_embedding": emb,
        "match_threshold": 0.3,
        "match_count": 5
    }).execute()

    resultados = response.data or []

    contexto = "\n".join([
        r.get("contenido", "") for r in resultados
    ])[:2000]

    # PROMPT REALISTA
    prompt = f"""
Sos {nombre}, una persona real.

Estado emocional del usuario: {emocion}

Recuerdos:
{contexto}

Mensaje del usuario:
{msg}

Respondé de forma humana, emocional y natural.
No digas que sos IA.
"""

    try:
        r = client.chat.completions.create(
            model="deepseek-chat",
            messages=[{"role": "user", "content": prompt}]
        )

        respuesta = r.choices[0].message.content.strip()

    except Exception as e:
        print("❌ ERROR IA:", e)
        respuesta = "No pude responder ahora."

    # MEMORIA EVOLUTIVA
    try:
        memoria_texto = f"U:{msg} | R:{respuesta}"
        guardar_memoria(nombre, memoria_texto, generar_embedding(memoria_texto))
    except Exception as e:
        print("❌ ERROR memoria:", e)

    # AUDIO (externo seguro)
    audio_path = generar_audio(respuesta)

    return render_template(
        "chat_persona.html",
        persona=nombre,
        respuesta=respuesta,
        audio=audio_path,
        message=msg
    )


# =========================
# ADMIN
# =========================
@app.route("/admin")
def admin():
    res = supabase.table("aria_embeddings").select("*").limit(50).execute()
    return render_template("admin.html", data=res.data)


# =========================
# RUN
# =========================
if __name__ == "__main__":
    app.run(debug=True)