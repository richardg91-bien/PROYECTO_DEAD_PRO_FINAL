"""API canónica person-centric de Visión 1."""

import uuid
from flask import Blueprint, current_app, jsonify, request

from app.auth import login_required
from app.character.identity import get_persona_by_id, get_persona_by_slug
from app.character.character_engine import generar_respuesta
from app.character.conversation import crear_conversacion, obtener_conversacion, guardar_mensaje, obtener_mensajes
from app.character.personality import normalizar_personalidad
from app.services.upload_service import generar_qr
from app.services.persona_memory_service import guardar_memoria_persona, obtener_memorias_persona, actualizar_memoria_persona, eliminar_memoria_persona
from app.ia_service import generar_embedding
from app.voice.voice_service import sintetizar_voz

persona_bp = Blueprint("persona", __name__, url_prefix="/api/personas")

PERSONALITY_FIELDS = (
    "traits", "values", "temperament", "communication_style",
    "humor_style", "likes", "dislikes", "behavioral_rules"
)


def _valid_uuid(value):
    try:
        return str(uuid.UUID(str(value)))
    except (ValueError, AttributeError, TypeError):
        return None


def _session_id(value):
    value = str(value or "").strip()
    return value if value and len(value) <= 200 else str(uuid.uuid4())


def _persona_owned(persona_id, current_user):
    response = (current_app.supabase.table("personas").select("id,nombre,slug,owner_id,qr").eq("id", persona_id).eq("owner_id", str(current_user.id)).limit(1).execute())
    return response.data[0] if response.data else None


def _memory_type(value):
    allowed = {"biografia", "experiencia", "familia", "amistad", "trabajo", "gustos", "anecdota", "opinion", "valor", "relacion", "conversacion", "otro"}
    return value if value in allowed else "otro"


def _personality_payload(data):
    """Normaliza la personalidad estructurada sin permitir campos arbitrarios."""
    payload = {}
    for field in PERSONALITY_FIELDS:
        if field not in data:
            continue
        value = data[field]
        if field in ("likes", "dislikes", "behavioral_rules"):
            if not isinstance(value, list):
                raise ValueError(f"{field} debe ser una lista")
            payload[field] = [str(item).strip() for item in value if str(item).strip()][:100]
        else:
            if not isinstance(value, dict):
                raise ValueError(f"{field} debe ser un objeto")
            payload[field] = value
    return payload


def _historial_persistido(conversation_id, session_id):
    """Convierte mensajes persistidos en el formato esperado por el Character Engine.

    El historial del navegador no se usa como fuente de verdad para evitar que el
    cliente pueda inyectar contexto arbitrario en la personalidad conversacional.
    """
    mensajes = obtener_mensajes(conversation_id, limit=20, session_id=session_id)
    historial = []
    for mensaje in mensajes:
        role = mensaje.get("role")
        if role == "visitor":
            role = "user"
        elif role == "persona":
            role = "assistant"
        elif role != "system":
            continue
        content = mensaje.get("content")
        if content:
            historial.append({"role": role, "content": str(content)})
    return historial


@persona_bp.get("")
@login_required
def api_personas(current_user=None):
    try:
        response = (current_app.supabase.table("personas").select("id,owner_id,nombre,slug,bio,fecha_nacimiento,fecha_fallecimiento,lugar_nacimiento,lugar_fallecimiento,foto_principal,visibilidad,qr,created_at,updated_at").eq("owner_id", str(current_user.id)).order("created_at", desc=True).execute())
        return jsonify(response.data or [])
    except Exception as exc:
        print(f"❌ Error listando personas: {exc}"); return jsonify({"error":"No se pudieron cargar las personas"}),500


@persona_bp.get("/<persona_id>")
def api_persona(persona_id):
    persona_id = _valid_uuid(persona_id)
    if not persona_id: return jsonify({"error":"ID de persona inválido"}),400
    try: persona = get_persona_by_id(current_app, persona_id)
    except Exception as exc: print(f"❌ Error persona: {exc}"); return jsonify({"error":"Error interno"}),500
    if not persona: return jsonify({"error":"Persona no encontrada"}),404
    return jsonify(persona)


