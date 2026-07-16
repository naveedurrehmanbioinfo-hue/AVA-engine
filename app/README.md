# AVA MVP — Grounded Knowledge Assistant

A minimal, functional version of the platform: upload/crawl knowledge, ask
questions, get **grounded-or-refused** answers with real citations. Follows the
build plan's deterministic pipeline and Answer Contract.

## Stack
- **FastAPI** (Python) backend — deterministic answer pipeline
- **Postgres + pgvector** — embeddings + metadata + provenance log (host port **5433**)
- **OpenAI** — `text-embedding-3-small` (vectors) + `gpt-4o-mini` (answers)
- **Hybrid retrieval** — vector (cosine) + full-text (ts_rank), fused with RRF
- Embeddable **widget** + admin **console** (vanilla JS)

## Pipeline (member answer path — deterministic, not agentic)
`normalize → hybrid-retrieve (collection-filtered) → generate (grounded, structured-output) → validate (citations resolve, refuse if no evidence) → log provenance`

## Run locally
1. Put your key in the gitignored `../.env`:
   ```
   OPENAI_API_KEY=sk-...
   SPIDER_CLOUD_API_KEY=sk-...   # optional, for website crawl
   ```
2. From `app/`:
   ```
   docker compose up --build
   ```
3. Open:
   - Console (test bench + knowledge + conversations): http://localhost:8000/
   - Embeddable widget: http://localhost:8000/widget
   - Health: http://localhost:8000/api/health

## Try it
- **Knowledge → Upload** `sample_docs/aiag-webinars-sample.md`
- Ask *"How long is the Timo Unger ELV webinar?"* → grounded answer citing the source (124.03 min — from the record, not invented).
- Ask *"What is AIAG's refund policy?"* → **honest refusal** (not in the corpus), logged as a gap.

## API
| Method | Path | Purpose |
|---|---|---|
| POST | `/api/chat` | `{query}` → grounded answer / refusal + citations + provenance |
| POST | `/api/upload` | multipart file → parsed, chunked, embedded, indexed |
| POST | `/api/crawl` | `{url,limit}` → spider.cloud crawl → ingested |
| GET | `/api/sources` | list ingested sources |
| GET | `/api/conversations` | provenance log |
| POST | `/api/feedback` | `{conversation_id, feedback}` 👍/👎 |
| GET | `/api/health` | status, key presence, counts |

## What's intentionally MVP (per the build plan's phasing)
Grounding is enforced structurally (no invented citations, refuse-on-no-evidence).
Deferred to later phases: typed fact registry + contradiction queue, NLI claim-support
grader, entitlements/multi-instance isolation beyond collection filters, eval harness
+ release gates, agentic KG pipeline, streaming. The abstractions (collections,
provenance, Answer Contract) are in place so those slot in without a rewrite.
