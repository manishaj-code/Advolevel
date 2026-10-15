"""MON-01: trigger a test exception to prove Sentry wiring (spec 13 §12).

Mounted only when DEBUG_ENDPOINTS_ENABLED is true, which settings forbid in production.
TODO(M1): require the platform-admin capability once authentication exists (KI-007).
"""

from fastapi import APIRouter

router = APIRouter(prefix="/admin/debug", tags=["admin"])


class DebugTestError(RuntimeError):
    pass


@router.post("/raise")
async def raise_test_error() -> None:
    raise DebugTestError("MON-01 test exception")
