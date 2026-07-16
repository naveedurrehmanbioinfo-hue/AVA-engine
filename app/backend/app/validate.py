"""Post-generation validation, pre-display. Turns a raw model answer + the
retrieved evidence into a validated, citation-clean result — or a refusal.

Enforces the structural zero-tolerance gates we can make deterministic:
 - no invented citations (every cited passage must be one we actually retrieved)
 - no answer without evidence (refuse instead of guessing)
"""
from .retrieve import Hit


def validate(answer: dict, hits: list[Hit]) -> dict:
    """Returns a normalized result dict ready for the API/widget."""
    refused = bool(answer.get("refused"))
    text = (answer.get("direct_answer") or "").strip()

    # 1. No evidence at all -> refuse regardless of what the model said.
    if not hits:
        return _refusal("I don't have a source-backed answer for that in the current knowledge base.")

    # 2. Model chose to refuse, or produced no text.
    if refused or not text:
        reason = (answer.get("caveat") or answer.get("direct_answer")
                  or "The available sources don't contain a reliable answer to that.")
        return _refusal(reason.strip())

    # 3. Map cited passage numbers -> real chunks. Drop anything out of range
    #    (an "invented" citation index) rather than trusting it.
    cited_idx = [c for c in (answer.get("citations") or []) if isinstance(c, int)]
    citations = []
    for c in cited_idx:
        if 1 <= c <= len(hits):
            h = hits[c - 1]
            citations.append({"chunk_id": h.chunk_id, "title": h.title,
                              "url": h.url, "source_id": h.source_id})

    # 4. An answer that cites nothing valid is ungrounded -> refuse.
    if not citations:
        return _refusal("I found related material but couldn't ground a specific answer, "
                        "so I won't guess. Try rephrasing or narrowing the question.")

    return {
        "refused": False,
        "answer": text,
        "why_relevant": (answer.get("why_relevant") or "").strip(),
        "confidence": float(answer.get("confidence") or 0.0),
        "caveat": (answer.get("caveat") or "").strip(),
        "citations": citations,
    }


def _refusal(reason: str) -> dict:
    return {
        "refused": True,
        "answer": reason,
        "why_relevant": "",
        "confidence": 0.0,
        "caveat": "",
        "citations": [],
    }
