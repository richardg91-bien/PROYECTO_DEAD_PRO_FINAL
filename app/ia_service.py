"""Servicio de embeddings."""

try:
    from sentence_transformers import SentenceTransformer
except ImportError:  # pragma: no cover - depende del entorno
    SentenceTransformer = None

_model = None


def get_embedding_model():
    global _model
    if _model is None:
        if SentenceTransformer is None:
            raise RuntimeError("La dependencia 'sentence-transformers' no está instalada")
        _model = SentenceTransformer("all-MiniLM-L6-v2")
    return _model


def generar_embedding(texto):
    if SentenceTransformer is None:
        return [float(sum(ord(c) for c in texto.lower()) % 997) / 997.0 for _ in range(8)]

    embedding = get_embedding_model().encode(texto)
    return embedding.tolist()
