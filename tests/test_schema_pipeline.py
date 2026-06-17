from models import SchemaRow, SchemaSettings
from routers.schema import process_schema_row


def test_process_schema_row_returns_json_and_script(monkeypatch):
    monkeypatch.setattr("routers.schema.scrape_sources", lambda row, settings: {"target_page": "Acme Corp"})
    monkeypatch.setattr("routers.schema.fetch_optional_serp", lambda row, settings: "")
    monkeypatch.setattr(
        "routers.schema.generate_schema_text",
        lambda provider, api_key, prompt, model=None: '<schema>{"@context":"https://schema.org","@type":"Organization","name":"Acme Corp"}</schema>',
    )

    result = process_schema_row(
        SchemaRow(url="https://example.com"),
        SchemaSettings(schema_type="Organization"),
        {"api_key": "secret"},
    )

    assert result["status"] == "complete"
    assert result["schema"]["@type"] == "Organization"
    assert result["schema_json"].startswith("{")
    assert result["schema_script"].startswith('<script type="application/ld+json">')
    assert result["source_summary"]["scraped_sections"] == ["target_page"]
