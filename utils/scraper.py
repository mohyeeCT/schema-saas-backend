from urllib.parse import urlparse

import requests


JINA_BASE = "https://r.jina.ai"
FIRECRAWL_SCRAPE_URL = "https://api.firecrawl.dev/v2/scrape"
_JINA_RENDER_TIMEOUT_SECONDS = 180
_JINA_REQUEST_TIMEOUT_SECONDS = 200
_JINA_CACHE_FALLBACK_TIMEOUT_SECONDS = 30
_FIRECRAWL_RENDER_TIMEOUT_MS = 120000
_FIRECRAWL_REQUEST_TIMEOUT_SECONDS = 135

_REMOVE_SELECTOR = ", ".join([
    "nav", "header", "footer", "aside",
    "#cart", ".cart", "[class*='cart']",
    "#header", "#footer", "#nav", "#sidebar",
    "[class*='sidebar']", "[class*='navigation']",
    "[class*='breadcrumb']", "[class*='cookie']",
    "[class*='popup']", "[class*='modal']",
    "[class*='newsletter']", "[class*='subscribe']",
    "form", "script", "style", "noscript", "iframe",
])


def _origin(url: str) -> str:
    parsed = urlparse(url)
    return f"{parsed.scheme}://{parsed.netloc}"


def build_scrape_targets(
    url: str,
    scrape_target: bool = True,
    scrape_homepage: bool = True,
    deep_scrape: bool = False,
) -> list[tuple[str, str]]:
    base = _origin(url)
    targets: list[tuple[str, str]] = []
    if scrape_target:
        targets.append(("target_page", url.rstrip("/") or url))
    if scrape_homepage:
        targets.append(("homepage", base))
    if deep_scrape:
        targets.append(("about", f"{base}/about-us"))
        targets.append(("contact", f"{base}/contact-us"))

    seen = set()
    unique_targets = []
    for key, target_url in targets:
        if target_url not in seen:
            unique_targets.append((key, target_url))
            seen.add(target_url)
    return unique_targets


def _request_cached_snapshot(url: str, headers: dict):
    fallback_headers = dict(headers)
    fallback_headers.pop("X-No-Cache", None)
    fallback_headers.pop("X-Remove-Selector", None)
    fallback_headers.pop("X-Timeout", None)
    return requests.get(
        f"{JINA_BASE}/{url}",
        headers=fallback_headers,
        timeout=_JINA_CACHE_FALLBACK_TIMEOUT_SECONDS,
    )


def scrape_with_jina(url: str, max_chars: int = 15000, api_key: str = "") -> str:
    headers = {
        "Accept": "text/plain",
        "X-Return-Format": "markdown",
        "X-Remove-Selector": _REMOVE_SELECTOR,
        "X-No-Cache": "true",
        "X-Timeout": str(_JINA_RENDER_TIMEOUT_SECONDS),
    }
    if api_key:
        headers["Authorization"] = f"Bearer {api_key}"

    try:
        response = requests.get(f"{JINA_BASE}/{url}", headers=headers, timeout=_JINA_REQUEST_TIMEOUT_SECONDS)
        if response.status_code in (400, 422):
            headers.pop("X-Remove-Selector", None)
            response = requests.get(f"{JINA_BASE}/{url}", headers=headers, timeout=_JINA_REQUEST_TIMEOUT_SECONDS)
    except requests.exceptions.Timeout:
        response = _request_cached_snapshot(url, headers)

    if 500 <= response.status_code < 600:
        response = _request_cached_snapshot(url, headers)
    response.raise_for_status()
    content = (response.text or "").strip()
    if not content and "X-No-Cache" in headers:
        cached_response = _request_cached_snapshot(url, headers)
        cached_response.raise_for_status()
        content = (cached_response.text or "").strip()
    if not content:
        raise ValueError("Jina returned empty content after cached fallback")
    return content[:max_chars]


def scrape_with_firecrawl(url: str, api_key: str, max_chars: int = 15000) -> str:
    if not api_key:
        raise ValueError("Firecrawl API key is not configured")
    response = requests.post(
        FIRECRAWL_SCRAPE_URL,
        headers={"Content-Type": "application/json", "Authorization": f"Bearer {api_key}"},
        json={
            "url": url,
            "formats": ["markdown"],
            "onlyMainContent": True,
            "onlyCleanContent": False,
            "maxAge": 0,
            "waitFor": 0,
            "timeout": _FIRECRAWL_RENDER_TIMEOUT_MS,
            "removeBase64Images": True,
            "blockAds": True,
            "proxy": "auto",
            "storeInCache": False,
        },
        timeout=_FIRECRAWL_REQUEST_TIMEOUT_SECONDS,
    )
    response.raise_for_status()
    data = response.json()
    page_data = data.get("data") if isinstance(data, dict) else None
    if not isinstance(data, dict) or data.get("success") is not True or not isinstance(page_data, dict):
        raise ValueError("Firecrawl returned an invalid response")
    content = (page_data.get("markdown") or "").strip()
    if not content:
        raise ValueError("Firecrawl returned empty content")
    return content[:max_chars]
