"""Identity business rules: WF-01 (users), WF-02 (org creation), WF-03 (invitations), spec 02.

Functions flush but never commit; routers commit once per request so each operation is atomic.
"""

import hashlib
import re
import secrets
import unicodedata
import uuid
from datetime import UTC, datetime, timedelta

from sqlalchemy import ColumnElement, func, select, update
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.ext.asyncio import AsyncSession

from app.core import audit
from app.core.config import get_settings
from app.core.entitlements import Limit, ensure_within, get_limit
from app.core.errors import AppError
from app.identity.models import Invitation, Membership, Organization, User
from app.identity.permissions import Role
from app.identity.provider import ProviderUser
from app.identity.schemas import (
    InvitationCreate,
    MemberUpdate,
    OrganizationCreate,
    OrganizationUpdate,
)

INVITATION_TTL = timedelta(days=7)  # WF-03
ORG_PURGE_AFTER = timedelta(days=30)  # BR-T-03 (PROPOSED, OQ-016)
_SLUG_MAX = 60


def now() -> datetime:
    return datetime.now(UTC)


# ---- users (WF-01) ------------------------------------------------------------------------


async def upsert_user(session: AsyncSession, provider_user: ProviderUser) -> User:
    """Idempotent on the provider user ID: repeated webhooks or JIT calls converge (AT-01-3)."""
    values = {
        "email": provider_user.email,
        "email_verified": provider_user.email_verified,
        "name": provider_user.name,
        "avatar_url": provider_user.avatar_url,
    }
    stmt = (
        insert(User)
        .values(auth_provider_user_id=provider_user.provider_user_id, **values)
        .on_conflict_do_update(
            index_elements=[User.auth_provider_user_id],
            set_={**values, "updated_at": func.now()},
        )
        .returning(User)
    )
    user = (await session.execute(stmt, execution_options={"populate_existing": True})).scalar_one()
    return user


async def delete_user(session: AsyncSession, provider_user_id: str) -> None:
    user = await session.scalar(select(User).where(User.auth_provider_user_id == provider_user_id))
    if user is None or user.deleted_at is not None:
        return
    user.deleted_at = now()
    await session.execute(
        update(Membership)
        .where(Membership.user_id == user.id, Membership.role != Role.OWNER)
        .values(status="disabled")
    )
    # An owner's org keeps its owner row; ownership transfer is a support task (KI-010).
    audit.record("user.deleted", actor_user_id=None, organization_id=None, target_id=user.id)


async def my_memberships(
    session: AsyncSession, user: User
) -> list[tuple[Membership, Organization]]:
    rows = await session.execute(
        select(Membership, Organization)
        .join(Organization, Organization.id == Membership.organization_id)
        .where(
            Membership.user_id == user.id,
            Membership.status == "active",
            Organization.deleted_at.is_(None),
        )
        .order_by(Organization.name)
    )
    return [(m, o) for m, o in rows]


# ---- organizations (WF-02) ----------------------------------------------------------------


def slugify(name: str) -> str:
    ascii_name = unicodedata.normalize("NFKD", name).encode("ascii", "ignore").decode()
    slug = re.sub(r"[^a-z0-9]+", "-", ascii_name.lower()).strip("-")
    return slug[:_SLUG_MAX].rstrip("-") or "org"


async def _unique_slug(session: AsyncSession, name: str) -> str:
    base = slugify(name)
    slug = base
    while await session.scalar(select(Organization.id).where(Organization.slug == slug)):
        slug = f"{base[: _SLUG_MAX - 7]}-{secrets.token_hex(3)}"
    return slug


