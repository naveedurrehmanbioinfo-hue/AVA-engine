from fastapi import FastAPI, Depends, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from sqlalchemy.orm import Session
from sqlalchemy import select, func
import logging
import os

from .db import init_db, get_db
from .models import Source, Chunk, Conversation
from . import ingest as ingestion
from . import pipeline
from . import spider
from .config import settings

app = FastAPI(title="AVA — Grounded Knowledge Assistant (MVP)")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # MVP: widget embeds anywhere. Lock down per-instance later.
    allow_methods=["*"],
    allow_headers=["*"],
)

WEB_DIR = os.environ.get("AVA_WEB_DIR") or os.path.join(os.path.dirname(os.path.dirname(__file__)), "web")


@app.on_event("startup")
def _startup():
    # Never let a DB hiccup take the whole app down (esp. on serverless cold
    # starts before DATABASE_URL is configured) — DB-dependent routes will
    # still surface their own errors when called.
    try:
        init_db()
    except Exception:
        logging.getLogger(__name__).exception("init_db() failed on startup")


# ---------- health / config ----------
@app.get("/api/health")
def health(db: Session = Depends(get_db)):
    return {
        "status": "ok",
        "openai_key_set": bool(settings.openai_api_key),
        "spider_key_set": bool(settings.spider_cloud_api_key),
        "sources": db.scalar(select(func.count()).select_from(Source)) or 0,
        "chunks": db.scalar(select(func.count()).select_from(Chunk)) or 0,
    }


# ---------- chat ----------
class ChatIn(BaseModel):
    query: str
    instance: str = "default"
    collection: str = "default"


@app.post("/api/chat")
def chat(body: ChatIn, db: Session = Depends(get_db)):
    try:
        return pipeline.answer(db, body.query, instance=body.instance, collection=body.collection)
    except RuntimeError as e:
        raise HTTPException(status_code=400, detail=str(e))


# ---------- ingestion ----------
@app.post("/api/upload")
async def upload(
    file: UploadFile = File(...),
    collection: str = Form("default"),
    db: Session = Depends(get_db),
):
    data = await file.read()
    try:
        src = ingestion.ingest_file(db, filename=file.filename, data=data, collection=collection)
    except RuntimeError as e:
        raise HTTPException(status_code=400, detail=str(e))
    return {"id": src.id, "title": src.title, "n_chunks": src.n_chunks, "collection": src.collection}


class CrawlIn(BaseModel):
    url: str
    limit: int = 10
    collection: str = "default"


@app.post("/api/crawl")
def crawl(body: CrawlIn, db: Session = Depends(get_db)):
    try:
        docs = spider.crawl(body.url, limit=body.limit)
    except spider.SpiderError as e:
        raise HTTPException(status_code=402, detail=str(e))
    created = []
    for d in docs:
        src = ingestion.ingest_text(
            db, title=d["title"], text=d["markdown"], origin="crawl",
            url=d["url"], collection=body.collection,
        )
        created.append({"id": src.id, "title": src.title, "url": src.url, "n_chunks": src.n_chunks})
    return {"pages": len(created), "sources": created}


# ---------- console data ----------
@app.get("/api/sources")
def sources(db: Session = Depends(get_db)):
    rows = db.execute(select(Source).order_by(Source.created_at.desc())).scalars().all()
    return [{"id": s.id, "title": s.title, "origin": s.origin, "url": s.url,
             "collection": s.collection, "n_chunks": s.n_chunks,
             "created_at": s.created_at.isoformat()} for s in rows]


@app.delete("/api/sources/{source_id}")
def delete_source(source_id: str, db: Session = Depends(get_db)):
    src = db.get(Source, source_id)
    if not src:
        raise HTTPException(status_code=404, detail="not found")
    db.delete(src)
    db.commit()
    return {"deleted": source_id}


@app.get("/api/conversations")
def conversations(limit: int = 50, db: Session = Depends(get_db)):
    rows = db.execute(
        select(Conversation).order_by(Conversation.created_at.desc()).limit(limit)
    ).scalars().all()
    return [{"id": c.id, "query": c.query, "answer": c.answer, "refused": c.refused,
             "confidence": c.confidence, "citations": c.citations, "model": c.model,
             "latency_ms": c.latency_ms, "feedback": c.feedback,
             "created_at": c.created_at.isoformat()} for c in rows]


class FeedbackIn(BaseModel):
    conversation_id: str
    feedback: str  # "up" | "down"


@app.post("/api/feedback")
def feedback(body: FeedbackIn, db: Session = Depends(get_db)):
    c = db.get(Conversation, body.conversation_id)
    if not c:
        raise HTTPException(status_code=404, detail="not found")
    c.feedback = body.feedback
    db.commit()
    return {"ok": True}


# ---------- static UI ----------
@app.get("/")
def root():
    return FileResponse(os.path.join(WEB_DIR, "console.html"))


@app.get("/favicon.ico")
def favicon():
    return FileResponse(os.path.join(WEB_DIR, "avatar-99xlab-ink.png"), media_type="image/png")


@app.get("/widget")
def widget():
    return FileResponse(os.path.join(WEB_DIR, "widget.html"))


if os.path.isdir(WEB_DIR):
    app.mount("/web", StaticFiles(directory=WEB_DIR), name="web")
