"""Rutas principales de la aplicación"""

from flask import Blueprint, render_template, request, redirect, current_app, jsonify
import uuid
import os

from app.auth import login_required
from app.services.emotion_service import detectar_emocion
from app.services.memory_service import guardar_memoria, obtener_memorias_personaje
from app.services.validation import (
    validar_archivo_imagen, validar_form_upload, validar_mensaje_chat
)
from app.services.upload_service import guardar_imagen, generar_qr
from app.ia_service import generar_embedding
from app.voz_service import generar_audio

# 🔥 MODELO CENTRALIZADO
MODEL_NAME = os.getenv("MODEL_NAME", "deepseek-chat")

main = Blueprint('main', __name__)

# =========================
# DEBUG
# =========================
@main.route("/debug")
def debug():
    return {
        "supabase": hasattr(current_app, "supabase"),
        "openai": hasattr(current_app, "openai_client")
    }

# =========================
# HOME
# =========================
@main.route("/")
def index():
    return render_template("index.html")

# =========================
# API TEST
# =========================
@main.route("/api/test")
def api_test():
    return jsonify({
        "status": "ok",
        "mensaje": "Proyecto Dead conectado correctamente"
    })

# =========================
# UPLOAD
# =========================
@main.route("/upload", methods=["GET", "POST"])
@login_required
def upload(current_user=None):
    if request.method == "GET":
        return render_template("upload.html")

    if not hasattr(current_app, "supabase"):
        return "Supabase no configurado", 500

    file = request.files.get("image")
    valido, error = validar_archivo_imagen(file)
    if not valido:
        return render_template("upload.html", error=error), 400

    persona = request.form.get("persona", "").strip()
    title = request.form.get("title", "").strip()
    description = request.form.get("description", "").strip()

    valido, error = validar_form_upload(persona, title, description)
    if not valido:
        return render_template("upload.html", error=error), 400

    try:
        uid = str(uuid.uuid4())

        filename = guardar_imagen(file)

        qr_url = f"{request.host_url.rstrip('/')}/experiencia/{uid}"
        qr_name = generar_qr(qr_url)

        current_app.supabase.table("experiences").insert({
            "id": uid,
            "persona": persona,
            "title": title,
            "description": description,
            "image": filename,
            "qr": qr_name
        }).execute()

        try:
            texto = f"{persona} | {title} | {description}"
            emb = generar_embedding(texto)
            guardar_memoria(persona, texto, emb, tipo='experiencia')
        except Exception as e:
            print(f"⚠️ Error embedding: {e}")

        return redirect("/")

    except Exception as e:
        print(f"❌ Error upload: {e}")
        return render_template("upload.html", error="Error al subir experiencia"), 500

# =========================
# API EXPERIENCIAS
# =========================
@main.route("/api/experiencias")
def api_experiencias():
    try:
        res = current_app.supabase \
            .table("experiences") \
            .select("*") \
            .order("created_at", desc=True) \
            .execute()

        return jsonify(res.data or [])

    except Exception as e:
        print(f"❌ Error supabase: {e}")
        return jsonify({"error": "Error al obtener experiencias"}), 500

# =========================
# API EXPERIENCIA
# =========================
@main.route("/api/experiencia/<id>")
def api_experiencia(id):
    try:
        res = current_app.supabase \
            .table("experiences") \
            .select("*") \
            .eq("id", id) \
            .execute()

        if not res.data:
            return jsonify({"error": "No encontrada"}), 404

        return jsonify(res.data[0])

    except Exception as e:
        print(f"❌ Error detalle: {e}")
        return jsonify({"error": "Error interno"}), 500

# =========================
# CHAT SIMPLE
# =========================
@main.route("/chat", methods=["GET", "POST"])
@login_required
def chat(current_user=None):
    if request.method == "GET":
        return render_template("chat.html")

    if not current_app.openai_client:
        return render_template("chat.html", error="IA no configurada"), 500

    mensaje = request.form.get("message", "").strip()

    valido, error = validar_mensaje_chat(mensaje)
    if not valido:
        return render_template("chat.html", error=error), 400

    try:
        r = current_app.openai_client.chat.completions.create(
            model=MODEL_NAME,
            messages=[{"role": "user", "content": mensaje}]
        )
        respuesta = r.choices[0].message.content

    except Exception as e:
        print(f"❌ Error IA: {e}")
        respuesta = "Error al consultar IA"

    return render_template("chat.html", mensaje=mensaje, respuesta=respuesta)

# =========================
# ADMIN (🔥 faltaba y rompe tests)
# =========================
@main.route("/admin")
@login_required
def admin(current_user=None):
    try:
        res = current_app.supabase \
            .table("aria_embeddings") \
            .select("*") \
            .limit(50) \
            .execute()

        return render_template("admin.html", data=res.data)

    except Exception as e:
        print(f"❌ Error admin: {e}")
        return render_template("admin.html", data=[])

# =========================
# API CHAT PERSONA (JSON)
# =========================
@main.route("/api/chat/<nombre>", methods=["POST"])
@login_required
def api_chat_persona(nombre, current_user=None):

    if not current_app.openai_client:
        return jsonify({"error": "IA no configurada"}), 503

    data = request.get_json(silent=True) or {}
    msg = (data.get("message") or "").strip()
    historial = data.get("historial") or []

    valido, error = validar_mensaje_chat(msg)
    if not valido:
        return jsonify({"error": error}), 400

    emocion = detectar_emocion(msg)

    try:
        r = current_app.openai_client.chat.completions.create(
            model=MODEL_NAME,
            messages=[{"role": "user", "content": msg}]
        )
        respuesta = r.choices[0].message.content.strip()
    except Exception as e:
        print(f"❌ Error IA: {e}")
        return jsonify({"error": str(e)}), 500

    return jsonify({
        "respuesta": respuesta,
        "emocion": emocion
    })