@persona_bp.put("/<persona_id>")
@login_required
def api_persona_update(persona_id, current_user=None):
    persona_id = _valid_uuid(persona_id)
    if not persona_id: return jsonify({"error":"ID de persona inválido"}),400
    if not _persona_owned(persona_id, current_user): return jsonify({"error":"Persona no encontrada"}),404
    data = request.get_json(silent=True) or {}
    allowed = ["nombre","bio","fecha_nacimiento","fecha_fallecimiento","lugar_nacimiento","lugar_fallecimiento","foto_principal","visibilidad"]
    payload = {k:data[k] for k in allowed if k in data}
    if "nombre" in payload:
        payload["nombre"] = str(payload["nombre"] or "").strip()
        if not payload["nombre"] or len(payload["nombre"]) > 200: return jsonify({"error":"Nombre inválido"}),400
    if "visibilidad" in payload and payload["visibilidad"] not in ("publica","privada"): return jsonify({"error":"Visibilidad inválida"}),400
    try:
        response = current_app.supabase.table("personas").update(payload).eq("id",persona_id).eq("owner_id",str(current_user.id)).execute()
        if not response.data: return jsonify({"error":"No se pudo actualizar la persona"}),500
        return jsonify(response.data[0])
    except Exception as exc:
        print(f"❌ Error actualizando persona: {exc}"); return jsonify({"error":"No se pudo actualizar la identidad"}),500


@persona_bp.get("/<persona_id>/personalidad")
@login_required
def api_persona_personalidad(current_user=None, persona_id=None):
    persona_id = _valid_uuid(persona_id)
    if not persona_id or not _persona_owned(persona_id, current_user):
        return jsonify({"error":"Persona no encontrada"}),404
    try:
        response = (current_app.supabase.table("personalities").select("id,persona_id,traits,values,temperament,communication_style,humor_style,likes,dislikes,behavioral_rules,created_at,updated_at").eq("persona_id", persona_id).limit(1).execute())
        personalidad = response.data[0] if response.data else None
        return jsonify(normalizar_personalidad(personalidad) | ({"id": personalidad["id"], "persona_id": persona_id, "created_at": personalidad.get("created_at"), "updated_at": personalidad.get("updated_at")} if personalidad else {"persona_id": persona_id}))
    except Exception as exc:
        print(f"❌ Error obteniendo personalidad: {exc}"); return jsonify({"error":"No se pudo cargar la personalidad"}),500


@persona_bp.put("/<persona_id>/personalidad")
@login_required
def api_persona_personalidad_update(persona_id, current_user=None):
    persona_id = _valid_uuid(persona_id)
    if not persona_id or not _persona_owned(persona_id, current_user):
        return jsonify({"error":"Persona no encontrada"}),404
    data = request.get_json(silent=True) or {}
    try:
        payload = _personality_payload(data)
    except ValueError as exc:
        return jsonify({"error": str(exc)}),400
    if not payload:
        return jsonify({"error":"No se recibió información de personalidad"}),400
    payload["persona_id"] = persona_id
    try:
        response = current_app.supabase.table("personalities").upsert(payload, on_conflict="persona_id").execute()
        if not response.data:
            return jsonify({"error":"No se pudo guardar la personalidad"}),500
        return jsonify(response.data[0])
    except Exception as exc:
        print(f"❌ Error guardando personalidad: {exc}"); return jsonify({"error":"No se pudo guardar la personalidad"}),500


@persona_bp.get("/<persona_id>/experiencias")
def api_persona_experiencias(persona_id):
    persona_id = _valid_uuid(persona_id)
    if not persona_id: return jsonify({"error":"ID de persona inválido"}),400
    if not get_persona_by_id(current_app, persona_id): return jsonify({"error":"Persona no encontrada"}),404
    try:
        response=(current_app.supabase.table("experiences").select("id,persona_id,title,description,image,created_at,ai_description,qr").eq("persona_id",persona_id).order("created_at",desc=True).execute())
        return jsonify(response.data or [])
    except Exception as exc: print(f"❌ Error experiencias persona: {exc}"); return jsonify({"error":"Error interno"}),500


@persona_bp.get("/<persona_id>/memorias")
@login_required
def api_persona_memorias(persona_id, current_user=None):
    persona_id = _valid_uuid(persona_id)
    if not persona_id or not _persona_owned(persona_id, current_user): return jsonify({"error":"Persona no encontrada"}),404
    return jsonify(obtener_memorias_persona(persona_id, embedding=None, limit=100))


