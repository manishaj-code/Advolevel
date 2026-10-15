"""MON-01: trigger a test exception to prove Sentry wiring (spec 13 §12).

Mounted only when DEBUG_ENDPOINTS_ENABLED is true (settings forbid it in production), and only
platform admins can call it (KI-007).
"""

from fastapi import APIRouter, Depends

from app.identity.deps import require_platform_admin

router = APIRouter(
    prefix="/admin/debug", tags=["admin"], dependencies=[Depends(require_platform_admin)]
)


class DebugTestError(RuntimeError):
    pass


@router.post("/raise")
async def raise_test_error() -> None:
    raise DebugTestError("MON-01 test exception")
