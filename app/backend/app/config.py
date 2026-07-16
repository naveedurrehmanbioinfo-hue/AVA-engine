import os
from pydantic_settings import BaseSettings, SettingsConfigDict


def _load_runtime_secret(key: str) -> str:
    """Fallback: read a secret from a mounted, gitignored file when it isn't
    present in the process environment (used for dev without a container recreate)."""
    path = os.path.join(os.path.dirname(__file__), "_runtime_secret.env")
    if not os.path.exists(path):
        return ""
    for line in open(path, encoding="utf-8"):
        line = line.strip()
        if line.startswith(f"{key}="):
            return line.split("=", 1)[1].strip()
    return ""


class Settings(BaseSettings):
    # Loaded from environment / ../.env (via docker compose env_file).
    model_config = SettingsConfigDict(env_file=".env", extra="ignore", case_sensitive=False)

    database_url: str = "postgresql+psycopg://ava:ava@localhost:5433/ava"

    openai_api_key: str = ""
    spider_cloud_api_key: str = ""

    # Models
    chat_model: str = "gpt-5.5"
    embedding_model: str = "text-embedding-3-small"
    embedding_dim: int = 1536

    # Retrieval / grounding knobs
    retrieve_k: int = 12                 # candidates pulled per search arm
    context_k: int = 8                   # chunks handed to the LLM
    min_similarity: float = 0.25        # cosine floor; below this = no usable evidence -> refuse
    chunk_tokens: int = 400
    chunk_overlap: int = 60


settings = Settings()

# Dev fallback when the key isn't in the container env (avoids a full recreate).
if not settings.openai_api_key:
    settings.openai_api_key = _load_runtime_secret("OPENAI_API_KEY")
