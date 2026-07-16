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


def embed(texts: list[str]) -> list[list[float]]:
    if not texts:
        return []
    resp = client().embeddings.create(model=settings.embedding_model, input=texts)
    return [d.embedding for d in resp.data]


def embed_one(text: str) -> list[float]:
    return embed([text])[0]
