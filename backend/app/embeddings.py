
from functools import lru_cache

from sentence_transformers import SentenceTransformer


MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"
EMBEDDING_DIMENSION = 384


@lru_cache(maxsize=1)
def get_embedding_model():
    return SentenceTransformer(MODEL_NAME)


def generate_embedding(text: str) -> list[float]:
    if not text.strip():
        raise ValueError("Cannot embed empty text")

    model = get_embedding_model()

    vector = model.encode(
        text,
        normalize_embeddings=True
    )

    return vector.tolist()


def generate_embeddings(
    texts: list[str]
) -> list[list[float]]:
    if not texts:
        return []

    model = get_embedding_model()

    vectors = model.encode(
        texts,
        batch_size=16,
        normalize_embeddings=True,
        show_progress_bar=False
    )

    return vectors.tolist()