@persona_bp.post("/<persona_id>/memorias")
@login_required
def api_persona_memoria_create(persona_id, current_user=None):
    persona_id = _valid_uuid(persona_id)
    if not persona_id or not _persona_owned(persona_id, current_user): return jsonify({"error":"Persona no encontrada"}),404
    data = request.get_json(silent=True) or {}
    contenido = str(data.get("contenido") or "").strip()
    if not contenido or len(contenido) > 10000: return jsonify({"error":"Contenido de memoria inválido"}),400
    tipo = _memory_type(data.get("tipo", "otro"))
    try:
        importancia = max(1, min(5, int(data.get("importancia", 3))))
        embedding = generar_embedding(contenido)
        memoria = guardar_memoria_persona(persona_id, contenido, embedding, tipo=tipo, origen="manual", importancia=importancia)
        if not memoria: return jsonify({"error":"No se pudo guardar la memoria"}),500
        return jsonify(memoria),201
    except (TypeError, ValueError): return jsonify({"error":"Importancia inválida"}),400
    except Exception as exc: print(f"❌ Error creando memoria: {exc}"); return jsonify({"error":"No se pudo crear la memoria"}),500


@persona_bp.put("/<persona_id>/memorias/<memoria_id>")
@login_required
def api_persona_memoria_update(persona_id, memoria_id, current_user=None):
    persona_id = _valid_uuid(persona_id); memoria_id = _valid_uuid(memoria_id)
    if not persona_id or not memoria_id or not _persona_owned(persona_id, current_user): return jsonify({"error":"Memoria no encontrada"}),404
    data = request.get_json(silent=True) or {}
    tipo = _memory_type(data["tipo"]) if "tipo" in data else None
    try:
        memoria = actualizar_memoria_persona(persona_id, memoria_id, data.get("contenido"), tipo, data.get("importancia"))
        if not memoria: return jsonify({"error":"Memoria no encontrada o sin cambios"}),404
        return jsonify(memoria)
    except (TypeError, ValueError): return jsonify({"error":"Importancia inválida"}),400


@persona_bp.delete("/<persona_id>/memorias/<memoria_id>")
@login_required
def api_persona_memoria_delete(persona_id, memoria_id, current_user=None):
    persona_id = _valid_uuid(persona_id); memoria_id = _valid_uuid(memoria_id)
    if not persona_id or not memoria_id or not _persona_owned(persona_id, current_user): return jsonify({"error":"Memoria no encontrada"}),404
    if not eliminar_memoria_persona(persona_id, memoria_id): return jsonify({"error":"Memoria no encontrada"}),404
    return jsonify({"ok":True,"id":memoria_id})


@persona_bp.get("/slug/<slug>")
def api_persona_slug(slug):
    if not slug or len(slug)>120: return jsonify({"error":"Slug inválido"}),400
    try: persona=get_persona_by_slug(current_app,slug)
    except Exception as exc: print(f"❌ Error persona por slug: {exc}"); return jsonify({"error":"Error interno"}),500
    if not persona: return jsonify({"error":"Persona no encontrada"}),404
    return jsonify(persona)


@persona_bp.post("")
@login_required
def api_persona_create(current_user=None):
    data=request.get_json(silent=True) or {}; nombre=(data.get("nombre") or "").strip(); slug=(data.get("slug") or "").strip().lower()
    if not nombre or not slug: return jsonify({"error":"nombre y slug son obligatorios"}),400
    if len(nombre)>200 or len(slug)>120: return jsonify({"error":"nombre o slug demasiado largo"}),400
    payload={"owner_id":str(current_user.id),"nombre":nombre,"slug":slug,"bio":data.get("bio"),"fecha_nacimiento":data.get("fecha_nacimiento"),"fecha_fallecimiento":data.get("fecha_fallecimiento"),"lugar_nacimiento":data.get("lugar_nacimiento"),"lugar_fallecimiento":data.get("lugar_fallecimiento"),"foto_principal":data.get("foto_principal"),"visibilidad":data.get("visibilidad","publica")}
    try:
        response=current_app.supabase.table("personas").insert(payload).execute()
        if not response.data: return jsonify({"error":"No se pudo crear la persona"}),500
        persona=response.data[0]
        try:
            qr_name=generar_qr(f"{request.host_url.rstrip('/')}/p/{persona['id']}"); qr_update=current_app.supabase.table("personas").update({"qr":qr_name}).eq("id",persona["id"]).eq("owner_id",str(current_user.id)).execute()
            if qr_update.data: persona=qr_update.data[0]
        except Exception as qr_exc: print(f"⚠️ Error generando QR de persona: {qr_exc}")
        return jsonify(persona),201
    except Exception as exc: print(f"❌ Error creando persona: {exc}"); return jsonify({"error":"No se pudo crear la persona"}),500


