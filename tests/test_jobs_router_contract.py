from pathlib import Path


def test_jobs_router_filters_schema_tool_only():
    source = Path("routers/jobs.py").read_text()

    assert '.eq("tool", "schema")' in source
    assert '"tool": "schema"' in source
    assert '"page-copy"' not in source
    assert '"faq"' not in source
