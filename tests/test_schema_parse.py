import pytest

from utils.schema_parse import extract_schema_json, wrap_json_ld


def test_extracts_schema_tagged_json():
    text = '<schema>{"@context":"https://schema.org","@type":"Organization","name":"Acme"}</schema>'

    parsed = extract_schema_json(text)

    assert parsed["@type"] == "Organization"
    assert parsed["name"] == "Acme"


def test_extracts_bare_json_with_context():
    text = 'Here it is: {"@context":"https://schema.org","@type":"WebSite","url":"https://example.com"}'

    parsed = extract_schema_json(text)

    assert parsed["@type"] == "WebSite"


def test_rejects_invalid_json():
    with pytest.raises(ValueError, match="valid JSON"):
        extract_schema_json("<schema>{bad json}</schema>")


def test_wrap_json_ld_outputs_script_block():
    script = wrap_json_ld({"@context": "https://schema.org", "@type": "Organization"})

    assert script.startswith('<script type="application/ld+json">')
    assert script.endswith("</script>")
    assert '"@type": "Organization"' in script
