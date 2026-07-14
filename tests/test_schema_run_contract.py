from models import SchemaJobRequest
from routers.schema import build_initial_job_record


def test_initial_job_record_uses_schema_tool_and_strips_secrets():
    request = SchemaJobRequest(
        name="Schema Job",
        rows=[{"url": "https://example.com"}],
        settings={
            "provider": "Claude",
            "schema_type": "Organization",
        },
    )

    record = build_initial_job_record("user-1", request)

    assert record["user_id"] == "user-1"
    assert record["tool"] == "schema"
    assert record["status"] == "running"
    assert record["settings"]["schema_type"] == "Organization"
    assert record["total_rows"] == 1
    assert record["completed_rows"] == 0
    assert record["failed_rows"] == 0
    assert record["current_step"] == "Starting..."
    assert "progress" not in record
    assert "api_key" not in record["settings"]
    assert "dfs_password" not in record["settings"]
    assert "jina_api_key" not in record["settings"]
    assert "firecrawl_api_key" not in record["settings"]
