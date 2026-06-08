"""Rutas principales de la aplicación"""

from flask import Blueprint, render_template, request, redirect, current_app, jsonify
import uuid

from app import get_db
from app.exceptions import ValidationError, NotFoundError, IAServiceError, FileUploadError
from app.services.emotion_service import detectar_emocion
from app.services.memory_service import guardar_memoria, obtener_memorias_personaje
from app.services.validation import (
    validar_archivo_imagen, validar_form_upload, validar_mensaje_chat
)
from app.services.upload_service import guardar_imagen, generar_qr
from app.ia_service import generar_embedding
from app.voz_service import generar_audio

main = Blueprint('main', __name__)


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

    # Validar archivo
    file = request.files.get("image")
    valido, error = validar_archivo_imagen(file)
    if not valido:
        return render_template("upload.html", error=error), 400

    # Validar formulario
    persona = request.form.get("persona", "").strip()
    title = request.form.get("title", "").strip()
    description = request.form.get("description", "").strip()

    valido, error = validar_form_upload(persona, title, description)
    if not valido:
        return render_template("upload.html", error=error), 400

    try:
        uid = str(uuid.uuid4())

        # Guardar imagen
        filename = guardar_imagen(file)

        # Generar QR
        qr_url = f"{request.host_url.rstrip('/')}/experiencia/{uid}"
        qr_name = generar_qr(qr_url)

        # Guardar en BD
        db = get_db()
        db.execute(
            "INSERT INTO experiences VALUES (?,?,?,?,?,?,CURRENT_TIMESTAMP)",
            (uid, persona, title, description, filename, qr_name)
        )
        db.commit()
        db.close()

        # Guardar embedding inicial
        try:
            texto = f"{persona} | {title} | {description}"
            emb = generar_embedding(texto)
            guardar_memoria(persona, texto, emb)
        except Exception as e:
            print(f"⚠️ Error embedding: {e}")

        return redirect("/galeria")

    except Exception as e:
        print(f"❌ Error upload: {e}")
        return render_template("upload.html", error="Error al procesar upload"), 500


# =========================
# GALERIA
# =========================
@main.route("/galeria")
def galeria():
    db = get_db()
    data = db.execute("SELECT * FROM experiences ORDER BY created_at DESC").fetchall()
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
        return render_template("error.html", message="Experiencia no encontrada"), 404

    return render_template("experiencia.html", item=item)


# =========================
# CHAT SIMPLE
# =========================
@main.route("/chat", methods=["GET", "POST"])
def chat():
    if request.method == "GET":
        return render_template("chat.html")

    mensaje = request.form.get("message", "").strip()
    respuesta = ""

    valido, error = validar_mensaje_chat(mensaje)
    if not valido:
        return render_template("chat.html", error=error), 400

    try:
        r = current_app.openai_client.chat.completions.create(
            model="deepseek-chat",
            messages=[{"role": "user", "content": mensaje}]
        )
        respuesta = r.choices[0].message.content

    except Exception as e:
        print(f"❌ Error IA chat: {e}")
        respuesta = "Error al consultar IA"

    return render_template("chat.html", mensaje=mensaje, respuesta=respuesta)


# =========================
# BUSCAR CON IA
# =========================
@main.route("/buscar_ia", methods=["GET", "POST"])
def buscar_ia():
    if request.method == "GET":
        return render_template("buscar_ia.html")

    consulta = request.form.get("consulta", "").strip()
    resultado = ""

    valido, error = validar_mensaje_chat(consulta)
    if not valido:
        return render_template("buscar_ia.html", error=error), 400

    try:
        r = current_app.openai_client.chat.completions.create(
            model="deepseek-chat",
            messages=[{"role": "user", "content": consulta}]
        )
        resultado = r.choices[0].message.content

    except Exception as e:
        print(f"❌ Error IA buscar: {e}")
        resultado = "Error al buscar"

    return render_template("resultados_ia.html", consulta=consulta, resultado=resultado)


# =========================
# CHAT CON PERSONA (MEMORIA VIVA)
# =========================
@main.route("/chat_persona/<nombre>", methods=["GET", "POST"])
def chat_persona(nombre):
    if request.method == "GET":
        return render_template("chat_persona.html", persona=nombre)

    msg = request.form.get("message", "").strip()

    valido, error = validar_mensaje_chat(msg)
    if not valido:
        return render_template("chat_persona.html", persona=nombre, error=error), 400

    emocion = detectar_emocion(msg)

    # Generar embedding del mensaje
    try:
        emb = generar_embedding(msg)
        if hasattr(emb, "tolist"):
            emb = emb.tolist()

        # Buscar memoria semántica
        resultados = obtener_memorias_personaje(nombre, emb)
        contexto = "\n".join([r.get("contenido", "") for r in resultados])[:2000]

    except Exception as e:
        print(f"⚠️ Error embedding: {e}")
        contexto = ""

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

    respuesta = "No pude responder ahora."
    audio_path = None

    try:
        r = current_app.openai_client.chat.completions.create(
            model="deepseek-chat",
            messages=[{"role": "user", "content": prompt}]
        )
        respuesta = r.choices[0].message.content.strip()

    except Exception as e:
        print(f"❌ ERROR IA: {e}")

    # Guardar memoria evolutiva
    try:
        memoria_texto = f"U:{msg} | R:{respuesta}"
        emb_respuesta = generar_embedding(memoria_texto)
        guardar_memoria(nombre, memoria_texto, emb_respuesta)
    except Exception as e:
        print(f"⚠️ Error guardar memoria: {e}")

    # Generar audio
    try:
        audio_path = generar_audio(respuesta)
    except Exception as e:
        print(f"⚠️ Error generando audio: {e}")

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
    try:
        res = current_app.supabase.table("aria_embeddings").select("*").limit(50).execute()
        return render_template("admin.html", data=res.data)
    except Exception as e:
        print(f"❌ Error admin: {e}")
        return render_template("admin.html", data=[])


# =========================
# ERROR HANDLERS
# =========================
@main.errorhandler(404)
def not_found(error):
    return render_template("error.html", message="Página no encontrada"), 404


@main.errorhandler(500)
def internal_error(error):
    return render_template("error.html", message="Error interno del servidor"), 500
