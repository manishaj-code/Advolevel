"""Identity and tenancy tables (spec 07 §3.1). Our DB is the source of truth for memberships."""

import uuid
from datetime import datetime

from sqlalchemy import (
    ARRAY,
    Boolean,
    CheckConstraint,
    DateTime,
    ForeignKey,
    Index,
    String,
    Text,
    UniqueConstraint,
    false,
    func,
    text,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.db import Base, IdMixin, TimestampMixin
from app.identity.permissions import Role

ORG_STATUSES = ("active", "past_due", "read_only", "suspended", "deleted")
MEMBERSHIP_STATUSES = ("active", "disabled")


def _in(column: str, values: tuple[str, ...]) -> str:
    return f"{column} IN ({', '.join(repr(v) for v in values)})"


class User(IdMixin, TimestampMixin, Base):
    __tablename__ = "users"
    __table_args__ = (
        # Partial so a deleted account's address can register again.
        Index(
            "uq_users_lower_email",
            func.lower(text("email")),
            unique=True,
            postgresql_where=text("deleted_at IS NULL"),
        ),
    )

    auth_provider_user_id: Mapped[str] = mapped_column(String(255), unique=True)
    email: Mapped[str] = mapped_column(String(320))
    email_verified: Mapped[bool] = mapped_column(Boolean, server_default=false())
    name: Mapped[str | None] = mapped_column(String(200))
    avatar_url: Mapped[str | None] = mapped_column(String(2048))
    is_platform_admin: Mapped[bool] = mapped_column(Boolean, server_default=false())
    platform_role: Mapped[str | None] = mapped_column(String(32))
    last_seen_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    deleted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))


class Organization(IdMixin, TimestampMixin, Base):
    __tablename__ = "organizations"
    __table_args__ = (CheckConstraint(_in("status", ORG_STATUSES), name="status"),)

    name: Mapped[str] = mapped_column(String(120))
    slug: Mapped[str] = mapped_column(String(80), unique=True)
    industry: Mapped[str | None] = mapped_column(String(120))
    size_band: Mapped[str | None] = mapped_column(String(16))
    website: Mapped[str | None] = mapped_column(String(2048))
    timezone: Mapped[str] = mapped_column(String(64), server_default="UTC")
    status: Mapped[str] = mapped_column(String(16), server_default="active")
    owner_user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id"))
    deleted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    purge_after: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))


class Membership(IdMixin, TimestampMixin, Base):
    __tablename__ = "memberships"
    __table_args__ = (
        UniqueConstraint("organization_id", "user_id"),
        Index(
            "uq_memberships_one_owner",
            "organization_id",
            unique=True,
            postgresql_where=text("role = 'owner'"),
        ),
        CheckConstraint(_in("role", tuple(r.value for r in Role)), name="role"),
        CheckConstraint(_in("status", MEMBERSHIP_STATUSES), name="status"),
    )

    organization_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("organizations.id"))
    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id"), index=True)
    role: Mapped[str] = mapped_column(String(16))
    capabilities: Mapped[list[str]] = mapped_column(ARRAY(Text), server_default="{}")
    status: Mapped[str] = mapped_column(String(16), server_default="active")
    joined_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    organization: Mapped[Organization] = relationship(lazy="raise")
    user: Mapped[User] = relationship(lazy="raise")


class Invitation(IdMixin, TimestampMixin, Base):
    __tablename__ = "invitations"
    __table_args__ = (
        Index("ix_invitations_organization_id_email", "organization_id", "email"),
        CheckConstraint(_in("role", ("admin", "member", "viewer")), name="role"),
    )

    organization_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("organizations.id"))
    email: Mapped[str] = mapped_column(String(320))  # stored lower-cased
    role: Mapped[str] = mapped_column(String(16))
    capabilities: Mapped[list[str]] = mapped_column(ARRAY(Text), server_default="{}")
    token_hash: Mapped[str] = mapped_column(String(64), unique=True)  # sha256 hex
    invited_by: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id"))
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    accepted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    revoked_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
