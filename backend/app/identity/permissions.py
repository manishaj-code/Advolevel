"""Roles, capabilities and permissions (spec 02 §1-2).

Only the identity/org rows of the matrix exist so far; each milestone adds its own permissions
here, and the table-driven AZ-01 test (tests/test_permissions.py) pins the whole mapping.
"""

from enum import StrEnum


class Role(StrEnum):
    OWNER = "owner"
    ADMIN = "admin"
    MEMBER = "member"
    VIEWER = "viewer"


class Capability(StrEnum):
    APPROVER = "approver"
    EXECUTIVE_CONFIGURATOR = "executive_configurator"
    KNOWLEDGE_MANAGER = "knowledge_manager"
    CONTENT_PUBLISHER = "content_publisher"


class Permission(StrEnum):
    ORG_READ = "org:read"
    ORG_UPDATE = "org:update"
    ORG_DELETE = "org:delete"
    ORG_TRANSFER_OWNERSHIP = "org:transfer_ownership"
    MEMBERS_READ = "members:read"
    MEMBERS_INVITE = "members:invite"
    MEMBERS_UPDATE = "members:update"
    MEMBERS_REMOVE = "members:remove"


_ADMIN = {
    Permission.ORG_READ,
    Permission.ORG_UPDATE,
    Permission.MEMBERS_READ,
    Permission.MEMBERS_INVITE,
    Permission.MEMBERS_UPDATE,
    Permission.MEMBERS_REMOVE,
}

ROLE_PERMISSIONS: dict[Role, frozenset[Permission]] = {
    Role.OWNER: frozenset(_ADMIN | {Permission.ORG_DELETE, Permission.ORG_TRANSFER_OWNERSHIP}),
    Role.ADMIN: frozenset(_ADMIN),
    Role.MEMBER: frozenset({Permission.ORG_READ, Permission.MEMBERS_READ}),
    Role.VIEWER: frozenset({Permission.ORG_READ, Permission.MEMBERS_READ}),
}

# Capabilities grant extra permissions to members (spec 02 ⚙️ cells). None apply to identity yet.
CAPABILITY_PERMISSIONS: dict[Capability, frozenset[Permission]] = {
    c: frozenset() for c in Capability
}

# Roles that may be granted through an invitation or a role change; ownership only moves by
# transfer (BR: exactly one owner per org).
ASSIGNABLE_ROLES = (Role.ADMIN, Role.MEMBER, Role.VIEWER)


def has_permission(role: str, capabilities: list[str], permission: Permission) -> bool:
    if permission in ROLE_PERMISSIONS[Role(role)]:
        return True
    return any(
        permission in CAPABILITY_PERMISSIONS.get(Capability(c), frozenset())
        for c in capabilities
        if c in Capability._value2member_map_
    )
