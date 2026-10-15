"""Local stand-ins for Clerk: RS256 key + JWKS, token minting, fake Backend API, Svix signing."""

import base64
import hashlib
import hmac
import json
import time
from dataclasses import dataclass, field
from typing import Any

import jwt
from cryptography.hazmat.primitives.asymmetric import rsa
from jwt.algorithms import RSAAlgorithm

from app.core.security import TokenVerifier
from app.email.sender import Email
from app.identity.provider import ProviderUser

ISSUER = "https://clerk.test.advolevel.local"
KID = "test-key-1"
WEBHOOK_SECRET = "whsec_" + base64.b64encode(b"advolevel-test-webhook-secret-32b").decode()


@dataclass
class SigningKey:
    private: rsa.RSAPrivateKey
    kid: str = KID

    @classmethod
    def generate(cls, kid: str = KID) -> "SigningKey":
        return cls(rsa.generate_private_key(public_exponent=65537, key_size=2048), kid)

    def jwk(self) -> dict[str, Any]:
        data: dict[str, Any] = json.loads(RSAAlgorithm.to_jwk(self.private.public_key()))
        return {**data, "kid": self.kid, "alg": "RS256", "use": "sig"}

    def token(self, subject: str, **overrides: Any) -> str:
        now = int(time.time())
        claims: dict[str, Any] = {
            "iss": ISSUER,
            "sub": subject,
            "sid": f"sess_{subject}",
            "iat": now,
            "nbf": now,
            "exp": now + 60,
            "azp": "http://localhost:3000",
        }
        claims.update(overrides)
        claims = {k: v for k, v in claims.items() if v is not None}
        return jwt.encode(claims, self.private, algorithm="RS256", headers={"kid": self.kid})


def make_verifier(*keys: SigningKey, **kwargs: Any) -> TokenVerifier:
    async def fetch() -> dict[str, Any]:
        return {"keys": [k.jwk() for k in keys]}

    return TokenVerifier(issuer=ISSUER, fetch_jwks=fetch, **kwargs)


@dataclass
class FakeIdentityProvider:
    users: dict[str, ProviderUser] = field(default_factory=dict)

    def add(
        self, subject: str, email: str, *, verified: bool = True, name: str | None = None
    ) -> None:
        self.users[subject] = ProviderUser(
            provider_user_id=subject,
            email=email.lower(),
            email_verified=verified,
            name=name,
            avatar_url=None,
        )

    async def get_user(self, provider_user_id: str) -> ProviderUser | None:
        return self.users.get(provider_user_id)


@dataclass
class RecordingEmailSender:
    sent: list[Email] = field(default_factory=list)

    async def send(self, email: Email) -> None:
        self.sent.append(email)


def svix_headers(
    body: bytes, *, secret: str = WEBHOOK_SECRET, msg_id: str = "msg_1"
) -> dict[str, str]:
    timestamp = str(int(time.time()))
    key = base64.b64decode(secret.removeprefix("whsec_"))
    digest = hmac.new(key, f"{msg_id}.{timestamp}.".encode() + body, hashlib.sha256).digest()
    return {
        "svix-id": msg_id,
        "svix-timestamp": timestamp,
        "svix-signature": "v1," + base64.b64encode(digest).decode(),
        "content-type": "application/json",
    }


def clerk_user_payload(subject: str, email: str, *, verified: bool = True) -> dict[str, Any]:
    return {
        "id": subject,
        "first_name": "Test",
        "last_name": subject,
        "image_url": None,
        "primary_email_address_id": "idn_1",
        "email_addresses": [
            {
                "id": "idn_1",
                "email_address": email,
                "verification": {"status": "verified" if verified else "unverified"},
            }
        ],
    }
