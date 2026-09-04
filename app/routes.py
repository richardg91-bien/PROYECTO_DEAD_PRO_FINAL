"""Rutas principales de la aplicación."""

import re
import unicodedata
import uuid

from flask import Blueprint, render_template, request, redirect, current_app, jsonify

from app.auth import login_required
from app.services.emotion_service import detectar_emocion
from app.services.memory_service import guardar_memoria, obtener_memorias_personaje
from app.services.validation import validar_archivo_imagen, validar_form_upload, validar_mensaje_chat
from app.services.upload_service import guardar_imagen, generar_qr
from app.ia_service import generar_embedding
from app.voz_service import generar_audio

main = Blueprint('main', __name__)


def _slugify(value):
    value = unicodedata.normalize("NFD", str(value or ""))
    value = "".join(ch for ch in value if unicodedata.category(ch) != "Mn")
    value = re.sub(r"[^a-zA-Z0-9]+", "-", value).strip("-").lower()
    return value[:120]


@main.route("/debug")
def debug():
    return {"supabase": hasattr(current_app, "supabase"), "openai": hasattr(current_app, "openai_client")}


@main.route("/")
def index():
    return render_template("index.html")


@main.route("/api/test")
def api_test():
    return jsonify({"status": "ok", "mensaje": "Proyecto Dead conectado correctamente"})


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

    # PERSONA es ahora la identidad canónica. El nombre queda únicamente
    # como compatibilidad para formularios/enlaces legacy.
    persona_id = (request.form.get("persona_id") or "").strip()
    persona_nombre = (request.form.get("persona") or "").strip()
    title = request.form.get("title", "").strip()
    description = request.form.get("description", "").strip()

    persona = None
    if persona_id:
        try:
            persona_response = (current_app.supabase.table("personas")
                .select("id,owner_id,nombre,slug")
                .eq("id", persona_id)
                .eq("owner_id", str(current_user.id))
                .limit(1).execute())
            persona = persona_response.data[0] if persona_response.data else None
        except Exception as exc:
            print(f"❌ Error buscando persona: {exc}")
            return render_template("upload.html", error="No se pudo validar la persona"), 500
        if not persona:
            return render_template("upload.html", error="La persona seleccionada no existe"), 404
    else:
        # Compatibilidad: los formularios antiguos pueden enviar solo nombre.
        # Para lo nuevo, el frontend enviará siempre persona_id.
        if not persona_nombre:
            return render_template("upload.html", error="Seleccioná una persona"), 400
        slug = _slugify(persona_nombre)
        try:
            existing = (current_app.supabase.table("personas")
                .select("id,owner_id,nombre,slug")
                .eq("owner_id", str(current_user.id))
                .eq("slug", slug).limit(1).execute())
            persona = existing.data[0] if existing.data else None
            if not persona:
                created = (current_app.supabase.table("personas").insert({
                    "owner_id": str(current_user.id),
                    "nombre": persona_nombre,
                    "slug": slug,
                    "visibilidad": "publica",
                }).execute())
                if not created.data:
                    return render_template("upload.html", error="No se pudo crear la persona"), 500
                persona = created.data[0]
                try:
                    qr_name = generar_qr(f"{request.host_url.rstrip('/')}/p/{persona['id']}")
                    current_app.supabase.table("personas").update({"qr": qr_name}).eq("id", persona["id"]).execute()
                except Exception as qr_exc:
                    print(f"⚠️ Error QR persona: {qr_exc}")
        except Exception as exc:
            print(f"❌ Error resolviendo persona legacy: {exc}")
            return render_template("upload.html", error="No se pudo resolver la persona"), 500

    persona_nombre = persona["nombre"]
    valido, error = validar_form_upload(persona_nombre, title, description)
    if not valido:
        return render_template("upload.html", error=error), 400

    try:
        uid = str(uuid.uuid4())
        filename = guardar_imagen(file)

        # QR de EXPERIENCIA: se conserva exactamente para no romper QR históricos.
        old_qr_url = f"{request.host_url.rstrip('/')}/experiencia/{uid}"
        old_qr_name = generar_qr(old_qr_url)

        current_app.supabase.table("experiences").insert({
            "id": uid,
            "persona_id": persona["id"],
            "persona": persona_nombre,
            "title": title,
            "description": description,
            "image": filename,
            "qr": old_qr_name,
        }).execute()

        # La memoria nueva queda vinculada a persona_id. El guardado legacy
        # por nombre se conserva temporalmente para no romper el sistema anterior.
        try:
            texto = f"{persona_nombre} | {title} | {description}"
            emb = generar_embedding(texto)
            if hasattr(emb, "tolist"):
                emb = emb.tolist()
            from app.services.persona_memory_service import guardar_memoria_persona
            guardar_memoria_persona(persona["id"], texto, emb, tipo="experiencia", origen="upload")
        except Exception as e:
            print(f"⚠️ Error memoria canónica: {e}")

        try:
            texto_legacy = f"{persona_nombre} | {title} | {description}"
            emb_legacy = generar_embedding(texto_legacy)
            guardar_memoria(persona_nombre, texto_legacy, emb_legacy)
        except Exception as e:
            print(f"⚠️ Error embedding legacy: {e}")

        return redirect("/")
    except Exception as e:
        print(f"❌ Error upload: {e}")
        return render_template("upload.html", error="Error al subir experiencia"), 500


