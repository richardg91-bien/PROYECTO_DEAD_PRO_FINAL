from app.routes import obtener_respuesta_ia


class DummyCompletions:
    def __init__(self, responses):
        self.responses = responses
        self.calls = []

    def create(self, **kwargs):
        self.calls.append(kwargs)
        if self.responses:
            response = self.responses.pop(0)
            if isinstance(response, Exception):
                raise response
            return response
        raise RuntimeError("sin respuestas")


class FakeClient:
    def __init__(self, responses):
        self.chat = type("Chat", (), {"completions": DummyCompletions(responses)})()


def test_obtener_respuesta_ia_fallback_a_modelo_disponible():
    class Response:
        class Choice:
            class Message:
                content = "respuesta"

            message = Message()

        choices = [Choice()]

    client = FakeClient([
        Exception("model_not_found"),
        Response(),
    ])

    respuesta, modelo = obtener_respuesta_ia(client, "hola", modelo_inicial="deepseek-chat")

    assert respuesta == "respuesta"
    assert modelo == "llama-3.1-8b-instant"
    assert len(client.chat.completions.calls) == 2


def test_obtener_respuesta_ia_fallback_con_error_404_de_modelo():
    class Response:
        class Choice:
            class Message:
                content = "respuesta"

            message = Message()

        choices = [Choice()]

    class ApiError(Exception):
        def __init__(self):
            super().__init__("The model does not exist")
            self.status_code = 404
            self.code = "model_not_found"
            self.body = {"error": {"code": "model_not_found"}}

    client = FakeClient([
        ApiError(),
        Response(),
    ])

    respuesta, modelo = obtener_respuesta_ia(client, "hola", modelo_inicial="deepseek-chat")

    assert respuesta == "respuesta"
    assert modelo == "llama-3.1-8b-instant"
    assert len(client.chat.completions.calls) == 2
