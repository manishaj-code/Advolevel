"""Clerk as the identity provider (DEC-006, OQ-019 resolved 2026-10-15).

Two inbound paths keep ``users`` in sync, both idempotent on ``auth_provider_user_id``:
- webhooks (``user.created/updated/deleted``, Svix-signed) — WF-01;
- just-in-time lookup through the Backend API when a verified token arrives for a user we
  have not seen yet (webhooks can lag, and cannot reach a developer laptop).
"""

import base64
import hashlib
import hmac
import time
from dataclasses import dataclass
from typing import Any, Protocol

import httpx

WEBHOOK_TOLERANCE_SECONDS = 5 * 60


@dataclass(frozen=True)
class ProviderUser:
    provider_user_id: str
    email: str
    email_verified: bool
    name: str | None
    avatar_url: str | None


class IdentityProvider(Protocol):
    async def get_user(self, provider_user_id: str) -> ProviderUser | None: ...


class ProviderUnavailableError(Exception):
    pass


def parse_clerk_user(data: dict[str, Any]) -> ProviderUser | None:
    """Clerk user object (Backend API and webhook payloads share the shape)."""
    primary_id = data.get("primary_email_address_id")
    primary = next(
        (e for e in data.get("email_addresses") or [] if e.get("id") == primary_id), None
    )
    if primary is None or not primary.get("email_address"):
        return None
    name = " ".join(p for p in (data.get("first_name"), data.get("last_name")) if p) or None
    return ProviderUser(
        provider_user_id=str(data["id"]),
        email=str(primary["email_address"]).strip().lower(),
        email_verified=(primary.get("verification") or {}).get("status") == "verified",
        name=name,
        avatar_url=data.get("image_url") or None,
    )


class ClerkIdentityProvider:
    def __init__(self, *, api_url: str, secret_key: str) -> None:
        self._api_url = api_url.rstrip("/")
        self._secret_key = secret_key

    async def get_user(self, provider_user_id: str) -> ProviderUser | None:
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                response = await client.get(
                    f"{self._api_url}/users/{provider_user_id}",
                    headers={"Authorization": f"Bearer {self._secret_key}"},
                )
        except httpx.HTTPError as exc:
            raise ProviderUnavailableError(type(exc).__name__) from exc
        if response.status_code == 404:
            return None
        if response.status_code >= 400:
            raise ProviderUnavailableError(f"clerk status {response.status_code}")
        return parse_clerk_user(response.json())


class InvalidWebhookError(Exception):
    pass


def verify_svix_signature(
    secret: str, headers: dict[str, str], body: bytes, *, now: float | None = None
) -> None:
    """Svix scheme used by Clerk webhooks: HMAC-SHA256 over ``{id}.{timestamp}.{body}``."""
    msg_id = headers.get("svix-id")
    timestamp = headers.get("svix-timestamp")
    signatures = headers.get("svix-signature")
    if not (msg_id and timestamp and signatures):
        raise InvalidWebhookError("missing svix headers")
    try:
        sent_at = int(timestamp)
    except ValueError as exc:
        raise InvalidWebhookError("bad timestamp") from exc
    if abs((now if now is not None else time.time()) - sent_at) > WEBHOOK_TOLERANCE_SECONDS:
        raise InvalidWebhookError("timestamp outside tolerance")

    key = base64.b64decode(secret.removeprefix("whsec_"))
    signed = f"{msg_id}.{timestamp}.".encode() + body
    expected = base64.b64encode(hmac.new(key, signed, hashlib.sha256).digest()).decode()
    for candidate in signatures.split():
        version, _, value = candidate.partition(",")
        if version == "v1" and hmac.compare_digest(value, expected):
            return
    raise InvalidWebhookError("no matching signature")
