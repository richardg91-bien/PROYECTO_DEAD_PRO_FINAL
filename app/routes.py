"""Rutas principales de la aplicación"""

from flask import Blueprint, render_template, request, redirect, current_app, jsonify
from openai import OpenAI
import uuid
import os
from dotenv import load_dotenv
from app.services.vision_service import describir_imagen  # noqa: F401 (mantenido por compatibilidad)

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
from app.services.experience_analysis_service import analizar_y_guardar_experiencia
from app.ia_service import generar_embedding
from app.voz_service import generar_audio

load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), "..", ".env"), override=False)

# 🔥 MODELO CENTRALIZADO (Groq; la IA propia local es la principal — esto es solo respaldo)
DEFAULT_MODEL = "llama-3.1-8b-instant"
MODEL_NAME = os.getenv("MODEL_NAME", DEFAULT_MODEL)
MODEL_FALLBACKS = [
    os.getenv("MODEL_NAME", DEFAULT_MODEL),
    "llama-3.1-8b-instant",
    "openai/gpt-oss-120b",
]

main = Blueprint('main', __name__)


def _limpiar_archivos_huerfanos(filename, qr_name):
    """Elimina la imagen y el QR subidos si la experiencia no se guardó."""
    for carpeta, nombre in (("static/uploads", filename), ("static/qr", qr_name)):
        if not nombre:
            continue
        ruta = os.path.join(carpeta, nombre)
        try:
            if os.path.exists(ruta):
                os.remove(ruta)
        except OSError as e:
            print(f"⚠️ No se pudo eliminar archivo huérfano {ruta}: {e}")


def responder_con_ia(client, prompt, respuesta_por_defecto="No pude responder.", propagar_error=False):
    """Obtiene respuesta de la IA con logging de errores.

    Returns:
        str: La respuesta de la IA, o el valor por defecto si falló.

    Raises:
        Exception: Solo si propagar_error es True.
    """
    try:
        respuesta, _ = obtener_respuesta_ia(client, prompt, modelo_inicial=MODEL_NAME)
        return respuesta
    except Exception as e:
        print(f"❌ Error IA: {e}")
        if propagar_error:
            raise
        return respuesta_por_defecto


def generar_audio_seguro(respuesta, emocion, persona=None):
    """Genera audio de la respuesta, devolviendo None si falla.

    La voz se modula según la afinidad acumulada con la persona (evolución
    de la IA propia); si no se puede leer, usa la voz base sin alterar.
    """
    afinidad = None
    if persona:
        try:
            from app.ia_core.evolucion import cargar_estado
            afinidad = cargar_estado(persona).afinidad
        except Exception as e:
            print(f"⚠️ Voz: sin afinidad para {persona}: {e}")
    try:
        return generar_audio(respuesta, emocion=emocion, afinidad=afinidad)
    except Exception as e:
        print(f"⚠️ Error audio: {e}")
        return None


