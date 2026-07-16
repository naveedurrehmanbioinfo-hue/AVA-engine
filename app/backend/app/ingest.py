"""Ingestion: parse -> chunk -> embed -> index. Used by upload and crawl."""
from sqlalchemy.orm import Session

from .models import Source, Chunk
from .chunking import chunk_text
from .parse import extract_text
from . import llm


def ingest_text(
    db: Session,
    *,
    title: str,
    text: str,
    origin: str,
    url: str | None = None,
    collection: str = "default",
) -> Source:
    chunks = chunk_text(text)
    source = Source(
        title=title, origin=origin, url=url, collection=collection,
        status="indexed", n_chunks=len(chunks),
    )
    db.add(source)
    db.flush()  # get source.id

    if chunks:
        vectors = llm.embed(chunks)
        for i, (content, vec) in enumerate(zip(chunks, vectors)):
            db.add(Chunk(
                source_id=source.id, collection=collection, ordinal=i,
                content=content, title=title, url=url, embedding=vec,
            ))
    db.commit()
    db.refresh(source)
    return source


def ingest_file(db: Session, *, filename: str, data: bytes, collection: str = "default") -> Source:
    text = extract_text(filename, data)
    return ingest_text(
        db, title=filename, text=text, origin="upload", url=None, collection=collection,
    )


def start_ingest_file(db: Session, *, filename: str, data: bytes, collection: str = "default") -> Source:
    """Parse + chunk only (no embedding calls) — fast enough for a single
    serverless request even on very large files. Chunks are stored with
    embedding=NULL and picked up by embed_pending_batch(); retrieval already
    filters on `embedding IS NOT NULL` so pending chunks stay invisible to
    search until embedded."""
    text = extract_text(filename, data)
    chunks = chunk_text(text)
    source = Source(
        title=filename, origin="upload", url=None, collection=collection,
        status="indexed" if not chunks else "pending", n_chunks=len(chunks),
    )
    db.add(source)
    db.flush()
    for i, content in enumerate(chunks):
        db.add(Chunk(
            source_id=source.id, collection=collection, ordinal=i,
            content=content, title=filename, url=None, embedding=None,
        ))
    db.commit()
    db.refresh(source)
    return source


def embed_pending_batch(db: Session, *, source_id: str, batch_size: int = 100) -> dict:
    """Embed up to `batch_size` not-yet-embedded chunks for a source. Call
    repeatedly until done=True to drive a real upload progress bar."""
    source = db.get(Source, source_id)
    if source is None:
        raise RuntimeError(f"source {source_id} not found")

    pending = (
        db.query(Chunk)
        .filter(Chunk.source_id == source_id, Chunk.embedding.is_(None))
        .order_by(Chunk.ordinal)
        .limit(batch_size)
        .all()
    )
    if pending:
        vectors = llm.embed([c.content for c in pending])
        for chunk, vec in zip(pending, vectors):
            chunk.embedding = vec
        db.commit()

    remaining = (
        db.query(Chunk)
        .filter(Chunk.source_id == source_id, Chunk.embedding.is_(None))
        .count()
    )
    done = remaining == 0
    if done and source.status != "indexed":
        source.status = "indexed"
        db.commit()

    return {
        "source_id": source_id,
        "embedded_this_batch": len(pending),
        "remaining": remaining,
        "total": source.n_chunks,
        "done": done,
    }
