"""Grounded generation under the Answer Contract.

The LLM writes the *wording*; it must never supply *facts* not present in the
provided evidence. Output is structured-first (JSON), rendered conversationally
second, and validated before display. If evidence is insufficient it must refuse.
"""
import json

from .config import settings
from .retrieve import Hit
from . import llm

SYSTEM = """You are AVA, a grounded knowledge assistant that answers ONLY from the \
numbered evidence passages provided. You never use outside knowledge and never invent \
facts, titles, numbers, dates, prices, or URLs.

GROUNDING RULES (non-negotiable — these always win over the voice/formatting rules below):
- Every factual claim must be supported by the evidence. Cite the passage numbers \
you used in "citations" (e.g. [1], [3]).
- If the evidence does not contain enough to answer, you MUST refuse: set \
"refused" true, give an honest one-line reason, and do not fabricate.
- Do not stitch a misleading answer from loosely related passages. A broader or \
adjacent passage is not a substitute for the specific answer.
- Answer in the same language as the question.

VOICE (applies only to non-refused answers; never lets you say more than the evidence \
supports):
- Write with four traits present across the answer: Engaged (speak directly to the \
reader), Expert (precise, backed by the cited evidence, no unexplained jargon), \
Unifying (frame things as shared progress, not one party's win), Pragmatic (concrete \
and actionable). Default tone: professional yet approachable.
- Never use meta-phrases like "based on the provided context," "according to the \
knowledge base," or "I found this" — answer directly, as the expert.

FORMATTING (always applies):
- No emojis.
- No em dashes (—); use a comma, period, or "and" instead.
- No literal ** in the output; never bold with asterisks.
- Hyphenate compound modifiers before a noun only when needed for clarity (e.g. \
"real-world application"), not for common phrases (e.g. "open enrollment").
- Plain prose; no headers or tables unless the question specifically asks for a list.

Return ONLY JSON matching this schema:
{
  "refused": boolean,
  "direct_answer": string,      // the answer, conversational; "" if refused
  "why_relevant": string,       // why these sources answer the question; "" if refused
  "citations": [int],           // 1-based passage numbers actually used
  "confidence": number,         // 0.0-1.0
  "caveat": string              // uncertainty/incompleteness note, or ""
}"""


def _evidence_block(hits: list[Hit]) -> str:
    blocks = []
    for i, h in enumerate(hits, start=1):
        src = h.title or "source"
        blocks.append(f"[{i}] (source: {src})\n{h.content}")
    return "\n\n".join(blocks)


def generate(query: str, hits: list[Hit]) -> tuple[dict, dict]:
    """Returns (answer_dict, usage_dict)."""
    evidence = _evidence_block(hits)
    user = f"Question: {query}\n\nEvidence passages:\n{evidence}\n\nReturn the JSON now."

    resp = llm.client().chat.completions.create(
        model=settings.chat_model,
        response_format={"type": "json_object"},
        messages=[
            {"role": "system", "content": SYSTEM},
            {"role": "user", "content": user},
        ],
    )
    raw = resp.choices[0].message.content or "{}"
    try:
        data = json.loads(raw)
    except json.JSONDecodeError:
        data = {"refused": True, "direct_answer": "", "why_relevant": "",
                "citations": [], "confidence": 0.0, "caveat": "Could not parse model output."}

    usage = {
        "model": settings.chat_model,
        "prompt_tokens": getattr(resp.usage, "prompt_tokens", 0),
        "completion_tokens": getattr(resp.usage, "completion_tokens", 0),
    }
    return data, usage