@main.route("/api/experiencias")
def api_experiencias():
    try:
        res = current_app.supabase.table("experiences").select("*").order("created_at", desc=True).execute()
        return jsonify(res.data or [])
    except Exception as e:
        print(f"❌ Error supabase: {e}")
        return jsonify({"error": "Error al obtener experiencias"}), 500


@main.route("/api/experiencia/<id>")
def api_experiencia(id):
    try:
        res = current_app.supabase.table("experiences").select("*").eq("id", id).execute()
        if not res.data:
            return jsonify({"error": "No encontrada"}), 404
        return jsonify(res.data[0])
    except Exception as e:
        print(f"❌ Error detalle: {e}")
        return jsonify({"error": "Error interno"}), 500


# LEGACY EXPERIENCE: conserva los QR y enlaces históricos /experiencia/<id>.
@main.route("/experiencia/<id>")
def experiencia_legacy(id):
    try:
        res = current_app.supabase.table("experiences").select("*").eq("id", id).limit(1).execute()
        if not res.data:
            return render_template("error.html", message="Experiencia no encontrada"), 404
        return render_template("experiencia.html", item=res.data[0])
    except Exception as e:
        print(f"❌ Error experiencia legacy: {e}")
        return render_template("error.html", message="Error interno del servidor"), 500


# LEGACY PERSONA: conserva el acceso por nombre usado por los enlaces antiguos.
@main.route("/persona/<nombre>")
def persona_legacy(nombre):
    try:
        res = (current_app.supabase.table("experiences")
               .select("*").eq("persona", nombre)
               .order("created_at", desc=True).execute())
        return render_template("persona.html", persona=nombre, recuerdos=res.data or [])
    except Exception as e:
        print(f"❌ Error persona legacy: {e}")
        return render_template("error.html", message="Error interno del servidor"), 500


