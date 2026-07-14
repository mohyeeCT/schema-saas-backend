import asyncio
import json

from fastapi.testclient import TestClient
from starlette.requests import Request

from main import _global_exception_handler, app


def test_health_returns_ok():
    client = TestClient(app)

    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok", "tool": "schema"}


def test_global_error_handler_keeps_cors_for_copypilot():
    request = Request({
        "type": "http",
        "method": "POST",
        "path": "/api/schema/run",
        "headers": [(b"origin", b"https://copypilot.app")],
        "query_string": b"",
        "server": ("testserver", 80),
        "client": ("testclient", 50000),
        "scheme": "http",
        "http_version": "1.1",
    })

    response = asyncio.run(_global_exception_handler(request, RuntimeError("boom")))

    assert response.status_code == 500
    assert json.loads(response.body) == {"detail": "Internal server error"}
    assert response.headers["access-control-allow-origin"] == "https://copypilot.app"
    assert response.headers["access-control-allow-credentials"] == "true"
