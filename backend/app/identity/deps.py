"""Authentication and authorization dependencies (spec 10 §1-2, BR-T-02)."""

import uuid
from collections.abc import Awaitable, Callable
from dataclasses import dataclass
from typing import Annotated

import structlog
from fastapi import Depends, Header, Request
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.db import get_session
from app.core.errors import AppError
from app.core.security import InvalidTokenError, Principal, TokenVerifier
from app.identity import service
from app.identity.models import Membership, Organization, User
from app.identity.permissions import Permission, has_permission
from app.identity.provider import IdentityProvider, ProviderUnavailableError

log = structlog.get_logger(__name__)

Session = Annotated[AsyncSession, Depends(get_session)]


def _unauthenticated(detail: str = "Sign in to continue.") -> AppError:
    return AppError(401, "unauthenticated", detail)


async def get_principal(
    request: Request, authorization: Annotated[str | None, Header()] = None
) -> Principal:
    verifier: TokenVerifier | None = request.app.state.token_verifier
    if verifier is None:
        raise AppError(503, "auth_not_configured", "Authentication is not configured.")
    scheme, _, token = (authorization or "").partition(" ")
    if scheme.lower() != "bearer" or not token:
        raise _unauthenticated()
    try:
        return await verifier.verify(token.strip())
    except InvalidTokenError as exc:
        log.info("token_rejected", reason=str(exc))
        raise _unauthenticated() from exc


async def get_current_user(
    request: Request,
    session: Session,
    principal: Annotated[Principal, Depends(get_principal)],
) -> User:
    user = await session.scalar(select(User).where(User.auth_provider_user_id == principal.subject))
    if user is None:
        # Webhook not processed yet (or unreachable locally): provision just in time.
        provider: IdentityProvider | None = request.app.state.identity_provider
        if provider is None:
            raise AppError(503, "auth_not_configured", "Authentication is not configured.")
        try:
            provider_user = await provider.get_user(principal.subject)
        except ProviderUnavailableError as exc:
            raise AppError(503, "provider_unavailable", "Please try again shortly.") from exc
        if provider_user is None:
            raise _unauthenticated()
        user = await service.upsert_user(session, provider_user)
        await session.commit()
    if user.deleted_at is not None:
        raise _unauthenticated()
    if not user.email_verified:
        raise AppError(403, "email_unverified", "Verify your email address to continue.")
    return user


CurrentUser = Annotated[User, Depends(get_current_user)]


async def require_platform_admin(user: CurrentUser) -> User:
    """Platform routes (BR-PA-01). Platform roles are never granted through memberships."""
    if not user.is_platform_admin:
        raise AppError(404, "not_found")
    return user


@dataclass(frozen=True)
class OrgContext:
    user: User
    organization: Organization
    membership: Membership

    def can(self, permission: Permission) -> bool:
        return has_permission(self.membership.role, self.membership.capabilities, permission)


async def _load_context(session: AsyncSession, user: User, org_id: uuid.UUID) -> OrgContext | None:
    row = (
        await session.execute(
            select(Membership, Organization)
            .join(Organization, Organization.id == Membership.organization_id)
            .where(
                Membership.organization_id == org_id,
                Membership.user_id == user.id,
                Membership.status == "active",
                Organization.deleted_at.is_(None),
            )
        )
    ).first()
    if row is None:
        return None
    membership, organization = row
    return OrgContext(user=user, organization=organization, membership=membership)


async def get_org_context(
    session: Session,
    user: CurrentUser,
    x_org_id: Annotated[uuid.UUID, Header(description="Active organization (BR-T-02)")],
) -> OrgContext:
    """Tenant routes: the active org comes from ``X-Org-Id`` and is checked on every request."""
    context = await _load_context(session, user, x_org_id)
    if context is None:
        raise AppError(403, "org_membership_required", "You are not a member of this organization.")
    return context


async def get_path_org_context(
    session: Session, user: CurrentUser, org_id: uuid.UUID
) -> OrgContext:
    """``/orgs/{org_id}`` routes: non-members get 404 so other tenants' IDs are not confirmed."""
    context = await _load_context(session, user, org_id)
    if context is None:
        raise AppError(404, "not_found")
    return context


def _guard(
    permission: Permission, source: Callable[..., Awaitable[OrgContext]]
) -> Callable[..., Awaitable[OrgContext]]:
    async def dependency(context: Annotated[OrgContext, Depends(source)]) -> OrgContext:
        if not context.can(permission):
            raise AppError(403, "forbidden", "Your role does not allow this action.")
        return context

    return dependency


def require_permission(permission: Permission) -> Callable[..., Awaitable[OrgContext]]:
    """Layer 1 of spec 10 §2 for ``X-Org-Id`` routes."""
    return _guard(permission, get_org_context)


def require_org_permission(permission: Permission) -> Callable[..., Awaitable[OrgContext]]:
    """Same as ``require_permission`` for ``/orgs/{org_id}`` routes."""
    return _guard(permission, get_path_org_context)
