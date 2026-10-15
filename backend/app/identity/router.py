"""Identity and organization endpoints (spec 08 §2, WF-01…03)."""

import uuid
from typing import Annotated

import structlog
from fastapi import APIRouter, BackgroundTasks, Depends, Query, Request, Response, status
from pydantic import BaseModel, Field

from app.core.config import get_settings
from app.email.sender import EmailSender
from app.email.templates import invitation_email
from app.identity import service
from app.identity.deps import (
    CurrentUser,
    OrgContext,
    Session,
    get_path_org_context,
    require_org_permission,
    require_permission,
)
from app.identity.models import Invitation, Membership, Organization, User
from app.identity.permissions import Permission, Role
from app.identity.schemas import (
    InvitationCreate,
    InvitationOut,
    InvitationPreview,
    MemberOut,
    MemberUpdate,
    MeOut,
    MyMembership,
    OrganizationCreate,
    OrganizationOut,
    OrganizationSummary,
    OrganizationUpdate,
    Page,
    TransferOwnership,
    UserOut,
)

router = APIRouter(tags=["identity"])
log = structlog.get_logger(__name__)

Limit = Annotated[int, Query(ge=1, le=100)]
Cursor = Annotated[str | None, Query(max_length=64)]


class InvitationToken(BaseModel):
    # Tokens travel in bodies, never URLs, so logs, traces and Sentry never see them (DEC-026).
    token: str = Field(min_length=20, max_length=128)


def _member_out(membership: Membership, user: User) -> MemberOut:
    return MemberOut(
        id=membership.id,
        user=UserOut.model_validate(user),
        role=Role(membership.role),
        capabilities=membership.capabilities,
        status=membership.status,
        joined_at=membership.joined_at,
    )


async def _send_invitation(
    sender: EmailSender, invitation: Invitation, org: Organization, inviter: User, token: str
) -> None:
    accept_url = f"{get_settings().app_base_url.rstrip('/')}/invite#token={token}"
    try:
        await sender.send(
            invitation_email(
                to=invitation.email,
                organization_name=org.name,
                inviter_name=inviter.name,
                role=invitation.role,
                accept_url=accept_url,
            )
        )
    except Exception as exc:
        # TODO(M4 worker): move to a retried job and surface bounces on S-49 (WF-03).
        log.warning(
            "invitation_email_failed", invitation_id=str(invitation.id), error=type(exc).__name__
        )


# ---- me -----------------------------------------------------------------------------------


@router.get("/me")
async def get_me(session: Session, user: CurrentUser) -> MeOut:
    memberships = await service.my_memberships(session, user)
    return MeOut(
        user=UserOut.model_validate(user),
        is_platform_admin=user.is_platform_admin,
        memberships=[
            MyMembership(
                organization=OrganizationSummary.model_validate(org),
                role=Role(m.role),
                capabilities=m.capabilities,
            )
            for m, org in memberships
        ],
    )


# ---- organizations ------------------------------------------------------------------------


@router.post("/orgs", status_code=status.HTTP_201_CREATED)
async def create_org(
    session: Session, user: CurrentUser, body: OrganizationCreate
) -> OrganizationOut:
    org = await service.create_organization(session, user, body)
    await session.commit()
    return OrganizationOut.model_validate(org)


@router.get("/orgs/{org_id}")
async def get_org(context: Annotated[OrgContext, Depends(get_path_org_context)]) -> OrganizationOut:
    return OrganizationOut.model_validate(context.organization)


@router.patch("/orgs/{org_id}")
async def update_org(
    session: Session,
    body: OrganizationUpdate,
    context: Annotated[OrgContext, Depends(require_org_permission(Permission.ORG_UPDATE))],
) -> OrganizationOut:
    org = await service.update_organization(session, context.user, context.organization, body)
    await session.commit()
    return OrganizationOut.model_validate(org)


@router.delete("/orgs/{org_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_org(
    session: Session,
    context: Annotated[OrgContext, Depends(require_org_permission(Permission.ORG_DELETE))],
) -> Response:
    await service.delete_organization(session, context.user, context.organization)
    await session.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.post("/orgs/{org_id}/transfer-ownership", status_code=status.HTTP_204_NO_CONTENT)
async def transfer_ownership(
    session: Session,
    body: TransferOwnership,
    context: Annotated[
        OrgContext, Depends(require_org_permission(Permission.ORG_TRANSFER_OWNERSHIP))
    ],
) -> Response:
    await service.transfer_ownership(
        session, context.user, context.organization, body.new_owner_user_id
    )
    await session.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)


