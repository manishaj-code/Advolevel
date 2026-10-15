import base64
import time
from typing import Any

import jwt
import pytest
from pydantic import SecretStr, ValidationError

from app.core.config import Settings
from app.core.ids import new_id
from app.core.security import InvalidTokenError, TokenVerifier
from app.identity.permissions import ROLE_PERMISSIONS, Permission, Role, has_permission
from app.identity.provider import InvalidWebhookError, parse_clerk_user, verify_svix_signature
from app.identity.service import mask_email, slugify
from tests.auth_helpers import (
    ISSUER,
    WEBHOOK_SECRET,
    SigningKey,
    clerk_user_payload,
    make_verifier,
    svix_headers,
)
from tests.conftest import make_settings

KEY = SigningKey.generate()

# ---- token verification (spec 10 §1) ------------------------------------------------------


async def test_valid_token_yields_principal() -> None:
    principal = await make_verifier(KEY).verify(KEY.token("user_1"))
    assert (principal.subject, principal.session_id) == ("user_1", "sess_user_1")


@pytest.mark.parametrize(
    "overrides",
    [
        {"exp": int(time.time()) - 120},  # expired beyond 60 s leeway
        {"nbf": int(time.time()) + 120},  # not yet valid
        {"iss": "https://other.clerk.dev"},
        {"sub": None},
        {"azp": "https://evil.example"},
    ],
)
async def test_invalid_claims_are_rejected(overrides: dict[str, Any]) -> None:
    verifier = make_verifier(KEY, authorized_parties=["http://localhost:3000"])
    with pytest.raises(InvalidTokenError):
        await verifier.verify(KEY.token("user_1", **overrides))


async def test_expiry_within_leeway_is_accepted() -> None:
    await make_verifier(KEY).verify(KEY.token("user_1", exp=int(time.time()) - 30))


async def test_audience_checked_when_configured() -> None:
    verifier = make_verifier(KEY, audience="advolevel-api")
    with pytest.raises(InvalidTokenError):
        await verifier.verify(KEY.token("user_1"))
    await verifier.verify(KEY.token("user_1", aud="advolevel-api"))


async def test_token_signed_by_unknown_key_is_rejected() -> None:
    other = SigningKey.generate()  # same kid, different key
    with pytest.raises(InvalidTokenError):
        await make_verifier(KEY).verify(other.token("user_1"))


async def test_alg_none_and_hs256_are_rejected() -> None:
    unsigned = jwt.encode({"sub": "x", "iss": ISSUER}, None, algorithm="none")  # type: ignore[arg-type]
    hs = jwt.encode({"sub": "x", "iss": ISSUER}, "s" * 32, algorithm="HS256", headers={"kid": "k"})
    for token in (unsigned, hs):
        with pytest.raises(InvalidTokenError):
            await make_verifier(KEY).verify(token)


async def test_jwks_refetched_on_rotation_but_throttled() -> None:
    calls = 0
    rotated = SigningKey.generate(kid="rotated")
    keys = [KEY]

    async def fetch() -> dict[str, Any]:
        nonlocal calls
        calls += 1
        return {"keys": [k.jwk() for k in keys]}

    verifier = TokenVerifier(issuer=ISSUER, fetch_jwks=fetch)
    await verifier.verify(KEY.token("u"))
    keys.append(rotated)
    with pytest.raises(InvalidTokenError):  # within the refresh window: no refetch
        await verifier.verify(rotated.token("u"))
    assert calls == 1
    verifier._fetched_at -= 61
    await verifier.verify(rotated.token("u"))
    assert calls == 2


# ---- webhooks -----------------------------------------------------------------------------


def test_svix_signature_round_trip() -> None:
    body = b'{"type":"user.created"}'
    verify_svix_signature(WEBHOOK_SECRET, svix_headers(body), body)


