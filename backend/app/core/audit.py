"""Audit events (spec 10 §7).

M1 writes them to the structured log only. M2 replaces the body of ``record`` with an insert into
the append-only, hash-chained ``audit_events`` table; call sites stay the same.
"""

import uuid
from typing import Any

import structlog

log = structlog.get_logger("audit")


def record(
    action: str,
    *,
    actor_user_id: uuid.UUID | None,
    organization_id: uuid.UUID | None,
    target_type: str | None = None,
    target_id: uuid.UUID | str | None = None,
    metadata: dict[str, Any] | None = None,
) -> None:
    log.info(
        "audit",
        action=action,
        actor_user_id=str(actor_user_id) if actor_user_id else None,
        organization_id=str(organization_id) if organization_id else None,
        target_type=target_type,
        target_id=str(target_id) if target_id else None,
        metadata=metadata or {},
    )
