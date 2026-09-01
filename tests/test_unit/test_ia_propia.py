"""Tests del motor de IA propio (empático, evolutivo, local)."""

from app.ia_core.emociones import analizar_estado_emocional, detectar_emocion
from app.ia_core.estilo import fusionar_estilo, extraer_estilo_de_conversacion
from app.ia_core.evolucion import EstadoEvolucion
from app.ia_core.motor import MotorEmpatico
from app.services.ia_propia_service import generar_respuesta_propia


class TestEmociones:
    def test_tristeza_y_duelo(self):
        estado = analizar_estado_emocion_stub("te extraño mucho, desde que te fuiste todo duele")
        assert estado["emocion"] == "triste"
        assert estado["duelo"] is True
        assert estado["intensidad"] > 0

    def test_alegria(self):
        estado = analizar_estado_emocion_stub("estoy muy feliz hoy, ¡gracias!")
        assert estado["emocion"] == "feliz"

    def test_enojo(self):
        assert detectar_emocion("tengo mucha bronca") == "enojado"

    def test_neutral(self):
        estado = analizar_estado_emocion_stub("hola, ¿qué tal?")
        assert estado["emocion"] == "neutral"
        assert estado["duelo"] is False

    def test_vacio(self):
        estado = analizar_estado_emocion_stub("")
        assert estado["emocion"] == "neutral"


def analizar_estado_emocion_stub(texto):
    return analizar_estado_emocional(texto)


class TestEvolucion:
    def test_registrar_interaccion_sube_afinidad(self):
        estado = EstadoEvolucion("Ana")
        antes = estado.afinidad
        estado.registrar_interaccion({"apertura": 0.8, "intensidad": 0.5})
        assert estado.afinidad > antes

    def test_subida_de_nivel(self):
        estado = EstadoEvolucion("Ana")
        for _ in range(11):
            estado.registrar_interaccion({"apertura": 0.2, "intensidad": 0.1})
        assert estado.nivel == 3  # 11 interacciones → nivel 3

    def test_aprende_si_preguntas_funcionan(self):
        estado = EstadoEvolucion("Ana")
        base = estado.apertura_preguntas
        estado.registrar_interaccion({}, hubo_respuesta_a_pregunta=True)
        estado.registrar_interaccion({}, hubo_respuesta_a_pregunta=True)
        assert estado.apertura_preguntas > base

    def test_reducir_preguntas_si_no_funcionan(self):
        estado = EstadoEvolucion("Ana")
        base = estado.apertura_preguntas
        for _ in range(5):
            estado.registrar_interaccion({}, hubo_respuesta_a_pregunta=False)
        assert estado.apertura_preguntas < base

    def test_aprender_sin_duplicados(self):
        estado = EstadoEvolucion("Ana")
        estado.aprender("Me gusta el café")
        estado.aprender("me gusta el café")
        assert len(estado.aprendizajes) == 1


class TestEstilo:
    def test_fusion_acumula_interacciones(self):
        rasgos = extraer_estilo_de_conversacion("Hola, ¿cómo estás!")
        estilo = fusionar_estilo({}, rasgos)
        assert estilo["interacciones"] == 1
        rasgos2 = extraer_estilo_de_conversacion("Otra vez por aquí")
        estilo2 = fusionar_estilo(estilo, rasgos2)
        assert estilo2["interacciones"] == 2

    def test_detecta_usted(self):
        rasgos = extraer_estilo_de_conversacion("¿Usted sabe qué pasó aquel día?")
        assert rasgos["tratamiento"] == "usted"


class TestMotor:
    def test_respuesta_contiene_contenido(self):
        motor = MotorEmpatico()
        res = motor.responder("te extraño mucho", memorias=[{"contenido": "U:hola | R:qué gusto verte"}])
        assert res["respuesta"]
        assert res["emocion"] == "triste"
        assert res["duelo"] is True

    def test_respuesta_usa_memoria(self):
        motor = MotorEmpatico()
        res = motor.responder("hoy recordé aquel verano", memorias=[{"contenido": "El verano en la playa fue inolvidable."}])
        assert "playa" in res["respuesta"] or "verano" in res["respuesta"].lower()

    def test_dos_respuestas_distintas(self):
        motor = MotorEmpatico()
        a = motor.responder("me siento triste")["respuesta"]
        b = motor.responder("me siento triste")["respuesta"]
        # Con variantes múltiples, es muy improbable que salgan idénticas
        assert a != b


class TestIntegracionServicio:
    def test_generar_respuesta_propia(self, app):
        with app.app_context():
            res = generar_respuesta_propia("Ana", "te extraño, abuela", historial=[])
            assert res["motor"] == "propio"
            assert res["respuesta"]
            assert res["emocion"] == "triste"
            assert "nivel" in res