@persona_bp.post("/<persona_id>/qr")
@login_required
def api_persona_qr(persona_id,current_user=None):
    persona_id=_valid_uuid(persona_id)
    if not persona_id:return jsonify({"error":"ID de persona inválido"}),400
    persona=_persona_owned(persona_id,current_user)
    if not persona:return jsonify({"error":"Persona no encontrada"}),404
    try:
        qr_name=generar_qr(f"{request.host_url.rstrip('/')}/p/{persona_id}"); response=current_app.supabase.table("personas").update({"qr":qr_name}).eq("id",persona_id).eq("owner_id",str(current_user.id)).execute()
        if not response.data:return jsonify({"error":"No se pudo guardar el QR"}),500
        return jsonify({"persona_id":persona_id,"qr":qr_name,"qr_url":f"/static/qr/{qr_name}","target":f"/p/{persona_id}"})
    except Exception as exc: print(f"❌ Error generando QR persona: {exc}"); return jsonify({"error":"No se pudo generar el QR"}),500


@persona_bp.post("/<persona_id>/conversations")
def api_conversation_create(persona_id):
    persona_id=_valid_uuid(persona_id)
    if not persona_id:return jsonify({"error":"ID de persona inválido"}),400
    if not get_persona_by_id(current_app,persona_id):return jsonify({"error":"Persona no encontrada"}),404
    data=request.get_json(silent=True) or {}; session_id=_session_id(data.get("session_id")); conversation=crear_conversacion(persona_id,session_id,metadata={"channel":"qr_web"})
    if not conversation:return jsonify({"error":"No se pudo crear la conversación"}),500
    return jsonify({"conversation":conversation,"session_id":session_id}),201


@persona_bp.get("/conversations/<conversation_id>")
def api_conversation(conversation_id):
    conversation_id=_valid_uuid(conversation_id)
    if not conversation_id:return jsonify({"error":"Conversación inválida"}),400
    session_id=request.args.get("session_id")
    if not session_id:return jsonify({"error":"session_id es obligatorio"}),400
    conversation=obtener_conversacion(conversation_id,session_id)
    if not conversation:return jsonify({"error":"Conversación no encontrada"}),404
    return jsonify({**conversation,"mensajes":obtener_mensajes(conversation_id,session_id=session_id)})


@persona_bp.post("/<persona_id>/chat")
def api_persona_chat(persona_id):
    persona_id=_valid_uuid(persona_id)
    if not persona_id:return jsonify({"error":"ID de persona inválido"}),400
    data=request.get_json(silent=True) or {}; message=(data.get("message") or "").strip(); conversation_id=_valid_uuid(data.get("conversation_id")); session_id=_session_id(data.get("session_id"))
    if not message:return jsonify({"error":"El mensaje es obligatorio"}),400
    if len(message)>5000:return jsonify({"error":"Mensaje demasiado largo"}),400
    if not get_persona_by_id(current_app,persona_id):return jsonify({"error":"Persona no encontrada"}),404
    if not current_app.openai_client:return jsonify({"error":"IA no configurada en el servidor"}),503
    if conversation_id:
        conversation=obtener_conversacion(conversation_id,session_id)
        if not conversation or conversation.get("persona_id")!=persona_id:return jsonify({"error":"Conversación inválida"}),400
    else:
        conversation=crear_conversacion(persona_id,session_id,metadata={"channel":"qr_web"})
        if not conversation:return jsonify({"error":"No se pudo iniciar la conversación"}),500
        conversation_id=conversation["id"]
    try:
        historial=_historial_persistido(conversation_id,session_id)
        resultado=generar_respuesta(persona_id,message,historial)
        if not resultado:return jsonify({"error":"Persona no encontrada"}),404
        emocion=resultado["emocion"]
        respuesta=resultado["respuesta"]
        if not guardar_mensaje(conversation_id,"visitor",message,emotion={"detected":emocion}):
            return jsonify({"error":"No se pudo guardar el mensaje del visitante"}),500
        if not guardar_mensaje(conversation_id,"persona",respuesta,emotion={"visitor":emocion}):
            return jsonify({"error":"No se pudo guardar la respuesta"}),500

        # Piper es una capa de presentación opcional: un fallo de TTS no rompe el chat.
        audio_url = sintetizar_voz(respuesta, emocion)
        return jsonify({
            "conversation_id": conversation_id,
            "session_id": session_id,
            "persona": resultado["persona"],
            "respuesta": respuesta,
            "emocion": emocion,
            "audio_url": audio_url,
            "audio": audio_url,
        })
    except Exception as exc: print(f"❌ Error Character Engine: {exc}"); return jsonify({"error":"No se pudo generar la respuesta"}),500
