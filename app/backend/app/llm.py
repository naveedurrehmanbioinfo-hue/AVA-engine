"""Thin wrappers over OpenAI for embeddings and grounded chat completion."""
from openai import OpenAI

from .config import settings

_client: OpenAI | None = None


def client() -> OpenAI:
    global _client
    if _client is None:
        if not settings.openai_api_key:
            raise RuntimeError(
                "OPENAI_API_KEY is not set. Add it to ../.env and restart the api container."
            )
        _client = OpenAI(api_key=settings.openai_api_key)
    return _client


_EMBED_BATCH = 200  # keep well under OpenAI's 2048-input-per-request limit


def embed(texts: list[str]) -> list[list[float]]:
    if not texts:
        return []
    vectors: list[list[float]] = []
    for i in range(0, len(texts), _EMBED_BATCH):
        batch = texts[i:i + _EMBED_BATCH]
        resp = client().embeddings.create(model=settings.embedding_model, input=batch)
        vectors.extend(d.embedding for d in resp.data)
    return vectors


def embed_one(text: str) -> list[float]:
    return embed([text])[0]
