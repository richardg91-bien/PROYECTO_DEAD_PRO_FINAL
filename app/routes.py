from flask import Blueprint, render_template, request, redirect, current_app
import os
import uuid
import sqlite3
import qrcode
from app.ia_service import generar_embedding
from app.voz_service import generar_audio

main = Blueprint('main', __name__)


# =========================
# BASE DE DATOS
# =========================
def get_db():
    conn = sqlite3.connect("database.db")
    conn.row_factory = sqlite3.Row
    return conn


# =========================
# UTILIDADES
# =========================
def detectar_emocion(texto):
    """Detecta emoción basada en palabras clave"""
    t = texto.lower()

    if any(x in t for x in ["triste", "llorar", "extraño", "dolor"]):
        return "triste"
    if any(x in t for x in ["feliz", "alegre", "contento"]):
        return "feliz"
    if any(x in t for x in ["enojado", "bronca", "odio"]):
        return "enojado"
    return "neutral"


def guardar_memoria(persona, contenido, embedding):
    """Guarda memoria en Supabase"""
    try:
        if hasattr(embedding, "tolist"):
            embedding = embedding.tolist()

        current_app.supabase.table("aria_embeddings").insert({
            "persona": persona,
            "contenido": contenido,
            "embedding": embedding
        }).execute()

    except Exception as e:
        print("❌ ERROR memoria:", e)


# =========================
# HOME
# =========================
@main.route("/")
def index():
    return render_template("index.html")


# =========================
# UPLOAD
# =========================
@main.route("/upload", methods=["GET", "POST"])
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

    # Generar QR
    qr_url = f"{request.host_url.rstrip('/')}/experiencia/{uid}"

    qr_name = f"{uid}.png"
    qr_path = os.path.join("static/qr", qr_name)

    qrcode.make(qr_url).save(qr_path)

    # Guardar en DB
    db = get_db()
    db.execute(
        "INSERT INTO experiences VALUES (?,?,?,?,?,?)",
        (uid, persona, title, desc, filename, qr_name)
    )
    db.commit()
    db.close()

    # Guardar embedding inicial
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
@main.route("/galeria")
def galeria():
    db = get_db()
    data = db.execute("SELECT * FROM experiences").fetchall()
    db.close()
    return render_template("galeria.html", data=data)


# =========================
# EXPERIENCIA
# =========================
@main.route("/experiencia/<id>")
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
# CHAT SIMPLE
# =========================
@main.route("/chat", methods=["GET", "POST"])
def chat():

    if request.method == "GET":
        return render_template("chat.html")

    mensaje = request.form.get("message", "")
    respuesta = ""

    if mensaje:
        try:
            r = current_app.openai_client.chat.completions.create(
                model="deepseek-chat",
                messages=[
                    {"role": "user", "content": mensaje}
                ]
            )

            respuesta = r.choices[0].message.content

        except Exception as e:
            print(e)
            respuesta = "Error al consultar IA"

    return render_template(
        "chat.html",
        mensaje=mensaje,
        respuesta=respuesta
    )


# =========================
# BUSCAR CON IA
# =========================
@main.route("/buscar_ia", methods=["GET", "POST"])
def buscar_ia():

    if request.method == "GET":
        return render_template("buscar_ia.html")

    consulta = request.form.get("consulta", "")
    resultado = ""

    if consulta:
        try:
            r = current_app.openai_client.chat.completions.create(
                model="deepseek-chat",
                messages=[
                    {
                        "role": "user",
                        "content": consulta
                    }
                ]
            )

            resultado = r.choices[0].message.content

        except Exception as e:
            print(e)
            resultado = "Error al buscar"

    return render_template(
        "resultados_ia.html",
        consulta=consulta,
        resultado=resultado
    )


# =========================
# CHAT CON PERSONA (MEMORIA VIVA)
# =========================
@main.route("/chat_persona/<nombre>", methods=["GET", "POST"])
def chat_persona(nombre):

    if request.method == "GET":
        return render_template("chat_persona.html", persona=nombre)

    msg = request.form.get("message", "").strip()

    if not msg:
        return render_template("chat_persona.html", persona=nombre)

    emocion = detectar_emocion(msg)

    # Generar embedding del mensaje
    emb = generar_embedding(msg)
    if hasattr(emb, "tolist"):
        emb = emb.tolist()

    # Buscar memoria semántica
    response = current_app.supabase.rpc("match_documents", {
        "query_embedding": emb,
        "match_threshold": 0.3,
        "match_count": 5
    }).execute()

    resultados = response.data or []

    contexto = "\n".join([
        r.get("contenido", "") for r in resultados
    ])[:2000]

    # Crear prompt con contexto
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
        r = current_app.openai_client.chat.completions.create(
            model="deepseek-chat",
            messages=[{"role": "user", "content": prompt}]
        )

        respuesta = r.choices[0].message.content.strip()

    except Exception as e:
        print("❌ ERROR IA:", e)
        respuesta = "No pude responder ahora."

    # Guardar memoria evolutiva
    try:
        memoria_texto = f"U:{msg} | R:{respuesta}"
        guardar_memoria(nombre, memoria_texto, generar_embedding(memoria_texto))
    except Exception as e:
        print("❌ ERROR memoria:", e)

    # Generar audio
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
@main.route("/admin")
def admin():
    res = current_app.supabase.table("aria_embeddings").select("*").limit(50).execute()
    return render_template("admin.html", data=res.data)
