"""Integration harness (needs `docker compose up` locally; service containers in CI).

A throwaway ``<db>_test`` database is created and migrated once per session. The API connects as
the restricted app role, so a missing GRANT fails tests just as it would in production.
"""

import os
import uuid
from collections.abc import Iterator
from dataclasses import dataclass
from typing import Any

import psycopg
import pytest
from alembic import command
from alembic.config import Config
from fastapi import FastAPI
from fastapi.testclient import TestClient
from httpx import Response
from psycopg import sql
from pydantic import SecretStr
from sqlalchemy.engine import URL, make_url

from app.core import db
from app.core.config import get_settings
from app.core.db import APP_DB_ROLE
from app.core.health import _ALEMBIC_INI
from app.main import create_app
from tests.auth_helpers import (
    WEBHOOK_SECRET,
    FakeIdentityProvider,
    RecordingEmailSender,
    SigningKey,
    make_verifier,
)

pytestmark = pytest.mark.integration

TABLES = ("invitations", "memberships", "organizations", "users")


def _libpq(url: str | URL) -> str:
    return (
        (url if isinstance(url, URL) else make_url(url))
        .set(drivername="postgresql")
        .render_as_string(hide_password=False)
    )


@pytest.fixture(scope="session")
def database() -> Iterator[str]:
    settings = get_settings()
    if settings.database_migration_url is None:
        pytest.fail("DATABASE_MIGRATION_URL (owner role) is required for integration tests")
    owner = make_url(str(settings.database_migration_url))
    app_url = make_url(str(settings.database_url))
    test_db = f"{owner.database}_test"

    with psycopg.connect(_libpq(owner), autocommit=True) as conn:
        conn.execute(
            sql.SQL("DROP DATABASE IF EXISTS {} WITH (FORCE)").format(sql.Identifier(test_db))
        )
        conn.execute(sql.SQL("CREATE DATABASE {}").format(sql.Identifier(test_db)))
        conn.execute(
            sql.SQL("GRANT CONNECT ON DATABASE {} TO {}").format(
                sql.Identifier(test_db), sql.Identifier(APP_DB_ROLE)
            )
        )

    owner_test = owner.set(database=test_db).render_as_string(hide_password=False)
    os.environ["DATABASE_MIGRATION_URL"] = owner_test
    os.environ["DATABASE_URL"] = app_url.set(database=test_db).render_as_string(hide_password=False)
    for cached in (get_settings, db.get_engine, db.get_sessionmaker):
        cached.cache_clear()
    command.upgrade(Config(str(_ALEMBIC_INI)), "head")
    yield owner_test


@pytest.fixture
def owner_conn(database: str) -> Iterator[psycopg.Connection[Any]]:
    with psycopg.connect(_libpq(database), autocommit=True) as conn:
        conn.execute(f"TRUNCATE {', '.join(TABLES)} CASCADE")
        yield conn


@dataclass
class Harness:
    app: FastAPI
    client: TestClient
    key: SigningKey
    idp: FakeIdentityProvider
    mail: RecordingEmailSender
    owner_conn: psycopg.Connection[Any]

    def user(self, name: str, *, verified: bool = True) -> dict[str, str]:
        """Registers ``name`` with the fake Clerk and returns its auth headers."""
        subject = f"user_{name}"
        self.idp.add(subject, f"{name}@example.com", verified=verified, name=name.title())
        return {"Authorization": f"Bearer {self.key.token(subject)}"}

    def me(self, headers: dict[str, str]) -> dict[str, Any]:
        response = self.client.get("/api/v1/me", headers=headers)
        assert response.status_code == 200, response.text
        data: dict[str, Any] = response.json()
        return data

    def create_org(self, headers: dict[str, str], name: str = "Acme Legal") -> dict[str, Any]:
        response = self.client.post("/api/v1/orgs", json={"name": name}, headers=headers)
        assert response.status_code == 201, response.text
        data: dict[str, Any] = response.json()
        return data

    def invite(
        self, headers: dict[str, str], org_id: str, email: str, role: str = "member"
    ) -> tuple[Response, str | None]:
        """Returns the response and the token from the captured email (if one was sent)."""
        before = len(self.mail.sent)
        response = self.client.post(
            "/api/v1/invitations",
            json={"email": email, "role": role},
            headers={**headers, "X-Org-Id": org_id},
        )
        token = None
        if len(self.mail.sent) > before:
            token = self.mail.sent[-1].body_text.split("#token=")[1].split()[0]
        return response, token

    def join(self, owner: dict[str, str], org_id: str, name: str, role: str) -> dict[str, str]:
        headers = self.user(name)
        response, token = self.invite(owner, org_id, f"{name}@example.com", role)
        assert response.status_code == 201, response.text
        accepted = self.client.post(
            "/api/v1/invitations/accept", json={"token": token}, headers=headers
        )
        assert accepted.status_code == 200, accepted.text
        return headers


@pytest.fixture
def harness(
    owner_conn: psycopg.Connection[Any], monkeypatch: pytest.MonkeyPatch
) -> Iterator[Harness]:
    # Code reads the cached settings instance, so tests patch that instance (undone per test).
    settings = get_settings()
    monkeypatch.setattr(settings, "auth_webhook_secret", SecretStr(WEBHOOK_SECRET))
    monkeypatch.setattr(settings, "debug_endpoints_enabled", True)
    app = create_app(settings)
    key = SigningKey.generate()
    idp, mail = FakeIdentityProvider(), RecordingEmailSender()
    app.state.token_verifier = make_verifier(key)
    app.state.identity_provider = idp
    app.state.email_sender = mail
    with TestClient(app, raise_server_exceptions=False) as client:
        yield Harness(app, client, key, idp, mail, owner_conn)


def new_uuid() -> str:
    return str(uuid.uuid4())
