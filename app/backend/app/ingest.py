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
