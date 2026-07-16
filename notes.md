# AVA Console — Engineering Notes

Running log of the stack, the bugs that cost real time, and how they were fixed.
Keep entries short. Add a bug here when the cause was non-obvious from the code.

## Stack

RAG is hand-rolled on Postgres. No vector DB, no LangChain/LlamaIndex.

| Layer | What | Where |
|---|---|---|
| Store | Postgres + **pgvector**, `chunks.embedding vector(1536)` | `models.py` |
| Chunking | tiktoken `cl100k_base`, 400-token windows, 60 overlap | `chunking.py` |
| Embeddings | OpenAI `text-embedding-3-small`, batched 200/call | `llm.py` |
| Retrieval | **Hybrid**: pgvector cosine (`<=>`) + Postgres FTS (`ts_rank`), fused with RRF (k=60) | `retrieve.py` |
| Generation | OpenAI `gpt-5.5`, forced JSON, citations validated vs real chunk IDs | `generate.py` |
| Pipeline | retrieve → similarity floor → generate → validate → log | `pipeline.py` |
| API/UI | FastAPI + vanilla HTML console | `main.py`, `web/console.html` |

Knobs (`config.py`): `retrieve_k=8` per arm, `context_k=5` to the LLM,
`min_similarity=0.25`, `chunk_tokens=400`, `chunk_overlap=60`.

Local: `cd app && docker compose up -d` → :8000 (db on :5433). venv at `app/backend/.venv`.
Prod: Vercel (`ava-engine.vercel.app`) + Neon Postgres. Deploy lands ~20-40s after push — poll, don't assume.

## Bugs

### Hybrid retrieval silently ran as vector-only  ← the expensive one
`61009ff`. The FTS arm never set `similarity`, so keyword-only hits carried
`0.0`. `pipeline.py` filters `similarity >= min_similarity` (0.25), so **every
chunk only the keyword arm found was discarded before generation**. The FTS arm
could only reorder what the vector arm already had.

- **Symptom**: broad questions refused ("the passages do not state...") while
  specific phrasings answered fine. Evidence sat in a retrieved-but-dropped chunk.
- **Tell**: `similarity: 0.0` rows in the `retrieval` array of `/api/chat`.
  A real chunk scoring exactly 0.0 means *unset*, not *irrelevant*.
- **Fix**: compute the same cosine similarity in the FTS query, record it during fusion.
- **Lesson**: this was misdiagnosed for hours as a *data* problem (boilerplate,
  duplicates, chunk dilution) and "fixed" with two delete+re-ingest cycles and a
  `retrieve_k`/`context_k` bump (`5156554`, reverted in `2f8c1ab`). None of it helped
  because the bug was plumbing. **Check the retrieval output before blaming the corpus.**

### gpt-5.5 rejects `temperature=0`
`a5b5533`. `generate.py` hardcoded `temperature=0`; gpt-5.5 only supports the
default. Every chat request 500'd immediately after the model switch.
`openai.BadRequestError: Unsupported value: 'temperature' does not support 0`.
Fix: drop the param. **Re-test chat after any model change** — this broke prod silently.

### OpenAI 2048-input embedding cap
`e714da6`. `llm.embed()` sent all chunks in one request. OpenAI caps embeddings
at 2048 inputs/request, so any upload over ~2048 chunks failed outright.
Fix: batch at `_EMBED_BATCH = 200`.

### Vercel 60s limit killed large uploads
`a5b5533`. Single-request upload (parse→chunk→embed→store) blew the function
limit with no partial save. Fix: two-phase —
`/api/upload/init` (parse+chunk, no embedding, fast) then
`/api/upload/embed-batch` looped 100 at a time, which also drives a **real**
progress bar. The old 4-step stepper was a fixed-timing animation, not server state.

Chunks land with `embedding=NULL` between the phases. Retrieval filters
`embedding IS NOT NULL`, so half-ingested sources stay invisible to search — by design.

## Ingestion gotchas

`Agent-prompts-aiag/.../aiag_website.md` is a 3.5MB scrape of **747 pages**
concatenated under `## https://...` headers.

- **Never upload it raw.** You get one source titled `aiag_website.md`, no URL,
  ~3000 chunks → citations read `aiag_website.md | None` and are unclickable.
- Split per-page instead: 340 real pages (~400 login/404 stubs filtered out),
  each with its true title + URL.
- `scripts/ingest_clean.py <md> <base_url> [collection]` — splits, strips repeated
  nav/purchase boilerplate, POSTs each page to `/api/upload-text`.
- `scripts/delete_sources.py <base_url> --title <substr> [--yes]` — dry-run by default.

**Boilerplate cleaning lives only in the script, not the server.** `ingest_text()`
does no cleaning, and `spider.py` stores crawl markdown verbatim (no readability
pass) — so `/api/crawl` and UI uploads still ingest nav chrome. Move the cleaning
into `ingest_text()` if that becomes a problem.

Scraped AIAG pages are ~90% chrome (language menus, "Related Resources" filter
panel with 220 results). One page → 121 chunks of mostly noise. It hurts citation
quality; it was *not* the cause of the refusals above.
