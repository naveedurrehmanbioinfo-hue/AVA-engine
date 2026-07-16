from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, declarative_base

from .config import settings

engine = create_engine(settings.database_url, pool_pre_ping=True, future=True)
SessionLocal = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False, future=True)
Base = declarative_base()


def init_db() -> None:
    """Enable pgvector, create tables, and a full-text index for hybrid search."""
    from . import models  # noqa: F401  (register models on Base)

    with engine.begin() as conn:
        conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector"))

    Base.metadata.create_all(engine)

    with engine.begin() as conn:
        # Full-text index for the BM25-style arm of hybrid retrieval.
        conn.execute(text(
            "CREATE INDEX IF NOT EXISTS chunks_fts_idx "
            "ON chunks USING GIN (to_tsvector('english', content))"
        ))
        # ANN index for vector search (cosine).
        conn.execute(text(
            "CREATE INDEX IF NOT EXISTS chunks_embedding_idx "
            "ON chunks USING ivfflat (embedding vector_cosine_ops) WITH (lists = 100)"
        ))


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
