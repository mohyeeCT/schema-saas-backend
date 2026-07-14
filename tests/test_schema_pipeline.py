from models import SchemaRow, SchemaSettings
from models import SchemaJobRequest
from routers import schema
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


class _Response:
    def __init__(self, data):
        self.data = data


class _Query:
    def __init__(self, sb):
        self.sb = sb
        self.filters = []
        self.payload = None

    def select(self, _columns):
        return self

    def update(self, payload):
        self.payload = payload
        return self

    def eq(self, column, value):
        self.filters.append((column, value))
        return self

    def execute(self):
        if self.payload is not None:
            self.sb.updates.append(self.payload)
            self.sb.update_queries.append({
                "payload": self.payload,
                "filters": list(self.filters),
            })
            self.sb.job.update(self.payload)
            return _Response([self.sb.job])
        return _Response([self.sb.job])


class _Supabase:
    def __init__(self, status="cancelled"):
        self.job = {"id": "job-1", "user_id": "user-1", "tool": "schema", "status": status}
        self.updates = []
        self.update_queries = []

    def table(self, _name):
        return _Query(self)


def test_schema_worker_stops_when_job_is_already_cancelled(monkeypatch):
    sb = _Supabase(status="cancelled")
    calls = []
    monkeypatch.setattr("routers.schema.hydrate_job_settings", lambda sb, user_id, settings: {})
    monkeypatch.setattr("routers.schema.process_schema_row", lambda row, settings, runtime: calls.append(row) or {"status": "complete"})

    schema._run_schema_job(
        sb,
        "user-1",
        "job-1",
        SchemaJobRequest(name="Schema", rows=[SchemaRow(url="https://example.com")], settings=SchemaSettings()),
    )

    assert calls == []
    assert sb.job["status"] == "cancelled"


def test_schema_worker_scopes_background_updates_to_user_and_schema_tool(monkeypatch):
    sb = _Supabase(status="running")
    monkeypatch.setattr("routers.schema.hydrate_job_settings", lambda sb, user_id, settings: {})
    monkeypatch.setattr(
        "routers.schema.process_schema_row",
        lambda row, settings, runtime: {
            "url": str(row.url),
            "status": "complete",
            "schema_type": settings.schema_type,
            "schema": {"@context": "https://schema.org", "@type": "Organization"},
            "schema_json": "{}",
            "schema_script": "<script>{}</script>",
            "source_summary": {"scraped_sections": [], "serp_used": False},
            "error": None,
        },
    )

    schema._run_schema_job(
        sb,
        "user-1",
        "job-1",
        SchemaJobRequest(name="Schema", rows=[SchemaRow(url="https://example.com")], settings=SchemaSettings()),
    )

    assert sb.update_queries
    for query in sb.update_queries:
        assert ("id", "job-1") in query["filters"]
        assert ("user_id", "user-1") in query["filters"]
        assert ("tool", "schema") in query["filters"]
        assert "progress" not in query["payload"]

    final_update = sb.updates[-1]
    assert final_update["status"] == "complete"
    assert final_update["completed_rows"] == 1
    assert final_update["failed_rows"] == 0
    assert final_update["current_step"] == "Done."


def test_schema_worker_records_failed_rows_with_supported_terminal_status(monkeypatch):
    sb = _Supabase(status="running")
    monkeypatch.setattr("routers.schema.hydrate_job_settings", lambda sb, user_id, settings: {})
    monkeypatch.setattr(
        "routers.schema.process_schema_row",
        lambda row, settings, runtime: {
            "url": str(row.url),
            "status": "failed",
            "error": "Provider unavailable",
        },
    )

    schema._run_schema_job(
        sb,
        "user-1",
        "job-1",
        SchemaJobRequest(name="Schema", rows=[SchemaRow(url="https://example.com")], settings=SchemaSettings()),
    )

    final_update = sb.updates[-1]
    assert final_update["status"] == "complete"
    assert final_update["completed_rows"] == 1
    assert final_update["failed_rows"] == 1
    assert final_update["current_step"] == "Done with 1 failed row(s)."
