import json
import re
from typing import Any


def extract_schema_json(text: str) -> dict[str, Any]:
    tagged = re.search(r"<schema>([\s\S]*?)</schema>", text, re.IGNORECASE)
    candidate = tagged.group(1).strip() if tagged else ""

    if not candidate:
        bare = re.search(r"\{[\s\S]*?\"@context\"[\s\S]*\}", text)
        candidate = bare.group(0).strip() if bare else ""

    if not candidate:
        raise ValueError("No schema JSON found in provider response.")

    try:
        parsed = json.loads(candidate)
    except json.JSONDecodeError as exc:
        raise ValueError("Provider returned schema text that is not valid JSON.") from exc

    if not isinstance(parsed, dict):
        raise ValueError("Schema JSON must be an object.")

    return parsed


def wrap_json_ld(schema: dict[str, Any]) -> str:
    raw = json.dumps(schema, ensure_ascii=False, indent=2)
    return f'<script type="application/ld+json">\n{raw}\n</script>'