@pytest.mark.parametrize("tamper", ["body", "secret", "old", "missing"])
def test_svix_signature_rejections(tamper: str) -> None:
    body = b'{"type":"user.created"}'
    headers = svix_headers(body)
    secret = WEBHOOK_SECRET
    now = None
    if tamper == "body":
        body = b'{"type":"user.deleted"}'
    elif tamper == "secret":
        secret = "whsec_" + base64.b64encode(b"x" * 32).decode()
    elif tamper == "old":
        now = time.time() + 600
    else:
        headers.pop("svix-signature")
    with pytest.raises(InvalidWebhookError):
        verify_svix_signature(secret, headers, body, now=now)


def test_parse_clerk_user_uses_primary_verified_email() -> None:
    user = parse_clerk_user(clerk_user_payload("user_9", " Mixed@Case.COM "))
    assert user is not None
    assert (user.email, user.email_verified, user.name) == ("mixed@case.com", True, "Test user_9")
    assert parse_clerk_user({"id": "u", "email_addresses": []}) is None
    unverified = parse_clerk_user(clerk_user_payload("u", "a@b.co", verified=False))
    assert unverified is not None and not unverified.email_verified


# ---- permissions (spec 02 §2) -------------------------------------------------------------

SPEC_02 = {
    Permission.ORG_READ: {"owner", "admin", "member", "viewer"},
    Permission.ORG_UPDATE: {"owner", "admin"},
    Permission.ORG_DELETE: {"owner"},
    Permission.ORG_TRANSFER_OWNERSHIP: {"owner"},
    Permission.MEMBERS_READ: {"owner", "admin", "member", "viewer"},
    Permission.MEMBERS_INVITE: {"owner", "admin"},
    Permission.MEMBERS_UPDATE: {"owner", "admin"},
    Permission.MEMBERS_REMOVE: {"owner", "admin"},
}


def test_role_permissions_match_spec_02() -> None:
    assert set(SPEC_02) == set(Permission)
    for permission, roles in SPEC_02.items():
        assert {r.value for r in Role if permission in ROLE_PERMISSIONS[r]} == roles, permission
        for role in Role:
            assert has_permission(role, ["approver", "bogus"], permission) == (role in roles)


# ---- helpers ------------------------------------------------------------------------------


def test_uuid7_layout_and_order() -> None:
    ids = [new_id() for _ in range(200)]
    assert all(i.version == 7 and i.variant == "specified in RFC 4122" for i in ids)
    timestamps = [i.int >> 80 for i in ids]
    assert timestamps == sorted(timestamps)
    assert abs(timestamps[-1] - int(time.time() * 1000)) < 5_000


@pytest.mark.parametrize(
    ("name", "slug"),
    [
        ("Acme Légal & Co", "acme-legal-co"),
        ("  --  ", "org"),
        ("Ünïcödé", "unicode"),
        ("a" * 99, "a" * 60),
    ],
)
def test_slugify(name: str, slug: str) -> None:
    assert slugify(name) == slug


def test_mask_email() -> None:
    assert mask_email("anna@example.com") == "a***@example.com"


# ---- settings guards ----------------------------------------------------------------------


def test_staging_requires_auth_and_real_email() -> None:
    with pytest.raises(ValidationError, match="AUTH_ISSUER"):
        Settings.model_validate(make_settings(app_env="staging").model_dump(by_alias=True))
    configured = make_settings(
        app_env="staging",
        auth_issuer=ISSUER,
        auth_secret_key=SecretStr("sk_test"),
        auth_webhook_secret=SecretStr(WEBHOOK_SECRET),
        email_provider="smtp",
    ).model_dump(by_alias=True)
    for key in ("auth_secret_key", "auth_webhook_secret"):
        configured[key] = configured[key].get_secret_value()
    assert Settings.model_validate(configured).jwks_url == f"{ISSUER}/.well-known/jwks.json"
    configured["email_provider"] = "console"
    with pytest.raises(ValidationError, match="EMAIL_PROVIDER"):
        Settings.model_validate(configured)
