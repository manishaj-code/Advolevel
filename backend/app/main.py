"""FastAPI application factory."""

from fastapi import APIRouter, FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.admin import debug
from app.core import health
from app.core.config import Settings, get_settings
from app.core.errors import UnhandledErrorMiddleware, register_error_handlers
from app.core.logging import AccessLogMiddleware, configure_logging
from app.core.request_context import REQUEST_ID_HEADER, RequestIdMiddleware
from app.core.security import build_token_verifier
from app.core.telemetry import init_sentry, init_tracing
from app.email.sender import build_email_sender
from app.identity import router as identity_router
from app.identity import webhooks as identity_webhooks
from app.identity.provider import ClerkIdentityProvider

API_PREFIX = "/api/v1"


def create_app(settings: Settings | None = None) -> FastAPI:
    settings = settings or get_settings()
    configure_logging(settings)
    init_sentry(settings)

    app = FastAPI(
        title="AdvoLevel API",
        version=settings.release,
        openapi_url=f"{API_PREFIX}/openapi.json",
        docs_url=None if settings.app_env == "production" else f"{API_PREFIX}/docs",
        redoc_url=None,
    )
    register_error_handlers(app)

    # Swappable collaborators; tests replace them on app.state.
    app.state.token_verifier = build_token_verifier(settings)
    secret = settings.auth_secret_key
    app.state.identity_provider = (
        ClerkIdentityProvider(api_url=settings.auth_api_url, secret_key=secret.get_secret_value())
        if secret
        else None
    )
    app.state.email_sender = build_email_sender(settings)

    app.include_router(health.router)
    api = APIRouter(prefix=API_PREFIX)
    api.include_router(identity_router.router)
    api.include_router(identity_webhooks.router)
    if settings.debug_endpoints_enabled:
        api.include_router(debug.router)
    app.include_router(api)

    # Added last = outermost. Order on the way in: RequestId -> AccessLog -> CORS -> errors -> app.
    app.add_middleware(UnhandledErrorMiddleware)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
        expose_headers=[REQUEST_ID_HEADER],
    )
    app.add_middleware(AccessLogMiddleware)
    app.add_middleware(RequestIdMiddleware)

    init_tracing(app, settings)
    return app


def app_factory() -> FastAPI:
    """Entry point for ``uvicorn --factory app.main:app_factory``."""
    return create_app()