# ---- members (X-Org-Id) -------------------------------------------------------------------


@router.get("/members")
async def list_members(
    session: Session,
    context: Annotated[OrgContext, Depends(require_permission(Permission.MEMBERS_READ))],
    limit: Limit = 50,
    cursor: Cursor = None,
) -> Page[MemberOut]:
    rows, next_cursor = await service.list_members(
        session, context.organization, limit=limit, cursor=cursor
    )
    return Page(items=[_member_out(m, u) for m, u in rows], next_cursor=next_cursor)


@router.patch("/members/{membership_id}")
async def update_member(
    session: Session,
    membership_id: uuid.UUID,
    body: MemberUpdate,
    context: Annotated[OrgContext, Depends(require_permission(Permission.MEMBERS_UPDATE))],
) -> MemberOut:
    membership, user = await service.update_member(
        session, context.user, context.organization, membership_id, body
    )
    await session.commit()
    return _member_out(membership, user)


@router.delete("/members/{membership_id}", status_code=status.HTTP_204_NO_CONTENT)
async def remove_member(
    session: Session,
    membership_id: uuid.UUID,
    context: Annotated[OrgContext, Depends(require_permission(Permission.MEMBERS_REMOVE))],
) -> Response:
    await service.remove_member(session, context.user, context.organization, membership_id)
    await session.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)


# ---- invitations --------------------------------------------------------------------------


@router.post("/invitations", status_code=status.HTTP_201_CREATED)
async def create_invitation(
    request: Request,
    session: Session,
    background: BackgroundTasks,
    body: InvitationCreate,
    context: Annotated[OrgContext, Depends(require_permission(Permission.MEMBERS_INVITE))],
) -> InvitationOut:
    invitation, token = await service.create_invitation(
        session, context.user, context.organization, body
    )
    await session.commit()
    background.add_task(
        _send_invitation,
        request.app.state.email_sender,
        invitation,
        context.organization,
        context.user,
        token,
    )
    return InvitationOut.model_validate(invitation)


@router.get("/invitations")
async def list_invitations(
    session: Session,
    context: Annotated[OrgContext, Depends(require_permission(Permission.MEMBERS_INVITE))],
    limit: Limit = 50,
    cursor: Cursor = None,
) -> Page[InvitationOut]:
    rows, next_cursor = await service.list_invitations(
        session, context.organization, limit=limit, cursor=cursor
    )
    return Page(items=[InvitationOut.model_validate(i) for i in rows], next_cursor=next_cursor)


@router.delete("/invitations/{invitation_id}", status_code=status.HTTP_204_NO_CONTENT)
async def revoke_invitation(
    session: Session,
    invitation_id: uuid.UUID,
    context: Annotated[OrgContext, Depends(require_permission(Permission.MEMBERS_INVITE))],
) -> Response:
    await service.revoke_invitation(session, context.user, context.organization, invitation_id)
    await session.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.post("/invitations/{invitation_id}/resend")
async def resend_invitation(
    request: Request,
    session: Session,
    background: BackgroundTasks,
    invitation_id: uuid.UUID,
    context: Annotated[OrgContext, Depends(require_permission(Permission.MEMBERS_INVITE))],
) -> InvitationOut:
    invitation, token = await service.resend_invitation(
        session, context.user, context.organization, invitation_id
    )
    await session.commit()
    background.add_task(
        _send_invitation,
        request.app.state.email_sender,
        invitation,
        context.organization,
        context.user,
        token,
    )
    return InvitationOut.model_validate(invitation)


@router.post("/invitations/preview")
async def preview_invitation(session: Session, body: InvitationToken) -> InvitationPreview:
    """Public (S-05 before sign-in). TODO(M2): rate limit per IP."""
    invitation, org, inviter = await service.preview_invitation(session, body.token)
    return InvitationPreview(
        organization_name=org.name,
        inviter_name=inviter.name if inviter else None,
        role=invitation.role,
        email_hint=service.mask_email(invitation.email),
        expires_at=invitation.expires_at,
    )


@router.post("/invitations/accept")
async def accept_invitation(
    session: Session, user: CurrentUser, body: InvitationToken
) -> MyMembership:
    membership = await service.accept_invitation(session, user, body.token)
    await session.commit()
    org = await session.get_one(Organization, membership.organization_id)
    return MyMembership(
        organization=OrganizationSummary.model_validate(org),
        role=Role(membership.role),
        capabilities=membership.capabilities,
    )
