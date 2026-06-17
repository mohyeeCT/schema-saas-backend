from urllib.parse import urlparse

import requests

JINA_BASE = "https://r.jina.ai"

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


def scrape_with_jina(url: str, max_chars: int = 15000) -> str:
    headers = {
        "Accept": "text/plain",
        "X-Return-Format": "markdown",
        "X-Remove-Selector": _REMOVE_SELECTOR,
    }
    response = requests.get(f"{JINA_BASE}/{url}", headers=headers, timeout=35)
    if not response.ok and "X-Remove-Selector" in headers:
        headers.pop("X-Remove-Selector", None)
        response = requests.get(f"{JINA_BASE}/{url}", headers=headers, timeout=35)
    response.raise_for_status()
    return response.text[:max_chars]


def scrape_with_firecrawl(url: str, api_key: str, max_chars: int = 15000) -> str:
    response = requests.post(
        "https://api.firecrawl.dev/v1/scrape",
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}",
        },
        json={
            "url": url,
            "formats": ["markdown"],
            "onlyMainContent": False,
            "waitFor": 3000,
        },
        timeout=60,
    )
    response.raise_for_status()
    data = response.json()
    content = (data.get("data") or {}).get("markdown") or data.get("markdown") or ""
    return content[:max_chars]