def obtener_respuesta_ia(client: "OpenAI", mensaje: str, modelo_inicial: str | None = None) -> tuple[str, str]:
    """Intenta responder con un modelo principal y hace fallback a modelos compatibles.

    Args:
        client: Cliente de OpenAI/Groq ya inicializado (openai.OpenAI).
        mensaje: Texto del mensaje del usuario a enviar al modelo.
        modelo_inicial: Modelo preferido; si es None se usan solo los
            fallbacks de MODEL_FALLBACKS.

    Returns:
        tuple[str, str]: (respuesta_texto, nombre_del_modelo_usado).

    Raises:
        Exception: Los errores de modelo no encontrado (404 / "model_not_found")
            son absorbidos y disparan el fallback al siguiente modelo. Cualquier
            otro error (rate limit, autenticación, red, etc.) se propaga
            inmediatamente al llamador. Si todos los modelos fallan con error
            de modelo no encontrado, se relanza el último error; si la lista de
            modelos queda vacía, se lanza RuntimeError.
    """
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
        "openai": hasattr(current_app, "openai_client"),
        "ia_propia": True
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

    filename = None
    qr_name = None
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

        # Análisis de imagen y guardado de memorias (servicio dedicado)
        analizar_y_guardar_experiencia(persona, title, description, filename, uid)

        return redirect("/")

    except Exception as e:
        print(f"❌ Error upload: {e}")
        _limpiar_archivos_huerfanos(filename, qr_name)
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

    respuesta = responder_con_ia(current_app.openai_client, mensaje, respuesta_por_defecto="Error al consultar IA")

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

    respuesta = responder_con_ia(current_app.openai_client, prompt)

    try:
        memoria_texto = f"U:{msg} | R:{respuesta}"
        emb_respuesta = generar_embedding(memoria_texto)
        guardar_memoria(nombre, memoria_texto, emb_respuesta, tipo='conversacion')
    except Exception as e:
        print(f"⚠️ Error memoria: {e}")

    audio_path = generar_audio_seguro(respuesta, emocion, persona=nombre)

    # Usa la imagen de la experiencia almacenada para esta persona, si existe
    avatar = construir_url_avatar(None)
    try:
        if hasattr(current_app, "supabase"):
            res_exp = current_app.supabase \
                .table("experiences") \
                .select("image") \
                .eq("persona", nombre) \
                .order("created_at", desc=True) \
                .limit(1) \
                .execute()
            if res_exp.data and res_exp.data[0].get("image"):
                avatar = construir_url_avatar(res_exp.data[0]["image"])
    except Exception as e:
        print(f"⚠️ Error obteniendo avatar de experiencia: {e}")
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
# API CHAT PERSONA (JSON) — motor de IA propio
@main.route("/api/chat/<nombre>", methods=["POST"])
@login_required
def api_chat_persona(nombre, current_user=None):
    data = request.get_json(silent=True) or {}
    msg = (data.get("message") or "").strip()
    historial = data.get("historial") or []

    valido, error = validar_mensaje_chat(msg)
    if not valido:
        return jsonify({"error": error}), 400

    # Recupera memorias semánticas para dar contexto vivo al motor propio
    memorias = []
    perfil = f"{nombre} es una persona interesante y expresiva"
    try:
        from app.ia_service import generar_embedding
        from app.services.memory_service import obtener_memorias_personaje
        emb = generar_embedding(msg)
        if hasattr(emb, "tolist"):
            emb = emb.tolist()
        memorias = obtener_memorias_personaje(nombre, emb)
    except Exception as e:
        print(f"⚠️ Memorias: {e}")

    # Motor de IA propio (empático, evolutivo, local). Groq solo como respaldo.
    from app.services.ia_propia_service import responder_con_respaldo
    resultado, motor_usado = responder_con_respaldo(
        nombre, msg, historial=historial, memorias=memorias, perfil=perfil
    )

    if not resultado or not resultado.get("respuesta"):
        return jsonify({"error": "IA no disponible en este momento"}), 503

    respuesta = resultado["respuesta"]
    emocion = resultado.get("emocion") or detectar_emocion(msg)

    # Guarda la conversación como memoria para futuras respuestas
    try:
        from app.ia_service import generar_embedding
        from app.services.memory_service import guardar_memoria
        memoria_texto = f"U:{msg} | R:{respuesta}"
        emb_respuesta = generar_embedding(memoria_texto)
        guardar_memoria(nombre, memoria_texto, emb_respuesta, tipo='conversacion')
    except Exception as e:
        print(f"⚠️ Error memoria: {e}")

    audio_path = generar_audio_seguro(respuesta, emocion, persona=nombre)

    return jsonify({
        "respuesta": respuesta,
        "emocion": emocion,
        "audio": f"/static/audio/{audio_path}" if audio_path else None,
        "avatar_state": obtener_estado_avatar(emocion),
        "motor": motor_usado,
        "nivel_ia": resultado.get("nivel"),
        "nombre_nivel": resultado.get("nombre_nivel"),
    })

# =========================
# ESTADO DE EVOLUCIÓN DE LA IA PROPIA
@main.route("/api/ia/estado/<nombre>")
@login_required
def api_ia_estado(nombre, current_user=None):
    """Devuelve cómo ha evolucionado la IA con esta persona."""
    from app.ia_core.evolucion import cargar_estado
    from app.services.ia_propia_service import _cargar_estilo

    estado = cargar_estado(nombre)
    estilo = _cargar_estilo(nombre)

    return jsonify({
        "persona": nombre,
        "evolucion": estado.to_dict(),
        "estilo": estilo,
    })
