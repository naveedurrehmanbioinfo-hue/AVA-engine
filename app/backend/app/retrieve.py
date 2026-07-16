"""Hybrid retrieval: vector (cosine) + full-text (BM25-ish ts_rank), fused with
Reciprocal Rank Fusion. Hybrid is mandatory because knowledge corpora are dense
with exact identifiers (standard codes, SKUs) that pure vector search fumbles.

Isolation is enforced HERE, at query time, via the collection filter — never
just in the UI.
"""
from dataclasses import dataclass

from sqlalchemy import text
from sqlalchemy.orm import Session

from .config import settings
from . import llm


@dataclass
class Hit:
    chunk_id: str
    source_id: str
    title: str
    url: str | None
    content: str
    similarity: float   # cosine similarity of best (vector) match, 0..1
    score: float        # fused RRF score


def retrieve(db: Session, query: str, collection: str = "default", k: int | None = None) -> list[Hit]:
    k = k or settings.context_k
    qvec = llm.embed_one(query)
    vec_literal = "[" + ",".join(f"{x:.7f}" for x in qvec) + "]"

    # Vector arm — cosine distance (<=>); similarity = 1 - distance.
    vec_rows = db.execute(text("""
        SELECT id, source_id, title, url, content,
               1 - (embedding <=> CAST(:qv AS vector)) AS similarity
        FROM chunks
        WHERE collection = :coll AND embedding IS NOT NULL
        ORDER BY embedding <=> CAST(:qv AS vector)
        LIMIT :k
    """), {"qv": vec_literal, "coll": collection, "k": settings.retrieve_k}).mappings().all()

    # Full-text arm — websearch_to_tsquery + ts_rank. Carries the same cosine
    # similarity as the vector arm: downstream applies a min_similarity floor,
    # and leaving it unset here would silently drop every keyword-only hit,
    # reducing hybrid search to vector-only.
    fts_rows = db.execute(text("""
        SELECT id, source_id, title, url, content,
               ts_rank(to_tsvector('english', content),
                       websearch_to_tsquery('english', :q)) AS rank,
               1 - (embedding <=> CAST(:qv AS vector)) AS similarity
        FROM chunks
        WHERE collection = :coll AND embedding IS NOT NULL
          AND to_tsvector('english', content) @@ websearch_to_tsquery('english', :q)
        ORDER BY rank DESC
        LIMIT :k
    """), {"q": query, "qv": vec_literal, "coll": collection,
           "k": settings.retrieve_k}).mappings().all()

    # Reciprocal Rank Fusion.
    RRF_K = 60
    fused: dict[str, dict] = {}
    for rank, row in enumerate(vec_rows):
        e = fused.setdefault(row["id"], {"row": row, "score": 0.0, "similarity": 0.0})
        e["score"] += 1.0 / (RRF_K + rank)
        e["similarity"] = float(row["similarity"])
    for rank, row in enumerate(fts_rows):
        e = fused.setdefault(row["id"], {"row": row, "score": 0.0, "similarity": 0.0})
        e["score"] += 1.0 / (RRF_K + rank)
        e["similarity"] = float(row["similarity"])

    ranked = sorted(fused.values(), key=lambda e: e["score"], reverse=True)[:k]
    return [
        Hit(
            chunk_id=e["row"]["id"], source_id=e["row"]["source_id"],
            title=e["row"]["title"] or "", url=e["row"]["url"],
            content=e["row"]["content"], similarity=e["similarity"], score=e["score"],
        )
        for e in ranked
    ]
