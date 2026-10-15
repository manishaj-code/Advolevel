"""Liveness and readiness probes (spec 12 §6, spec 13 §5)."""

import asyncio
from functools import lru_cache
from pathlib import Path
from typing import Any

import structlog
from alembic.config import Config
from alembic.script import ScriptDirectory
from fastapi import APIRouter, Response, status
from redis.asyncio import Redis
from sqlalchemy import text

from app.core.config import get_settings
from app.core.db import get_engine

router = APIRouter(tags=["health"])
log = structlog.get_logger(__name__)

CHECK_TIMEOUT_SECONDS = 2.0
_ALEMBIC_INI = Path(__file__).resolve().parents[2] / "alembic.ini"


@lru_cache
def expected_migration_heads() -> frozenset[str]:
    config = Config(str(_ALEMBIC_INI))
    return frozenset(ScriptDirectory.from_config(config).get_heads())


async def check_database() -> dict[str, Any]:
    async with get_engine().connect() as conn:
        await conn.execute(text("SELECT 1"))
        has_table = (
            await conn.execute(text("SELECT to_regclass('public.alembic_version') IS NOT NULL"))
        ).scalar_one()
        current = (
            set((await conn.execute(text("SELECT version_num FROM alembic_version"))).scalars())
            if has_table
            else set()
        )
    expected = expected_migration_heads()
    at_head = current == set(expected)
    return {"ok": at_head, "migrations_at_head": at_head}


async def check_redis() -> dict[str, Any]:
    client = Redis.from_url(str(get_settings().redis_url))
    try:
        return {"ok": bool(await client.ping())}
    finally:
        await client.aclose()


async def _run(name: str, check: Any) -> dict[str, Any]:
    try:
        return dict(await asyncio.wait_for(check(), timeout=CHECK_TIMEOUT_SECONDS))
    except Exception as exc:
        log.warning("readiness_check_failed", check=name, error=type(exc).__name__)
        return {"ok": False, "error": type(exc).__name__}


@router.get("/healthz")
async def healthz() -> dict[str, str]:
    return {"status": "ok"}


@router.get("/readyz")
async def readyz(response: Response) -> dict[str, Any]:
    database, redis = await asyncio.gather(
        _run("database", check_database), _run("redis", check_redis)
    )
    ready = database["ok"] and redis["ok"]
    if not ready:
        response.status_code = status.HTTP_503_SERVICE_UNAVAILABLE
    return {
        "status": "ok" if ready else "unavailable",
        "checks": {"database": database, "redis": redis},
    }
