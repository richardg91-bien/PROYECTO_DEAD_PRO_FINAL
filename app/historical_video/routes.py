"""Rutas HTTP exclusivas para la generacion de videos historicos."""

import re
from pathlib import Path

from flask import Blueprint, current_app, jsonify, request

from .generator import HistoricalSource, crear_video_historico
from .pipeline import producir_video_historico

historical_video_bp = Blueprint("historical_video", __name__, url_prefix="/api/historical-video")


def _safe_filename(value: str) -> str:
    """Normaliza el nombre de salida y evita rutas arbitrarias."""
    value = (value or "historical_video").strip()
    value = re.sub(r"[^A-Za-z0-9_-]+", "_", value).strip("._-")
    return value or "historical_video"


@historical_video_bp.get("/health")
def health():
    return jsonify({"status": "ok", "service": "historical-video"})


@historical_video_bp.post("/generate")
def generate():
    """Genera un video historico a partir de una narracion suministrada."""
    data = request.get_json(silent=True) or {}

    subject = str(data.get("subject") or "").strip()
    narration = str(data.get("narration") or "").strip()
    title = str(data.get("title") or "").strip() or None

    if not subject or not narration:
        return jsonify({
            "error": "Los campos 'subject' y 'narration' son obligatorios"
        }), 400

    sources = []
    for item in data.get("sources") or []:
        if not isinstance(item, dict):
            continue
        source_title = str(item.get("title") or "").strip()
        reference = str(item.get("reference") or "").strip()
        notes = str(item.get("notes") or "").strip()
        if source_title and reference:
            sources.append(HistoricalSource(source_title, reference, notes))

    try:
        plan = crear_video_historico(
            subject=subject,
            narration=narration,
            title=title,
            sources=sources,
            target_duration_seconds=int(data.get("target_duration_seconds") or 120),
        )

        output_dir = Path(current_app.static_folder) / "videos"
        output_dir.mkdir(parents=True, exist_ok=True)
        filename = _safe_filename(data.get("filename")) + ".mp4"
        output_path = output_dir / filename

        result = producir_video_historico(plan, output_path)

        public_url = f"{request.host_url.rstrip('/')}/static/videos/{filename}"
        return jsonify({
            "status": "ok",
            "title": plan.title,
            "scenes": len(plan.scenes),
            "video": result,
            "url": public_url,
            "plan": plan.to_dict(),
        })

    except ValueError as exc:
        return jsonify({"error": str(exc)}), 400
    except Exception as exc:
        current_app.logger.exception("Error generando video historico")
        return jsonify({"error": f"Error generando video historico: {exc}"}), 500
