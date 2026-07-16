"""Token-aware chunking with overlap. Preserves exact identifiers by never
splitting mid-word; splits on paragraph/sentence boundaries where possible."""
import re
import tiktoken

from .config import settings

_enc = tiktoken.get_encoding("cl100k_base")


def count_tokens(text: str) -> int:
    return len(_enc.encode(text))


def chunk_text(text: str) -> list[str]:
    text = text.strip()
    if not text:
        return []

    # Split into paragraphs first, then pack into token-bounded windows.
    paras = [p.strip() for p in re.split(r"\n\s*\n", text) if p.strip()]
    chunks: list[str] = []
    cur: list[str] = []
    cur_tokens = 0

    for para in paras:
        pt = count_tokens(para)
        # A single oversized paragraph is hard-split by sentences.
        if pt > settings.chunk_tokens:
            if cur:
                chunks.append("\n\n".join(cur))
                cur, cur_tokens = [], 0
            chunks.extend(_split_long(para))
            continue
        if cur_tokens + pt > settings.chunk_tokens and cur:
            chunks.append("\n\n".join(cur))
            # carry overlap: keep tail paragraphs up to chunk_overlap tokens
            cur, cur_tokens = _overlap_tail(cur)
        cur.append(para)
        cur_tokens += pt

    if cur:
        chunks.append("\n\n".join(cur))
    return [c for c in chunks if c.strip()]


def _split_long(para: str) -> list[str]:
    sentences = re.split(r"(?<=[.!?])\s+", para)
    out, cur, cur_tokens = [], [], 0
    for s in sentences:
        st = count_tokens(s)
        if cur_tokens + st > settings.chunk_tokens and cur:
            out.append(" ".join(cur))
            cur, cur_tokens = [], 0
        cur.append(s)
        cur_tokens += st
    if cur:
        out.append(" ".join(cur))
    return out


def _overlap_tail(paras: list[str]) -> tuple[list[str], int]:
    tail, tokens = [], 0
    for para in reversed(paras):
        pt = count_tokens(para)
        if tokens + pt > settings.chunk_overlap:
            break
        tail.insert(0, para)
        tokens += pt
    return tail, tokens