async def create_organization(
    session: AsyncSession, user: User, data: OrganizationCreate
) -> Organization:
    max_orgs = get_settings().max_orgs_per_user
    if max_orgs >= 0:
        owned = await session.scalar(
            select(func.count())
            .select_from(Organization)
            .where(Organization.owner_user_id == user.id, Organization.deleted_at.is_(None))
        )
        if (owned or 0) >= max_orgs:
            raise AppError(
                402, "entitlement_exceeded", f"You can own at most {max_orgs} organizations."
            )

    org = Organization(
        name=data.name,
        slug=await _unique_slug(session, data.name),
        industry=data.industry,
        size_band=data.size_band,
        website=str(data.website) if data.website else None,
        timezone=data.timezone,
        owner_user_id=user.id,
    )
    session.add(org)
    await session.flush()
    session.add(
        Membership(organization_id=org.id, user_id=user.id, role=Role.OWNER, capabilities=[])
    )
    # TODO(M8): default governance policies. TODO(M11): trial subscription + Stripe customer job.
    await session.flush()
    audit.record("org.created", actor_user_id=user.id, organization_id=org.id)
    return org


async def update_organization(
    session: AsyncSession, actor: User, org: Organization, data: OrganizationUpdate
) -> Organization:
    changes = data.model_dump(exclude_unset=True)
    if "website" in changes and changes["website"] is not None:
        changes["website"] = str(changes["website"])
    if changes.get("name") is None:
        changes.pop("name", None)
    if changes.get("timezone") is None:
        changes.pop("timezone", None)
    for field, value in changes.items():
        setattr(org, field, value)
    await session.flush()
    audit.record(
        "org.updated",
        actor_user_id=actor.id,
        organization_id=org.id,
        metadata={"fields": sorted(changes)},
    )
    return org


async def delete_organization(session: AsyncSession, actor: User, org: Organization) -> None:
    """Soft delete; a purge job hard-deletes after the retention window (BR-T-03)."""
    org.status = "deleted"
    org.deleted_at = now()
    org.purge_after = org.deleted_at + ORG_PURGE_AFTER
    await session.flush()
    audit.record("org.deleted", actor_user_id=actor.id, organization_id=org.id)


async def transfer_ownership(
    session: AsyncSession, actor: User, org: Organization, new_owner_user_id: uuid.UUID
) -> None:
    if new_owner_user_id == actor.id:
        raise AppError(409, "conflict", "You already own this organization.")
    target = await session.scalar(
        select(Membership).where(
            Membership.organization_id == org.id,
            Membership.user_id == new_owner_user_id,
            Membership.status == "active",
        )
    )
    if target is None:
        raise AppError(404, "not_found", "The new owner must be an active member.")
    # Order matters: the one-owner unique index is checked per statement.
    await session.execute(
        update(Membership)
        .where(Membership.organization_id == org.id, Membership.role == Role.OWNER)
        .values(role=Role.ADMIN)
    )
    await session.execute(
        update(Membership).where(Membership.id == target.id).values(role=Role.OWNER)
    )
    org.owner_user_id = new_owner_user_id
    await session.flush()
    audit.record(
        "org.ownership_transferred",
        actor_user_id=actor.id,
        organization_id=org.id,
        target_type="user",
        target_id=new_owner_user_id,
    )


# ---- members ------------------------------------------------------------------------------


def _decode_cursor(cursor: str | None) -> uuid.UUID | None:
    if cursor is None:
        return None
    try:
        return uuid.UUID(cursor)
    except ValueError as exc:
        raise AppError(400, "validation_error", "Invalid cursor.") from exc


async def list_members(
    session: AsyncSession, org: Organization, *, limit: int, cursor: str | None
) -> tuple[list[tuple[Membership, User]], str | None]:
    query = (
        select(Membership, User)
        .join(User, User.id == Membership.user_id)
        .where(Membership.organization_id == org.id)
        .order_by(Membership.id)
        .limit(limit + 1)
    )
    after = _decode_cursor(cursor)
    if after is not None:
        query = query.where(Membership.id > after)
    rows = [(m, u) for m, u in await session.execute(query)]
    next_cursor = str(rows[limit - 1][0].id) if len(rows) > limit else None
    return rows[:limit], next_cursor


async def _member(session: AsyncSession, org: Organization, membership_id: uuid.UUID) -> Membership:
    membership = await session.scalar(
        select(Membership).where(
            Membership.id == membership_id, Membership.organization_id == org.id
        )
    )
    if membership is None:
        raise AppError(404, "not_found")
    return membership


