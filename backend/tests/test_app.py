from typing import Any

import pytest
import sentry_sdk
from fastapi import FastAPI
from fastapi.testclient import TestClient
from structlog.testing import capture_logs

from app.core import health
from app.core.config import Settings
from app.core.telemetry import sentry_before_send
from app.identity.deps import require_platform_admin
from app.main import create_app
from tests.conftest import make_settings


def test_healthz(client: TestClient) -> None:
    response = client.get("/healthz")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_request_id_is_generated(client: TestClient) -> None:
    response = client.get("/healthz")
    assert len(response.headers["X-Request-Id"]) == 32


def test_well_formed_request_id_is_echoed(client: TestClient) -> None:
    response = client.get("/healthz", headers={"X-Request-Id": "req-abc-123456"})
    assert response.headers["X-Request-Id"] == "req-abc-123456"


def test_malformed_request_id_is_replaced(client: TestClient) -> None:
    response = client.get("/healthz", headers={"X-Request-Id": "bad id <script>"})
    assert response.headers["X-Request-Id"] != "bad id <script>"


def test_access_log_uses_full_route_template(client: TestClient) -> None:
    with capture_logs() as logs:
        client.post("/api/v1/admin/debug/raise")
        client.get("/api/v1/nope/12345")
    routes = [e["route"] for e in logs if e["event"] == "request"]
    assert routes == ["/api/v1/admin/debug/raise", "<unmatched>"]


def test_not_found_is_problem_json(client: TestClient) -> None:
    response = client.get("/api/v1/nope", headers={"X-Request-Id": "req-404-000000"})
    assert response.status_code == 404
    assert response.headers["content-type"] == "application/problem+json"
    body = response.json()
    assert body["code"] == "not_found"
    assert body["request_id"] == "req-404-000000"


def test_debug_endpoint_hidden_without_platform_admin(client: TestClient) -> None:
    # 401 (no token), or 503 when no AUTH_ISSUER is configured; never the raising handler's 500.
    assert client.post("/api/v1/admin/debug/raise").status_code in (401, 503)


def test_unhandled_error_is_500_problem_with_request_id(
    app: FastAPI, client: TestClient, monkeypatch: pytest.MonkeyPatch
) -> None:
    captured: list[BaseException] = []
    monkeypatch.setattr(sentry_sdk, "capture_exception", captured.append)
    app.dependency_overrides[require_platform_admin] = lambda: None

    response = client.post("/api/v1/admin/debug/raise", headers={"X-Request-Id": "req-500-000000"})

    assert response.status_code == 500
    assert response.headers["X-Request-Id"] == "req-500-000000"
    body = response.json()
    assert body["code"] == "internal_error"
    assert body["request_id"] == "req-500-000000"
    assert "MON-01" not in response.text  # no internals leaked
    assert len(captured) == 1


def test_debug_endpoint_absent_when_disabled() -> None:
    with TestClient(create_app(make_settings(debug_endpoints_enabled=False))) as c:
        assert c.post("/api/v1/admin/debug/raise").status_code == 404


def test_production_rejects_debug_endpoints() -> None:
    with pytest.raises(ValueError, match="DEBUG_ENDPOINTS_ENABLED"):
        Settings(
            app_env="production",
            debug_endpoints_enabled=True,
            database_url="postgresql://u:p@db/x",
            redis_url="redis://r:6379/0",
            SENTRY_DSN="https://k@sentry.example/1",
        )


def test_cors_origins_parse_from_comma_list(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("CORS_ORIGINS", "http://a.test, http://b.test")
    assert Settings().cors_origins == ["http://a.test", "http://b.test"]


def test_sentry_before_send_scrubs_and_tags() -> None:
    event: dict[str, Any] = {
        "request": {"headers": {"Authorization": "Bearer x"}},
        "extra": {"email": "a@b.co"},
    }
    result = sentry_before_send(event, {})
    assert result is not None
    assert result["request"]["headers"]["Authorization"] == "[REDACTED]"
    assert result["extra"]["email"] == "[REDACTED]"


def test_readyz_reports_failing_dependencies(
    client: TestClient, monkeypatch: pytest.MonkeyPatch
) -> None:
    async def ok() -> dict[str, Any]:
        return {"ok": True}

    async def down() -> dict[str, Any]:
        raise ConnectionError("redis down")

    monkeypatch.setattr(health, "check_database", ok)
    monkeypatch.setattr(health, "check_redis", down)

    response = client.get("/readyz")
    assert response.status_code == 503
    assert response.json()["checks"]["redis"] == {"ok": False, "error": "ConnectionError"}


def test_readyz_ok_when_dependencies_ok(
    client: TestClient, monkeypatch: pytest.MonkeyPatch
) -> None:
    async def ok() -> dict[str, Any]:
        return {"ok": True}

    monkeypatch.setattr(health, "check_database", ok)
    monkeypatch.setattr(health, "check_redis", ok)
    assert client.get("/readyz").status_code == 200


def test_migration_heads_resolve() -> None:
    assert len(health.expected_migration_heads()) == 1  # linear history (spec 12 §5)
