"""Parse the AIAG website scrape into per-page docs, strip repeated
boilerplate (nav chrome, purchase widgets, related-resources filter panel),
and ingest each page via /api/upload-text.

Usage:
  python3 scripts/ingest_clean.py <md_path> <base_url> [collection]

Example:
  python3 scripts/ingest_clean.py \
    "Agent-prompts-aiag/Agent-prompts-aiag/aiag_website.md" \
    https://ava-engine.vercel.app \
    default
"""
import json
import re
import sys
import time
from collections import Counter

import requests

SRC = sys.argv[1]
BASE = sys.argv[2].rstrip("/")
COLLECTION = sys.argv[3] if len(sys.argv) > 3 else "default"

BOILERPLATE_MIN_PAGES = 15  # a line seen verbatim on >=15 distinct pages -> chrome, not content
RELATED = "## Related Resources"


def build_pages(src_path):
    with open(src_path, encoding="utf-8", errors="ignore") as f:
        text = f.read()

    parts = re.split(r"(?m)^## (https?://\S+)\s*$", text)
    raw_pages = []
    seen_urls = set()
    for i in range(1, len(parts), 2):
        url = parts[i].strip()
        body = re.sub(r"\n---\s*$", "", parts[i + 1].strip())
        if url in seen_urls or "/login" in url.lower():
            continue
        seen_urls.add(url)
        ridx = body.find(RELATED)
        if ridx != -1:
            body = body[:ridx].strip()
        raw_pages.append((url, body))

    line_page_count = Counter()
    for _, body in raw_pages:
        for l in set(l.strip() for l in body.splitlines() if l.strip()):
            line_page_count[l] += 1
    boilerplate = {l for l, c in line_page_count.items() if c >= BOILERPLATE_MIN_PAGES}

    pages = []
    for url, body in raw_pages:
        kept = [l for l in body.splitlines() if l.strip() and l.strip() not in boilerplate]
        clean_body = "\n".join(kept).strip()

        lines = [l.strip() for l in body.splitlines() if l.strip()]
        title = url
        for l in lines:
            if l and l[0] not in "[](#":
                title = l
                break
        if title in {"404 Error", "MENU"}:
            continue
        if len(clean_body) < 50:
            continue
        pages.append({"title": title, "url": url, "text": clean_body})
    return pages


def main():
    pages = build_pages(SRC)
    print(f"{len(pages)} cleaned pages to ingest")

    ok, failed = 0, []
    for i, p in enumerate(pages, 1):
        try:
            r = requests.post(
                f"{BASE}/api/upload-text",
                json={"title": p["title"], "url": p["url"], "text": p["text"], "collection": COLLECTION},
                timeout=55,
            )
            if r.status_code == 200:
                ok += 1
                print(f"[{i}/{len(pages)}] ok  {p['url']}  ({r.json().get('n_chunks')} chunks)")
            else:
                failed.append((p["url"], r.status_code, r.text[:200]))
                print(f"[{i}/{len(pages)}] FAIL {r.status_code} {p['url']}  {r.text[:200]}")
        except Exception as e:
            failed.append((p["url"], "exc", str(e)))
            print(f"[{i}/{len(pages)}] EXC {p['url']}  {e}")
        time.sleep(0.1)

    print(f"\ndone: {ok} ok, {len(failed)} failed")
    if failed:
        print("failed:")
        for u, code, msg in failed:
            print(" ", code, u, msg)


if __name__ == "__main__":
    main()
