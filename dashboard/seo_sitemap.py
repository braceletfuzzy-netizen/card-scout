"""CAMEL FIRE-7 — sitemap the whole product: generate sitemap.xml from the registry
(757 /price/<player>/<lane> URLs + /bands + /lists/monthly + the landing + deals +
pricing). Replaces the hardcoded 3-URL template. Reads the ONE-WAY registry feed,
renders fresh at request time (cached 10 min), caps at 1000 URLs (Sitemap-protocol
limit is 50k, so we're safe)."""
from __future__ import annotations

import json
import time
from pathlib import Path

DASH_DIR = Path(__file__).resolve().parent
REGISTRY = DASH_DIR / "registry" / "card_page_registry.json"
BASE_URL = "https://cardscout.pro"
_CACHE = {"ts": 0.0, "urls": []}
_LOCK = __import__("threading").Lock()

sitemap_bp = None


SITEMAP_TEMPLATE = """<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
{% for u in urls %}
  <url>
    <loc>{{ u[0] }}</loc>
    <changefreq>{{ u[1] }}</changefreq>
    <priority>{{ u[2] }}</priority>
  </url>
{% endfor %}
</urlset>
"""


def _build_urls() -> list[tuple[str, str, str]]:
    with _LOCK:
        if time.time() - _CACHE["ts"] < 600 and _CACHE["urls"]:
            return _CACHE["urls"]
        urls: list[tuple[str, str, str]] = [
            (f"{BASE_URL}/", "weekly", "1.0"),
            (f"{BASE_URL}/bands", "weekly", "0.9"),
            (f"{BASE_URL}/deals", "daily", "0.8"),
            (f"{BASE_URL}/trending", "daily", "0.7"),
            (f"{BASE_URL}/pricing", "weekly", "0.6"),
            (f"{BASE_URL}/lists/monthly", "daily", "0.8"),
        ]
        try:
            reg = json.loads(REGISTRY.read_text(encoding="utf-8"))
            for L in reg.get("lanes", []):
                ps, ls = L.get("player_slug", ""), L.get("slug", "")
                if ps and ls:
                    urls.append((f"{BASE_URL}/price/{ps}/{ls}", "weekly", "0.7"))
        except (OSError, ValueError):
            pass
        urls = urls[:1000]
        _CACHE["ts"] = time.time()
        _CACHE["urls"] = urls
        return urls


