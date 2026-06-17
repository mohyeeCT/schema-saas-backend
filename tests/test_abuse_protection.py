import pytest
from fastapi import HTTPException

from abuse_protection import enforce_job_start, enforce_rate_limit


class FakeSupabase:
    def __init__(self, rows=None, rpc_rows=None, rpc_error=None):
        self.rows = rows or []
        self.rpc_rows = rpc_rows or [{"allowed": True, "retry_after_seconds": 0}]
        self.rpc_error = rpc_error

    def table(self, name):
        return self

    def select(self, value):
        return self

    def eq(self, key, value):
        self.rows = [row for row in self.rows if row.get(key) == value]
        return self

    def in_(self, key, values):
        self.rows = [row for row in self.rows if row.get(key) in values]
        return self

    def execute(self):
        return type("Response", (), {"data": self.rows})()

    def rpc(self, name, params):
        if self.rpc_error:
            raise self.rpc_error
        return type("Rpc", (), {"execute": lambda _self: type("Response", (), {"data": self.rpc_rows})()})()


def test_schema_job_row_limit_is_25():
    enforce_job_start(FakeSupabase(), "user-1", "schema", 25, 25)

    with pytest.raises(HTTPException):
        enforce_job_start(FakeSupabase(), "user-1", "schema", 26, 25)


def test_schema_blocks_second_active_job():
    active = FakeSupabase([{
        "id": "job-1",
        "user_id": "user-1",
        "tool": "schema",
        "status": "running",
    }])

    with pytest.raises(HTTPException):
        enforce_job_start(active, "user-1", "schema", 1, 25)


def test_rate_limit_raises_retry_after_when_denied():
    limited = FakeSupabase(rpc_rows=[{"allowed": False, "retry_after_seconds": 181}])

    with pytest.raises(HTTPException) as exc:
        enforce_rate_limit(limited, "user-1", "schema", "job-create", 10)

    assert exc.value.status_code == 429
    assert "Please wait 4 minutes" in exc.value.detail


def test_rate_limit_fails_open_on_rpc_error():
    enforce_rate_limit(
        FakeSupabase(rpc_error=RuntimeError("rpc unavailable")),
        "user-1",
        "schema",
        "job-create",
        10,
    )
