"""Database engine, session factory and model base. Tenant scoping (TenantContext + RLS) is M2."""

import uuid
from collections.abc import AsyncIterator
from datetime import datetime
from functools import lru_cache

from sqlalchemy import DateTime, MetaData, func
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy.pool import NullPool

from app.core.config import get_settings
from app.core.ids import new_id

# The API/worker database role (no BYPASSRLS). Every environment uses this name; migrations grant
# it table privileges explicitly.
APP_DB_ROLE = "advolevel_app"

# Deterministic constraint names keep Alembic autogenerate and downgrades predictable.
NAMING_CONVENTION = {
    "ix": "ix_%(table_name)s_%(column_0_N_name)s",
    "uq": "uq_%(table_name)s_%(column_0_N_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s",
}


class Base(DeclarativeBase):
    metadata = MetaData(naming_convention=NAMING_CONVENTION)
    # Fetch server defaults (created_at, status, ...) via RETURNING; lazy loads are not allowed
    # under asyncio.
    __mapper_args__ = {"eager_defaults": True}  # noqa: RUF012


class IdMixin:
    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=new_id)


class TimestampMixin:
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )


@lru_cache
def get_engine() -> AsyncEngine:
    settings = get_settings()
    # Tests open a new event loop per TestClient; pooled connections would outlive their loop.
    pool = {"poolclass": NullPool} if settings.app_env == "test" else {"pool_pre_ping": True}
    return create_async_engine(settings.sqlalchemy_url, **pool)


@lru_cache
def get_sessionmaker() -> async_sessionmaker[AsyncSession]:
    return async_sessionmaker(get_engine(), expire_on_commit=False)


async def get_session() -> AsyncIterator[AsyncSession]:
    """One session per request. Services commit explicitly; anything uncommitted rolls back."""
    async with get_sessionmaker()() as session:
        yield session
