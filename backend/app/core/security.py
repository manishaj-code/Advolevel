"""Access-token verification for the managed auth provider (spec 10 §1).

Checks the signature against the provider's JWKS (cached, refreshed on an unknown ``kid``), then
``iss``, ``exp``, ``nbf``, ``aud`` (when configured) and ``azp`` (when authorized parties are
configured), with 60 s leeway. Nothing from an unverified token is ever trusted.
"""

import asyncio
import time
from collections.abc import Awaitable, Callable
from dataclasses import dataclass
from typing import Any

import httpx
import jwt
import structlog
from jwt import PyJWK

from app.core.config import Settings

log = structlog.get_logger(__name__)

LEEWAY_SECONDS = 60
JWKS_MIN_REFRESH_SECONDS = 60
ALGORITHMS = ["RS256"]

JwksFetcher = Callable[[], Awaitable[dict[str, Any]]]


class InvalidTokenError(Exception):
    """The token is missing, malformed, expired or not issued for us."""


class AuthNotConfiguredError(Exception):
    """AUTH_ISSUER is not set (allowed only in local/test)."""


@dataclass(frozen=True)
class Principal:
    subject: str  # provider user ID (Clerk: user_...)
    session_id: str | None
    claims: dict[str, Any]


def http_jwks_fetcher(url: str) -> JwksFetcher:
    async def fetch() -> dict[str, Any]:
        async with httpx.AsyncClient(timeout=5.0) as client:
            response = await client.get(url)
            response.raise_for_status()
            data: dict[str, Any] = response.json()
            return data

    return fetch


class TokenVerifier:
    def __init__(
        self,
        *,
        issuer: str,
        fetch_jwks: JwksFetcher,
        audience: str | None = None,
        authorized_parties: list[str] | None = None,
    ) -> None:
        self.issuer = issuer
        self.audience = audience
        self.authorized_parties = set(authorized_parties or [])
        self._fetch_jwks = fetch_jwks
        self._keys: dict[str, PyJWK] = {}
        self._fetched_at = 0.0
        self._lock = asyncio.Lock()

    async def verify(self, token: str) -> Principal:
        try:
            header = jwt.get_unverified_header(token)
        except jwt.PyJWTError as exc:
            raise InvalidTokenError("malformed token") from exc
        kid = header.get("kid")
        if not isinstance(kid, str) or header.get("alg") not in ALGORITHMS:
            raise InvalidTokenError("unsupported token header")

        key = await self._key(kid)
        try:
            claims: dict[str, Any] = jwt.decode(
                token,
                key=key,
                algorithms=ALGORITHMS,
                issuer=self.issuer,
                audience=self.audience,
                leeway=LEEWAY_SECONDS,
                options={
                    "require": ["exp", "iat", "iss", "sub"],
                    "verify_aud": self.audience is not None,
                },
            )
        except jwt.PyJWTError as exc:
            raise InvalidTokenError(type(exc).__name__) from exc

        azp = claims.get("azp")
        if self.authorized_parties and azp is not None and azp not in self.authorized_parties:
            raise InvalidTokenError("unauthorized party")
        return Principal(subject=str(claims["sub"]), session_id=claims.get("sid"), claims=claims)

    async def _key(self, kid: str) -> PyJWK:
        if kid in self._keys:
            return self._keys[kid]
        async with self._lock:
            # Refetch on an unknown kid (key rotation), but at most once a minute, so random
            # kids in forged tokens cannot hammer the provider.
            never_fetched = self._fetched_at == 0.0
            stale = time.monotonic() - self._fetched_at >= JWKS_MIN_REFRESH_SECONDS
            if kid not in self._keys and (never_fetched or stale):
                await self._refresh()
        if kid not in self._keys:
            raise InvalidTokenError("unknown signing key")
        return self._keys[kid]

    async def _refresh(self) -> None:
        try:
            jwks = await self._fetch_jwks()
        except Exception as exc:
            log.warning("jwks_fetch_failed", error=type(exc).__name__)
            raise InvalidTokenError("signing keys unavailable") from exc
        self._fetched_at = time.monotonic()
        keys: dict[str, PyJWK] = {}
        for raw in jwks.get("keys", []):
            try:
                keys[raw["kid"]] = PyJWK.from_dict(raw)
            except (KeyError, jwt.PyJWTError):
                continue
        self._keys = keys


def build_token_verifier(settings: Settings) -> TokenVerifier | None:
    if not settings.auth_issuer or not settings.jwks_url:
        return None
    return TokenVerifier(
        issuer=settings.auth_issuer,
        fetch_jwks=http_jwks_fetcher(settings.jwks_url),
        audience=settings.auth_audience,
        authorized_parties=settings.auth_authorized_parties,
    )
