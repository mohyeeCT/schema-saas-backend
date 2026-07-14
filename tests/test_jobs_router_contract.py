from pathlib import Path

from routers.jobs import build_duplicate_job_record


def test_jobs_router_filters_schema_tool_only():
    source = Path("routers/jobs.py").read_text()

    assert '.eq("tool", "schema")' in source
    assert '"tool": "schema"' in source
    assert '"page-copy"' not in source
    assert '"faq"' not in source


def test_duplicate_job_record_uses_shared_job_columns():
    record = build_duplicate_job_record(
        "user-1",
        {
            "name": "Restaurant schema",
            "rows": [{"url": "https://example.com"}],
            "settings": {"schema_type": "Restaurant"},
            "results": [{"status": "failed", "error": "Provider unavailable"}],
        },
    )

    assert record["status"] == "complete"
    assert record["total_rows"] == 1
    assert record["completed_rows"] == 1
    assert record["failed_rows"] == 1
    assert record["current_step"] == "Duplicated."
    assert "progress" not in record
