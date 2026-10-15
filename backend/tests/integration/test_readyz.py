import pytest

from tests.integration.conftest import Harness

pytestmark = pytest.mark.integration


def test_readyz_against_real_services(harness: Harness) -> None:
    response = harness.client.get("/readyz")
    assert response.status_code == 200, response.json()
    assert response.json()["checks"]["database"]["migrations_at_head"] is True
