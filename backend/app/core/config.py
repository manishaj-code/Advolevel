"""Application settings, validated at startup (spec 12 §2). The app fails fast on bad config."""

from functools import lru_cache
from typing import Annotated, Literal, Self

from pydantic import Field, PostgresDsn, RedisDsn, SecretStr, field_validator, model_validator
from pydantic_settings import BaseSettings, NoDecode, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", env_ignore_empty=True, extra="ignore"
    )

    app_env: Literal["local", "test", "staging", "production"] = "local"
    service_name: str = Field(default="advolevel-api", alias="OTEL_SERVICE_NAME")
    release: str = Field(default="dev", alias="SENTRY_RELEASE")
    log_level: str = "INFO"

    database_url: PostgresDsn
    # Owner role; only the migration job sets it (spec 12 §5).
    database_migration_url: PostgresDsn | None = None
    redis_url: RedisDsn

    cors_origins: Annotated[list[str], NoDecode] = Field(default_factory=list)
    app_base_url: str = "http://localhost:3000"

    # Managed auth provider: Clerk (DEC-006, OQ-019). Issuer = the Clerk Frontend API URL.
    auth_issuer: str | None = None
    auth_jwks_url: str | None = None  # defaults to {issuer}/.well-known/jwks.json
    auth_audience: str | None = None  # Clerk session tokens carry no aud unless customised
    auth_authorized_parties: Annotated[list[str], NoDecode] = Field(default_factory=list)
    auth_secret_key: SecretStr | None = None  # Clerk Backend API (just-in-time user sync)
    auth_webhook_secret: SecretStr | None = None  # Svix signing secret, whsec_...
    auth_api_url: str = "https://api.clerk.com/v1"

    # Transactional email (OQ-029 pending): "smtp" (Mailpit locally) or "console" (log only).
    email_provider: Literal["smtp", "console"] = "console"
    email_from: str = "AdvoLevel <no-reply@advolevel.local>"
    smtp_host: str = "127.0.0.1"
    smtp_port: int = 1025

    # Stub limits until plans and entitlements land (M11, OQ-011; orgs per user OQ-006). -1 = none.
    max_orgs_per_user: int = -1
    default_seats_max: int = -1

    sentry_dsn: str | None = None
    sentry_environment: str | None = None

    otel_exporter_otlp_endpoint: str | None = None
    otel_trace_sample_rate: float = Field(default=0.1, ge=0.0, le=1.0)

    # MON-01: lets staging trigger a test exception. Never enabled in production.
    debug_endpoints_enabled: bool = False

    @field_validator("cors_origins", "auth_authorized_parties", mode="before")
    @classmethod
    def _split_cors(cls, value: object) -> object:
        if isinstance(value, str):
            return [o.strip() for o in value.split(",") if o.strip()]
        return value

    @model_validator(mode="after")
    def _production_guards(self) -> Self:
        if self.app_env == "production":
            if self.debug_endpoints_enabled:
                raise ValueError("DEBUG_ENDPOINTS_ENABLED must be false in production")
            if not self.sentry_dsn:
                raise ValueError("SENTRY_DSN is required in production")
        if self.app_env in ("staging", "production"):
            missing = [
                name
                for name, value in (
                    ("AUTH_ISSUER", self.auth_issuer),
                    ("AUTH_SECRET_KEY", self.auth_secret_key),
                    ("AUTH_WEBHOOK_SECRET", self.auth_webhook_secret),
                )
                if not value
            ]
            if missing:
                raise ValueError(f"Required in {self.app_env}: {', '.join(missing)}")
            if self.email_provider == "console":
                raise ValueError(f"EMAIL_PROVIDER=console is not allowed in {self.app_env}")
        return self

    @property
    def jwks_url(self) -> str | None:
        if self.auth_jwks_url:
            return self.auth_jwks_url
        if self.auth_issuer:
            return self.auth_issuer.rstrip("/") + "/.well-known/jwks.json"
        return None

    @property
    def sqlalchemy_url(self) -> str:
        return psycopg_url(str(self.database_url))


def psycopg_url(url: str) -> str:
    """Database URL with the psycopg 3 driver, whatever scheme the env var used."""
    for prefix in ("postgresql+psycopg://", "postgresql://", "postgres://"):
        if url.startswith(prefix):
            return "postgresql+psycopg://" + url[len(prefix) :]
    return url


@lru_cache
def get_settings() -> Settings:
    return Settings()
