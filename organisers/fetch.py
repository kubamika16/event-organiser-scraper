"""Small, polite HTTP layer shared by every source.

- one browser-like User-Agent
- a delay between requests to the same site
- an on-disk cache so re-runs and tests don't hit the site again
"""
from __future__ import annotations

import hashlib
import json
import re
import time
import urllib.request
from pathlib import Path
from urllib.parse import urlparse

UA = (
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/130.0 Safari/537.36"
)
CACHE_DIR = Path(".cache")
DELAY_SECONDS = 1.5
_last_hit: dict[str, float] = {}

LD_JSON = re.compile(
    r'<script[^>]*type="application/ld\+json"[^>]*>(.*?)</script>', re.S | re.I
)


def get(url: str, use_cache: bool = True, max_age_hours: float = 12) -> str:
    """Return the page HTML, from cache when fresh enough."""
    CACHE_DIR.mkdir(exist_ok=True)
    key = CACHE_DIR / (hashlib.sha1(url.encode()).hexdigest() + ".html")
    if use_cache and key.exists() and time.time() - key.stat().st_mtime < max_age_hours * 3600:
        return key.read_text(encoding="utf-8")

    host = urlparse(url).netloc
    wait = DELAY_SECONDS - (time.time() - _last_hit.get(host, 0))
    if wait > 0:
        time.sleep(wait)

    req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept-Language": "en-AU,en;q=0.9"})
    for attempt in range(3):
        try:
            with urllib.request.urlopen(req, timeout=30) as resp:
                html = resp.read().decode("utf-8", errors="replace")
            break
        except Exception:
            if attempt == 2:
                raise
            time.sleep(2 ** attempt * 2)
    _last_hit[host] = time.time()
    key.write_text(html, encoding="utf-8")
    return html


def json_ld(html: str) -> list:
    """Every schema.org JSON-LD block on the page, flattened into one list."""
    out: list = []
    for raw in LD_JSON.findall(html):
        try:
            data = json.loads(raw)
        except json.JSONDecodeError:
            continue
        out.extend(data if isinstance(data, list) else [data])
    return out