# LEGACY CHAT: se mantienen para compatibilidad con usuarios y enlaces existentes.
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
        r = current_app.openai_client.chat.completions.create(model="llama-3.1-8b-instant", messages=[{"role": "user", "content": mensaje}])
        respuesta = r.choices[0].message.content
    except Exception as e:
        print(f"❌ Error IA: {e}")
        respuesta = "Error al consultar IA"
    return render_template("chat.html", mensaje=mensaje, respuesta=respuesta)


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
    contexto = ""
    try:
        emb = generar_embedding(msg)
        if hasattr(emb, "tolist"):
            emb = emb.tolist()
        resultados = obtener_memorias_personaje(nombre, emb)
        contexto = "\n".join([r.get("contenido", "") for r in resultados])[:2000]
    except Exception as e:
        print(f"⚠️ Error embedding: {e}")
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
    respuesta = "No pude responder."
    audio_path = None
    try:
        r = current_app.openai_client.chat.completions.create(model="llama-3.1-8b-instant", messages=[{"role": "user", "content": prompt}])
        respuesta = r.choices[0].message.content.strip()
    except Exception as e:
        print(f"❌ Error IA persona: {e}")
    try:
        memoria_texto = f"U:{msg} | R:{respuesta}"
        emb_respuesta = generar_embedding(memoria_texto)
        guardar_memoria(nombre, memoria_texto, emb_respuesta)
    except Exception as e:
        print(f"⚠️ Error memoria: {e}")
    try:
        audio_path = generar_audio(respuesta)
    except Exception as e:
        print(f"⚠️ Error audio: {e}")
    return render_template("chat_persona.html", persona=nombre, respuesta=respuesta, audio=audio_path, message=msg)


@main.route("/api/chat/<nombre>", methods=["POST"])
@login_required
def api_chat_persona(nombre, current_user=None):
    if not current_app.openai_client:
        return jsonify({"error": "IA no configurada en el servidor"}), 503
    data = request.get_json(silent=True) or {}
    msg = (data.get("message") or "").strip()
    historial = data.get("historial") or []
    valido, error = validar_mensaje_chat(msg)
    if not valido:
        return jsonify({"error": error}), 400
    emocion = detectar_emocion(msg)
    contexto = ""
    try:
        emb = generar_embedding(msg)
        resultados = obtener_memorias_personaje(nombre, emb)
        contexto = "\n".join([r.get("contenido", "") for r in resultados])[:2000]
    except Exception as e:
        print(f"⚠️ Error embedding: {e}")
    system_prompt = f"""Sos {nombre}, una persona real que el usuario conoció y extraña.
Estado emocional del usuario ahora: {emocion}.
Recuerdos y memorias tuyas:
{contexto if contexto else "(sin recuerdos previos aún)"}

Respondé de forma humana, emocional y natural. Máximo 3 oraciones.
No digas que sos IA. No rompas el personaje."""
    messages = [{"role": "system", "content": system_prompt}]
    for turno in historial[-10:]:
        if turno.get("rol") == "usuario":
            messages.append({"role": "user", "content": turno.get("texto", "")})
        elif turno.get("rol") == "ia":
            messages.append({"role": "assistant", "content": turno.get("texto", "")})
    messages.append({"role": "user", "content": msg})
    try:
        r = current_app.openai_client.chat.completions.create(model="llama-3.1-8b-instant", messages=messages, max_tokens=300)
        respuesta = r.choices[0].message.content.strip()
    except Exception as e:
        print(f"❌ Error IA: {e}")
        return jsonify({"error": f"Error al consultar la IA: {str(e)}"}), 500
    try:
        memoria_texto = f"U: {msg} | R: {respuesta}"
        emb_nuevo = generar_embedding(memoria_texto)
        guardar_memoria(nombre, memoria_texto, emb_nuevo)
    except Exception as e:
        print(f"⚠️ Error guardando memoria: {e}")
    audio_nombre = None
    try:
        audio_nombre = generar_audio(respuesta)
    except Exception as e:
        print(f"⚠️ Error audio: {e}")
    return jsonify({"respuesta": respuesta, "emocion": emocion, "audio": f"/static/audio/{audio_nombre}" if audio_nombre else None})


@main.route("/admin")
@login_required
def admin(current_user=None):
    try:
        res = current_app.supabase.table("aria_embeddings").select("*").limit(50).execute()
        return render_template("admin.html", data=res.data)
    except Exception as e:
        print(f"❌ Error admin: {e}")
        return render_template("admin.html", data=[])


@main.errorhandler(404)
def not_found(error):
    return render_template("error.html", message="Página no encontrada"), 404


@main.errorhandler(500)
def internal_error(error):
    return render_template("error.html", message="Error interno del servidor"), 500