async def update_member(
    session: AsyncSession,
    actor: User,
    org: Organization,
    membership_id: uuid.UUID,
    data: MemberUpdate,
) -> tuple[Membership, User]:
    membership = await _member(session, org, membership_id)
    if membership.role == Role.OWNER:
        raise AppError(409, "owner_protected", "Use ownership transfer to change the owner.")
    if data.role is not None:
        membership.role = data.role
    if data.capabilities is not None:
        membership.capabilities = sorted({c.value for c in data.capabilities})
    await session.flush()
    audit.record(
        "member.updated",
        actor_user_id=actor.id,
        organization_id=org.id,
        target_type="membership",
        target_id=membership.id,
        metadata={"role": membership.role, "capabilities": membership.capabilities},
    )
    user = await session.get_one(User, membership.user_id)
    return membership, user


async def remove_member(
    session: AsyncSession, actor: User, org: Organization, membership_id: uuid.UUID
) -> None:
    membership = await _member(session, org, membership_id)
    if membership.role == Role.OWNER:
        raise AppError(409, "owner_protected", "The owner cannot be removed.")
    await session.delete(membership)
    await session.flush()
    audit.record(
        "member.removed",
        actor_user_id=actor.id,
        organization_id=org.id,
        target_type="user",
        target_id=membership.user_id,
    )


# ---- invitations (WF-03) ------------------------------------------------------------------


def hash_token(token: str) -> str:
    return hashlib.sha256(token.encode()).hexdigest()


def _pending(org_id: uuid.UUID) -> tuple[ColumnElement[bool], ...]:
    return (
        Invitation.organization_id == org_id,
        Invitation.accepted_at.is_(None),
        Invitation.revoked_at.is_(None),
        Invitation.expires_at > now(),
    )


async def _seats_used(session: AsyncSession, org_id: uuid.UUID) -> int:
    members = await session.scalar(
        select(func.count())
        .select_from(Membership)
        .where(Membership.organization_id == org_id, Membership.status == "active")
    )
    invites = await session.scalar(
        select(func.count()).select_from(Invitation).where(*_pending(org_id))
    )
    return (members or 0) + (invites or 0)


async def create_invitation(
    session: AsyncSession, actor: User, org: Organization, data: InvitationCreate
) -> tuple[Invitation, str]:
    """Returns the invitation and the raw token (only ever emailed, never stored or logged)."""
    already_member = await session.scalar(
        select(Membership.id)
        .join(User, User.id == Membership.user_id)
        .where(Membership.organization_id == org.id, func.lower(User.email) == data.email)
    )
    if already_member:
        raise AppError(409, "already_member", "This person is already a member.")
    pending = await session.scalar(
        select(Invitation.id).where(*_pending(org.id), Invitation.email == data.email)
    )
    if pending:
        raise AppError(409, "invitation_pending", "An invitation is already pending; resend it.")
    ensure_within(
        Limit.SEATS_MAX,
        await _seats_used(session, org.id),
        await get_limit(org.id, Limit.SEATS_MAX),
    )

    token = secrets.token_urlsafe(32)
    invitation = Invitation(
        organization_id=org.id,
        email=data.email,
        role=data.role,
        capabilities=sorted({c.value for c in data.capabilities}),
        token_hash=hash_token(token),
        invited_by=actor.id,
        expires_at=now() + INVITATION_TTL,
    )
    session.add(invitation)
    await session.flush()
    audit.record(
        "invitation.created",
        actor_user_id=actor.id,
        organization_id=org.id,
        target_type="invitation",
        target_id=invitation.id,
        metadata={"role": data.role},
    )
    return invitation, token


async def list_invitations(
    session: AsyncSession, org: Organization, *, limit: int, cursor: str | None
) -> tuple[list[Invitation], str | None]:
    query = select(Invitation).where(*_pending(org.id)).order_by(Invitation.id).limit(limit + 1)
    after = _decode_cursor(cursor)
    if after is not None:
        query = query.where(Invitation.id > after)
    rows = list((await session.scalars(query)).all())
    next_cursor = str(rows[limit - 1].id) if len(rows) > limit else None
    return rows[:limit], next_cursor


