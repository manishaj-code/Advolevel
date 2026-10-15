"""Runs against the docker compose stack after `alembic upgrade head`:

uv run pytest -m integration
"""

import pytest
from fastapi.testclient import TestClient

pytestmark = pytest.mark.integration


def test_readyz_against_real_services(client: TestClient) -> None:
    response = client.get("/readyz")
    assert response.status_code == 200, response.json()
    assert response.json()["checks"]["database"]["migrations_at_head"] is True
