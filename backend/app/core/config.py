"""Application settings, validated at startup (spec 12 §2). The app fails fast on bad config."""

from functools import lru_cache
from typing import Annotated, Literal, Self

from pydantic import Field, PostgresDsn, RedisDsn, field_validator, model_validator
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

    sentry_dsn: str | None = None
    sentry_environment: str | None = None

    otel_exporter_otlp_endpoint: str | None = None
    otel_trace_sample_rate: float = Field(default=0.1, ge=0.0, le=1.0)

    # MON-01: lets staging trigger a test exception. Never enabled in production.
    debug_endpoints_enabled: bool = False

    @field_validator("cors_origins", mode="before")
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
        return self

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
