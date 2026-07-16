"""spider.cloud crawl adapter. Returns [{url, title, markdown}] for ingestion.

NOTE: requires a spider.cloud account with credits. Without credits the API
returns 401 {"error":"Credits or a valid subscription required..."}.
"""
import httpx

from .config import settings

API = "https://api.spider.cloud/crawl"


class SpiderError(RuntimeError):
    pass


def crawl(url: str, *, limit: int = 10) -> list[dict]:
    if not settings.spider_cloud_api_key:
        raise SpiderError("SPIDER_CLOUD_API_KEY is not set.")

    payload = {
        "url": url,
        "limit": limit,
        "return_format": "markdown",
        "store_data": False,
    }
    headers = {
        "Authorization": f"Bearer {settings.spider_cloud_api_key}",
        "Content-Type": "application/json",
    }
    with httpx.Client(timeout=120) as c:
        r = c.post(API, json=payload, headers=headers)
    if r.status_code != 200:
        raise SpiderError(f"spider.cloud {r.status_code}: {r.text[:300]}")

    docs = []
    for item in r.json():
        content = item.get("content") or item.get("markdown") or ""
        if not content.strip():
            continue
        docs.append({
            "url": item.get("url"),
            "title": (item.get("metadata") or {}).get("title") or item.get("url") or url,
            "markdown": content,
        })
    return docs
