"""Entitlement lookups (spec 02 subscription entitlements).

Stub until plans and subscriptions exist (M11, OQ-011): limits come from settings. Callers already
go through this module so M11 only swaps the implementation. ``-1`` means unlimited.
"""

import uuid
from enum import StrEnum

from app.core.config import get_settings
from app.core.errors import AppError


class Limit(StrEnum):
    SEATS_MAX = "seats.max"


async def get_limit(organization_id: uuid.UUID, limit: Limit) -> int:
    del organization_id  # per-org plans and overrides arrive in M11
    if limit is Limit.SEATS_MAX:
        return get_settings().default_seats_max
    raise ValueError(limit)


def ensure_within(limit: Limit, used: int, maximum: int) -> None:
    if 0 <= maximum <= used:
        raise AppError(
            402,
            "entitlement_exceeded",
            f"Your plan allows {maximum} for {limit.value}.",
            title="Plan limit reached",
        )