async def _pending_invitation(
    session: AsyncSession, org: Organization, invitation_id: uuid.UUID
) -> Invitation:
    invitation = await session.scalar(
        select(Invitation).where(Invitation.id == invitation_id, *_pending(org.id))
    )
    if invitation is None:
        raise AppError(404, "not_found")
    return invitation


async def revoke_invitation(
    session: AsyncSession, actor: User, org: Organization, invitation_id: uuid.UUID
) -> None:
    invitation = await _pending_invitation(session, org, invitation_id)
    invitation.revoked_at = now()
    await session.flush()
    audit.record(
        "invitation.revoked",
        actor_user_id=actor.id,
        organization_id=org.id,
        target_type="invitation",
        target_id=invitation.id,
    )


async def resend_invitation(
    session: AsyncSession, actor: User, org: Organization, invitation_id: uuid.UUID
) -> tuple[Invitation, str]:
    """Rotates the token (the old link stops working) and restarts the 7-day expiry."""
    invitation = await _pending_invitation(session, org, invitation_id)
    token = secrets.token_urlsafe(32)
    invitation.token_hash = hash_token(token)
    invitation.expires_at = now() + INVITATION_TTL
    await session.flush()
    audit.record(
        "invitation.resent",
        actor_user_id=actor.id,
        organization_id=org.id,
        target_type="invitation",
        target_id=invitation.id,
    )
    return invitation, token


async def _by_token(
    session: AsyncSession, token: str, *, for_update: bool = False
) -> tuple[Invitation, Organization]:
    query = (
        select(Invitation, Organization)
        .join(Organization, Organization.id == Invitation.organization_id)
        .where(Invitation.token_hash == hash_token(token), Organization.deleted_at.is_(None))
    )
    if for_update:
        query = query.with_for_update(of=Invitation)
    row = (await session.execute(query)).first()
    if row is None:
        raise AppError(404, "invitation_not_found", "This invitation link is not valid.")
    invitation, org = row
    if invitation.revoked_at is not None:
        raise AppError(410, "invitation_revoked", "This invitation was withdrawn.")
    if invitation.accepted_at is not None:
        raise AppError(410, "invitation_used", "This invitation has already been used.")
    if invitation.expires_at <= now():
        raise AppError(410, "invitation_expired", "This invitation has expired.")
    return invitation, org


def mask_email(email: str) -> str:
    local, _, domain = email.partition("@")
    return f"{local[:1]}***@{domain}"


async def preview_invitation(
    session: AsyncSession, token: str
) -> tuple[Invitation, Organization, User | None]:
    invitation, org = await _by_token(session, token)
    inviter = await session.get(User, invitation.invited_by)
    return invitation, org, inviter


async def accept_invitation(session: AsyncSession, user: User, token: str) -> Membership:
    invitation, org = await _by_token(session, token, for_update=True)
    # AT-03-3: only the invited address, and only once it is verified, can accept.
    if not user.email_verified or user.email.lower() != invitation.email:
        raise AppError(
            403,
            "invitation_email_mismatch",
            f"This invitation is for {mask_email(invitation.email)}. "
            "Sign in with that address to accept it.",
        )
    existing = await session.scalar(
        select(Membership).where(
            Membership.organization_id == org.id, Membership.user_id == user.id
        )
    )
    if existing is not None:
        raise AppError(409, "already_member", "You are already a member of this organization.")

    membership = Membership(
        organization_id=org.id,
        user_id=user.id,
        role=invitation.role,
        capabilities=list(invitation.capabilities),
    )
    session.add(membership)
    invitation.accepted_at = now()
    await session.flush()
    audit.record(
        "invitation.accepted",
        actor_user_id=user.id,
        organization_id=org.id,
        target_type="membership",
        target_id=membership.id,
        metadata={"role": invitation.role},
    )
    return membership
