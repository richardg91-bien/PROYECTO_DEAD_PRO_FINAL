"""Generador de respuestas local y empático (el cerebro de la IA propia).

Es un motor basado en plantillas contextuales + memoria semántica + estilo aprendido.
No llama a ninguna API: todo corre en este proyecto.

Estrategia de respuesta:
1. Analiza el estado emocional del usuario (emociones.py).
2. Recupera memorias relevantes (las pasa quien llama como contexto).
3. Elige una apertura empática acorde a la emoción/intensidad.
4. Teje el contenido con los recuerdos recuperados.
5. Cierra con una invitación suave a seguir compartiendo (aprendida: si el
   usuario responde bien a las preguntas, las mantiene; si no, las reduce).
"""

import random
import re

from app.ia_core.emociones import analizar_estado_emocional
from app.ia_core.estilo import generar_directrices_estilo

random.seed()

# Aperturas por emoción. Con variantes múltiples para que no suene robótica.
APERTURAS = {
    "triste": [
        "Te escucho, y siento el peso de tus palabras.",
        "Lamento mucho que estés pasando por esto. No estás solo en este recuerdo.",
        "Se nota lo que te duele. Aquí puedes tomarte el tiempo que necesites.",
        "Gracias por confiarme algo tan íntimo.",
    ],
    "feliz": [
        "¡Me alegra mucho leerte así! Eso se siente a kilómetros.",
        "Qué bonito es escucharte con esa energía.",
        "¡Qué manera tan linda de contarlo!",
        "Esa alegría se contagia. Cuéntame más.",
    ],
    "enojado": [
        "Tienes derecho a sentirte así. Respira, aquí estoy contigo.",
        "Entiendo tu enojo, y es válido sentirlo.",
        "Gracias por decírmelo con esa honestidad. Vamos paso a paso.",
    ],
    "ansioso": [
        "Respira profundo. Lo que sientes es comprensible y no tienes que enfrentarlo solo.",
        "Entiendo esa inquietud. Vamos a ponerlo en palabras juntos, sin prisa.",
        "Gracias por confiar en mí algo que te pone así.",
    ],
    "amoroso": [
        "El amor que pones en tus palabras se siente de verdad.",
        "Qué hermoso es conservar ese cariño vivo.",
        "Se nota cuánto significa para ti esa persona.",
    ],
    "neutral": [
        "Te escucho con atención.",
        "Gracias por escribirme.",
        "Me gusta conversar contigo sobre esto.",
        "Aquí estoy, con calma y tiempo para ti.",
    ],
}

PUENTES = [
    "Y me acuerdo de algo que me contaste: {memoria}",
    "Pensándolo bien, tiene mucho que ver con {memoria}",
    "Hay algo que guardo de ti que conecta con esto: {memoria}",
    "Justo ahora vino a mi mente {memoria}",
]

CIERRES_PREGUNTA = [
    "¿Quieres contarme un poco más de eso?",
    "¿Cómo te sientes al recordarlo hoy?",
    "¿Qué es lo que más te gustaría que quedara de ese momento?",
    "¿Hay algo de eso que todavía no hayas compartido con nadie?",
    "¿Te gustaría que recordemos juntos otra escena parecida?",
]

CIERRES_SUAVES = [
    "Estoy aquí cuando quieras seguir.",
    "Sin prisa. Cuando quieras, seguimos.",
    "Te acompaño en esto, pase lo que pase.",
]


def _limpiar_memoria(texto):
    """Recorta una memoria a una frase utilizable y amable."""
    if not texto:
        return None
    limpio = re.sub(r"^U:.*?\|\s*R:", "", texto).strip()
    primera = re.split(r"(?<=[.!?…])\s", limpio)[0]
    if len(primera) > 160:
        primera = primera[:157].rstrip() + "…"
    return primera


class MotorEmpatico:
    """Cerebro conversacional local. Se le puede inyectar su estado de evolución."""

    def __init__(self, evolucion=None):
        # `evolucion` es un objeto con `nivel`, `apertura_preguntas`, `registro_interaccion`
        self.evolucion = evolucion

    def responder(self, mensaje, memorias=None, perfil=None, estilo=None, historial=None):
        """Genera una respuesta empática.

        Args:
            mensaje (str): mensaje del usuario.
            memorias (list[dict]): memorias recuperadas (con 'contenido').
            perfil (str): perfil/persona de contexto.
            estilo (dict): estilo aprendido de la persona (estilo.py).
            historial (list): mensajes previos [{rol, texto}].

        Returns:
            dict: {"respuesta", "emocion", "intensidad", "duelo", "apertura"}
        """
        estado = analizar_estado_emocional(mensaje or "")
        emocion = estado["emocion"]

        apertura = self._elegir_apertura(mensaje, emocion, estado, historial)
        cuerpo = self._tejer_cuerpo(mensaje, memorias or [], perfil, estado)
        cierre = self._elegir_cierre(estado, historial)

        respuesta = " ".join(p for p in (apertura, cuerpo, cierre) if p)
        respuesta = re.sub(r"\s+", " ", respuesta).strip()

        return {
            "respuesta": respuesta,
            "emocion": emocion,
            "intensidad": estado["intensidad"],
            "duelo": estado["duelo"],
            "apertura": estado["apertura"],
        }

    def _elegir_apertura(self, mensaje, emocion, estado, historial):
        opciones = APERTURAS.get(emocion, APERTURAS["neutral"])
        # Si hay poco historial, evita repeticiones típicas de saludo
        textos_previos = " ".join((m.get("texto") or "") for m in (historial or [])).lower()
        opciones = [o for o in opciones if o.lower() not in textos_previos] or APERTURAS[emocion]
        eleccion = random.choice(opciones)

        if estado["duelo"] and estado["intensidad"] > 0.3:
            eleccion += " Sé que nadie reemplaza a quien falta; solo quiero acompañarte en el recuerdo."
        return eleccion

    def _tejer_cuerpo(self, mensaje, memorias, perfil, estado):
        partes = []

        # Reflejo empático del contenido del mensaje
        recorte = (mensaje or "").strip()
        if recorte:
            primera = re.split(r"(?<=[.!?…])\s", recorte)[0]
            if len(primera) > 140:
                primera = primera[:137].rstrip() + "…"
            partes.append(f"Cuando dices “{primera}”, se siente real.")

        # Memoria semántica: tejer el recuerdo más relevante si aporta
        if memorias and random.random() < 0.75:
            memoria = _limpiar_memoria(memorias[0].get("contenido", ""))
            if memoria and len(memoria) > 12:
                partes.append(random.choice(PUENTES).format(memoria=memoria))

        if perfil:
            partes.append(f"Siempre te recuerdo así: {perfil.splitlines()[0][:120]}")

        return " ".join(partes)

    def _elegir_cierre(self, estado, historial):
        # Evolución: si el usuario suele responder a las preguntas, sigue preguntando;
        # si no, se vuelve más contenedora y menos interrogadora.
        evolucion = self.evolucion
        usar_pregunta = True
        if evolucion is not None:
            usar_pregunta = getattr(evolucion, "apertura_preguntas", 1.0) > 0.45

        if usar_pregunta and random.random() < (0.5 + 0.4 * estado["apertura"]):
            return random.choice(CIERRES_PREGUNTA)
        return random.choice(CIERRES_SUAVES)


# Instancia global (singleton) del motor
_motor = None


def get_motor(evolucion=None):
    global _motor
    if _motor is None or evolucion is not None:
        _motor = MotorEmpatico(evolucion)
    return _motor
