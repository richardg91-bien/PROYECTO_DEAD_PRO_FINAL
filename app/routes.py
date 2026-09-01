"""Rutas principales de la aplicación"""

from flask import Blueprint, render_template, request, redirect, current_app, jsonify
import uuid
import os
from dotenv import load_dotenv
from app.services.vision_service import describir_imagen

from app.auth import login_required
from app.services.emotion_service import detectar_emocion
from app.services.memory_service import (
    guardar_memoria,
    obtener_memorias_personaje,
    construir_contexto_persona,
    construir_prompt_memorial,
    construir_url_avatar,
    obtener_estado_avatar,
)
from app.services.validation import (
    validar_archivo_imagen, validar_form_upload, validar_mensaje_chat
)
from app.services.upload_service import guardar_imagen, generar_qr
from app.ia_service import generar_embedding
from app.voz_service import generar_audio

load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), "..", ".env"), override=False)

# 🔥 MODELO CENTRALIZADO
DEFAULT_MODEL = "llama-3.1-8b-instant"
MODEL_NAME = os.getenv("MODEL_NAME", DEFAULT_MODEL)
MODEL_FALLBACKS = [
    os.getenv("MODEL_NAME", DEFAULT_MODEL),
    "llama-3.1-8b-instant",
    "llama-3.3-70b-versatile",
]

main = Blueprint('main', __name__)


def obtener_respuesta_ia(client, mensaje, modelo_inicial=None):
    """Intenta responder con un modelo principal y hace fallback a modelos compatibles."""
    modelos = []
    if modelo_inicial:
        modelos.append(modelo_inicial)
    modelos.extend([m for m in MODEL_FALLBACKS if m and m not in modelos])

    ultimo_error = None

    for modelo in modelos:
        try:
            r = client.chat.completions.create(
                model=modelo,
                messages=[{"role": "user", "content": mensaje}]
            )
            return r.choices[0].message.content.strip(), modelo
        except Exception as e:
            ultimo_error = e
            mensaje_error = str(e).lower()
            codigo_error = getattr(e, "code", None)
            status_code = getattr(e, "status_code", None)
            cuerpo_error = getattr(e, "body", None)
            cuerpo_error_str = str(cuerpo_error).lower() if cuerpo_error is not None else ""

            if (
                "model_not_found" in mensaje_error
                or "does not exist" in mensaje_error
                or codigo_error == "model_not_found"
                or status_code == 404
                or "model_not_found" in cuerpo_error_str
            ):
                continue
            raise

    if ultimo_error is not None:
        raise ultimo_error
    raise RuntimeError("No se pudo obtener respuesta de IA")

# =========================
# DEBUG
@main.route("/debug")
def debug():
    return {
        "supabase": hasattr(current_app, "supabase"),
        "openai": hasattr(current_app, "openai_client")
    }

# =========================
# HOME
@main.route("/")
def index():
    return render_template("index.html")

# =========================
# API TEST
@main.route("/api/test")
def api_test():
    return jsonify({
        "status": "ok",
        "mensaje": "Proyecto Dead conectado correctamente"
    })


@main.route("/health")
def health():
    return jsonify({
        "status": "ok",
        "service": "dead-pro",
        "environment": current_app.config.get("ENV", "development")
    })

# =========================
# UPLOAD
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

        # Inserta la experiencia primero sin descripción IA
        current_app.supabase.table("experiences").insert({
            "id": uid,
            "persona": persona,
            "title": title,
            "description": description,
            "image": filename,
            "qr": qr_name
        }).execute()

        # ===============================
        # Análisis de imagen usando visión IA
        # ===============================
        descripcion_ia = None
        try:
            descripcion_ia = describir_imagen(filename)  # Ruta o URL accesible
            current_app.supabase.table("experiences").update({
                "ai_description": descripcion_ia
            }).eq("id", uid).execute()

            emb = generar_embedding(descripcion_ia)
            guardar_memoria(persona, descripcion_ia, emb, tipo='experiencia')

        except Exception as e:
            print(f"⚠️ Error en análisis de imagen: {e}")

        # También guardar la memoria del texto base (title + desc)
        try:
            texto = f"{persona} | {title} | {description}"
            emb = generar_embedding(texto)
            guardar_memoria(persona, texto, emb, tipo='experiencia')

            perfil_inicial = construir_perfil_inicial(persona, descripcion_ia, title, description)
            emb_perfil = generar_embedding(perfil_inicial)
            guardar_memoria(persona, perfil_inicial, emb_perfil, tipo='experiencia')
        except Exception as e:
            print(f"⚠️ Error embedding texto experiencia: {e}")

        return redirect("/")

    except Exception as e:
        print(f"❌ Error upload: {e}")
        return render_template("upload.html", error="Error al subir experiencia"), 500

