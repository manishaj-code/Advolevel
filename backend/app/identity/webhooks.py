"""Clerk webhooks (WF-01). Public, Svix-signature verified, idempotent (spec 10 §9)."""

import json
from typing import Any

import structlog
from fastapi import APIRouter, Request, Response, status

from app.core.config import get_settings
from app.core.errors import AppError
from app.identity import service
from app.identity.deps import Session
from app.identity.provider import InvalidWebhookError, parse_clerk_user, verify_svix_signature

router = APIRouter(prefix="/webhooks", tags=["webhooks"])
log = structlog.get_logger(__name__)

MAX_BODY_BYTES = 256 * 1024


@router.post("/clerk", status_code=status.HTTP_204_NO_CONTENT)
async def clerk_webhook(request: Request, session: Session) -> Response:
    secret = get_settings().auth_webhook_secret
    if secret is None:
        raise AppError(503, "auth_not_configured", "Webhooks are not configured.")
    body = await request.body()
    if len(body) > MAX_BODY_BYTES:
        raise AppError(413, "payload_too_large")
    try:
        verify_svix_signature(secret.get_secret_value(), dict(request.headers), body)
    except InvalidWebhookError as exc:
        log.warning("webhook_rejected", provider="clerk", reason=str(exc))
        raise AppError(401, "invalid_signature", "Webhook signature is invalid.") from exc

    event: dict[str, Any] = json.loads(body)
    event_type = event.get("type")
    data: dict[str, Any] = event.get("data") or {}
    if event_type in ("user.created", "user.updated"):
        provider_user = parse_clerk_user(data)
        if provider_user is None:
            log.warning("webhook_user_without_email", provider="clerk", event_type=event_type)
        else:
            await service.upsert_user(session, provider_user)
    elif event_type == "user.deleted" and data.get("id"):
        await service.delete_user(session, str(data["id"]))
    else:
        log.info("webhook_ignored", provider="clerk", event_type=event_type)
    await session.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)
