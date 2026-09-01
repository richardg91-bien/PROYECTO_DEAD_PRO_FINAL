"""Motor de evolución: la IA crece a través de sus experiencias con los humanos.

Guarda en Supabase (tabla aria_embeddings, tipo 'evolucion' y 'estilo') un
estado de crecimiento por persona:

- nivel: 1-5, sube con las interacciones significativas
- apertura_preguntas: 0-1, cuánto le funcionan las preguntas al usuario
- afinidad: 0-1, vínculo emocional acumulado
- aprendizajes: hechos/gustos/dolores que la IA ha aprendido y reutiliza

Así la IA no es estática: cada conversación la deja distinta que antes.
"""

from flask import current_app

DEFAULT_ESTADO = {
    "nivel": 1,
    "interacciones": 0,
    "apertura_preguntas": 0.7,
    "afinidad": 0.2,
    "aprendizajes": [],
}


class EstadoEvolucion:
    """Estado de evolución de la IA respecto a una persona."""

    def __init__(self, persona, datos=None):
        self.persona = persona
        datos = datos or {}
        self.nivel = int(datos.get("nivel", 1))
        self.interacciones = int(datos.get("interacciones", 0))
        self.apertura_preguntas = float(datos.get("apertura_preguntas", 0.7))
        self.afinidad = float(datos.get("afinidad", 0.2))
        self.aprendizajes = list(datos.get("aprendizajes", []))

    @property
    def nombre_nivel(self):
        nombres = {1: "Aprendiz", 2: "Atenta", 3: "Cercana", 4: "Cómplice", 5: "Alma afín"}
        return nombres.get(self.nivel, "Aprendiz")

    def to_dict(self):
        return {
            "nivel": self.nivel,
            "nombre_nivel": self.nombre_nivel,
            "interacciones": self.interacciones,
            "apertura_preguntas": round(self.apertura_preguntas, 2),
            "afinidad": round(self.afinidad, 2),
            "aprendizajes": self.aprendizajes[-10:],
        }

    def registrar_interaccion(self, estado_emocional, hubo_respuesta_a_pregunta=None):
        """Evoluciona con una interacción nueva.

        Args:
            estado_emocional (dict): salida de analizar_estado_emocional().
            hubo_respuesta_a_pregunta (bool | None): si el mensaje anterior de la
                IA fue pregunta y el usuario respondió con sustancia.
        """
        self.interacciones += 1

        # La afinidad crece con la apertura emocional y el duelo compartido
        ganancia = 0.03 + 0.1 * estado_emocional.get("apertura", 0) + 0.05 * estado_emocional.get("intensidad", 0)
        self.afinidad = min(1.0, self.afinidad + ganancia)

        # Aprende si las preguntas funcionan con esta persona
        if hubo_respuesta_a_pregunta is True:
            self.apertura_preguntas = min(1.0, self.apertura_preguntas + 0.08)
        elif hubo_respuesta_a_pregunta is False:
            self.apertura_preguntas = max(0.2, self.apertura_preguntas - 0.06)

        # Sube de nivel cada 5 interacciones hasta 5
        self.nivel = min(5, 1 + self.interacciones // 5)

    def aprender(self, texto):
        """Añade un aprendizaje (gusto, miedo, recuerdo importante) si es nuevo."""
        texto = (texto or "").strip()
        if texto and texto.lower() not in {a.lower() for a in self.aprendizajes}:
            self.aprendizajes.append(texto)
            self.aprendizajes = self.aprendizajes[-20:]


def cargar_estado(persona):
    """Carga el estado de evolución de una persona desde Supabase."""
    estado = EstadoEvolucion(persona)
    try:
        res = current_app.supabase.table("aria_embeddings").select("contenido").match({
            "persona": persona, "tipo": "evolucion"
        }).limit(1).execute()
        if res.data:
            import json
            try:
                datos = json.loads(res.data[0]["contenido"])
                estado = EstadoEvolucion(persona, datos)
            except (ValueError, TypeError):
                pass
    except Exception as e:
        print(f"⚠️ Evolución: no se pudo cargar estado: {e}")
    return estado


def guardar_estado(estado):
    """Persiste el estado de evolución (upsert simple: guarda una fila nueva)."""
    import json
    try:
        current_app.supabase.table("aria_embeddings").insert({
            "persona": estado.persona,
            "contenido": json.dumps(estado.to_dict(), ensure_ascii=False),
            "embedding": [0.0] * 8,
            "tipo": "evolucion",
        }).execute()
    except Exception as e:
        print(f"⚠️ Evolución: no se pudo guardar estado: {e}")


def extraer_aprendizajes(mensaje):
    """Extrae frases con información sobre el usuario para aprender de ellas."""
    import re
    patrones = [
        r"(?:me gusta|me encanta|amo)\s+([^.,;!?]{3,80})",
        r"(?:no me gusta|odio|detesto)\s+([^.,;!?]{3,80})",
        r"(?:me llamo|soy)\s+([A-ZÁÉÍÓÚÑ][\wáéíóúñ]{1,30})",
        r"(?:trabajo como|trabajo en|estudio)\s+([^.,;!?]{3,60})",
        r"(?:tengo miedo de|me da miedo)\s+([^.,;!?]{3,80})",
    ]
    encontrados = []
    for patron in patrones:
        for m in re.finditer(patron, mensaje or "", re.IGNORECASE):
            fragmento = m.group(0).strip()
            if fragmento not in encontrados:
                encontrados.append(fragmento)
    return encontrados[:3]
