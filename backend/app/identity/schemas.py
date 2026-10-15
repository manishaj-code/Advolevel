"""Request and response models for identity endpoints (spec 08 §2)."""

import uuid
import zoneinfo
from datetime import datetime
from functools import cache
from typing import Annotated, Literal

from pydantic import (
    AfterValidator,
    BaseModel,
    ConfigDict,
    EmailStr,
    Field,
    HttpUrl,
    StringConstraints,
    field_validator,
)

from app.identity.permissions import Capability, Role

SizeBand = Literal["1-10", "11-50", "51-200", "201-1000", "1000+"]
AssignableRole = Literal["admin", "member", "viewer"]
Name = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=120)]
ShortText = Annotated[str, StringConstraints(strip_whitespace=True, max_length=120)]


@cache
def _timezones() -> frozenset[str]:
    return frozenset(zoneinfo.available_timezones())


def _valid_timezone(value: str) -> str:
    if value not in _timezones():
        raise ValueError("unknown IANA time zone")
    return value


Timezone = Annotated[str, StringConstraints(max_length=64), AfterValidator(_valid_timezone)]
Capabilities = Annotated[list[Capability], Field(max_length=len(Capability))]


class StrictModel(BaseModel):
    model_config = ConfigDict(extra="forbid")


# ---- organizations ------------------------------------------------------------------------


class OrganizationCreate(StrictModel):
    name: Name
    industry: ShortText | None = None
    size_band: SizeBand | None = None
    website: HttpUrl | None = None
    timezone: Timezone = "UTC"


class OrganizationUpdate(StrictModel):
    name: Name | None = None
    industry: ShortText | None = None
    size_band: SizeBand | None = None
    website: HttpUrl | None = None
    timezone: Timezone | None = None


class OrganizationOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    name: str
    slug: str
    industry: str | None
    size_band: str | None
    website: str | None
    timezone: str
    status: str
    owner_user_id: uuid.UUID
    created_at: datetime


class OrganizationSummary(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    name: str
    slug: str
    status: str


class TransferOwnership(StrictModel):
    new_owner_user_id: uuid.UUID


# ---- users and memberships ----------------------------------------------------------------


class UserOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    email: str
    name: str | None
    avatar_url: str | None


class MyMembership(BaseModel):
    organization: OrganizationSummary
    role: Role
    capabilities: list[str]


class MeOut(BaseModel):
    user: UserOut
    is_platform_admin: bool
    memberships: list[MyMembership]


class MemberOut(BaseModel):
    id: uuid.UUID  # membership ID
    user: UserOut
    role: Role
    capabilities: list[str]
    status: str
    joined_at: datetime


class MemberUpdate(StrictModel):
    role: AssignableRole | None = None
    capabilities: Capabilities | None = None


class Page[T](BaseModel):
    items: list[T]
    next_cursor: str | None


# ---- invitations --------------------------------------------------------------------------


class InvitationCreate(StrictModel):
    email: EmailStr
    role: AssignableRole = "member"
    capabilities: Capabilities = Field(default_factory=list)

    @field_validator("email")
    @classmethod
    def _lower(cls, value: str) -> str:
        return value.strip().lower()


class InvitationOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    email: str
    role: str
    capabilities: list[str]
    invited_by: uuid.UUID
    expires_at: datetime
    created_at: datetime


class InvitationPreview(BaseModel):
    organization_name: str
    inviter_name: str | None
    role: str
    email_hint: str  # masked; lets the invitee spot a wrong-account sign-in
    expires_at: datetime
