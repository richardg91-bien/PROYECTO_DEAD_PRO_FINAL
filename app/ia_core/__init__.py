"""Motor de IA propio de PROYECTO_DEAD_PRO.

IA empática y local: no depende de ninguna API externa.
- `motor.py`       → cerebro: genera respuestas empáticas en español.
- `emociones.py`   → análisis emocional con intensidad y detección de duelo.
- `estilo.py`      → estilo de habla por persona (aprendido de las conversaciones).
- `evolucion.py`   → memoria de crecimiento: aprende de cada interacción y evoluciona.
"""

from app.ia_core.motor import MotorEmpatico, get_motor

__all__ = ["MotorEmpatico", "get_motor"]
