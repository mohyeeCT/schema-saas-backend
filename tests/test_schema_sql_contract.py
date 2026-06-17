from pathlib import Path


def test_schema_sql_includes_schema_tool():
    sql = Path("schema.sql").read_text()

    assert "'schema'" in sql
    assert "jobs" in sql
    assert "tool" in sql


def test_migration_adds_schema_tool_constraint():
    migration = Path("migrations/20260617_schema_tool_jobs.sql").read_text()

    assert "'schema'" in migration
    assert "jobs_tool_check" in migration