# =========================
# API EXPERIENCIAS
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
        respuesta, _ = obtener_respuesta_ia(current_app.openai_client, mensaje, modelo_inicial=MODEL_NAME)
    except Exception as e:
        print(f"❌ Error IA: {e}")
        respuesta = "Error al consultar IA"

    return render_template("chat.html", mensaje=mensaje, respuesta=respuesta)

# =========================
# CHAT PERSONA
@main.route("/chat_persona/<nombre>", methods=["GET", "POST"])
@login_required
def chat_persona(nombre, current_user=None):
    if request.method == "GET":
        return render_template("chat_persona.html", persona=nombre)

    if not current_app.openai_client:
        return render_template("chat_persona.html", persona=nombre, error="IA no disponible")

    msg = request.form.get("message", "").strip()

    valido, error = validar_mensaje_chat(msg)
    if not valido:
        return render_template("chat_persona.html", persona=nombre, error=error), 400

    emocion = detectar_emocion(msg)

    perfil_texto = request.form.get("perfil", "")

    try:
        emb = generar_embedding(msg)
        if hasattr(emb, "tolist"):
            emb = emb.tolist()

        resultados = obtener_memorias_personaje(nombre, emb)
        contexto = construir_contexto_persona(nombre, resultados, perfil_texto or f"{nombre} es una persona interesante y expresiva")

    except Exception as e:
        print(f"⚠️ Error embedding: {e}")
        contexto = construir_contexto_persona(nombre, [], perfil_texto or f"{nombre} es una persona interesante y expresiva")

    prompt = construir_prompt_memorial(
        nombre,
        contexto,
        msg,
        emocion,
    )

    respuesta = "No pude responder."
    audio_path = None

    try:
        respuesta, _ = obtener_respuesta_ia(current_app.openai_client, prompt, modelo_inicial=MODEL_NAME)
    except Exception as e:
        print(f"❌ Error IA persona: {e}")

    try:
        memoria_texto = f"U:{msg} | R:{respuesta}"
        emb_respuesta = generar_embedding(memoria_texto)
        guardar_memoria(nombre, memoria_texto, emb_respuesta, tipo='conversacion')
    except Exception as e:
        print(f"⚠️ Error memoria: {e}")

    try:
        audio_path = generar_audio(respuesta, emocion=emocion)
    except Exception as e:
        print(f"⚠️ Error audio: {e}")

    avatar = construir_url_avatar(None)
    try:
        avatar = construir_url_avatar(filename)
    except Exception:
        avatar = construir_url_avatar(None)

    return render_template(
        "chat_persona.html",
        persona=nombre,
        respuesta=respuesta,
        audio=audio_path,
        message=msg,
        avatar=avatar,
        avatar_state=obtener_estado_avatar(emocion),
    )

# =========================
# ADMIN
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
# ERRORES
@main.errorhandler(404)
def not_found(error):
    return render_template("error.html", message="Página no encontrada"), 404


@main.errorhandler(500)
def internal_error(error):
    return render_template("error.html", message="Error interno del servidor"), 500

# =========================
# API CHAT PERSONA (JSON)
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

    respuesta = "No pude responder."
    audio_path = None

    try:
        respuesta, _ = obtener_respuesta_ia(current_app.openai_client, msg, modelo_inicial=MODEL_NAME)
    except Exception as e:
        print(f"❌ Error IA: {e}")
        return jsonify({"error": str(e)}), 500

    try:
        audio_path = generar_audio(respuesta, emocion=emocion)
    except Exception as e:
        print(f"⚠️ Error audio API: {e}")

    return jsonify({
        "respuesta": respuesta,
        "emocion": emocion,
        "audio": f"/static/audio/{audio_path}" if audio_path else None,
        "avatar_state": obtener_estado_avatar(emocion),
    })
