"""The deterministic member answer path:
   normalize -> retrieve (entitlement/collection filtered) -> generate
   (grounded) -> validate -> log provenance.
Not agentic — a fixed pipeline, because in the answer path unpredictability is a
liability.
"""
import time

from sqlalchemy.orm import Session

from .config import settings
from .models import Conversation
from . import retrieve as retrieval
from . import generate as generation
from . import validate as validation


def answer(db: Session, query: str, instance: str = "default", collection: str = "default") -> dict:
    t0 = time.perf_counter()
    query = (query or "").strip()

    if not query:
        return {"refused": True, "answer": "Please ask a question.", "citations": [],
                "confidence": 0.0, "why_relevant": "", "caveat": ""}

    # Retrieve (collection filter = query-time isolation).
    hits = retrieval.retrieve(db, query, collection=collection)

    # No usable evidence above the similarity floor -> refuse early, log the gap.
    usable = [h for h in hits if h.similarity >= settings.min_similarity]
    usage = {"model": "", "prompt_tokens": 0, "completion_tokens": 0}

    if not usable:
        result = validation.validate({"refused": True}, [])
    else:
        raw, usage = generation.generate(query, usable)
        result = validation.validate(raw, usable)

    latency_ms = int((time.perf_counter() - t0) * 1000)

    # Provenance log — every answer, refused or not.
    convo = Conversation(
        instance=instance, query=query,
        answer=result["answer"], refused=result["refused"],
        confidence=result["confidence"], citations=result["citations"],
        retrieved_chunk_ids=[h.chunk_id for h in hits],
        model=usage["model"], latency_ms=latency_ms,
        prompt_tokens=usage["prompt_tokens"], completion_tokens=usage["completion_tokens"],
    )
    db.add(convo)
    db.commit()
    db.refresh(convo)

    result["conversation_id"] = convo.id
    result["latency_ms"] = latency_ms
    result["retrieval"] = [
        {"title": h.title, "url": h.url, "similarity": round(h.similarity, 3)} for h in hits
    ]
    return result
