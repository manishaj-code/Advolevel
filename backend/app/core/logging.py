"""Structured JSON logging with structlog (spec 13 §2)."""

import logging
import sys
import time
from collections.abc import MutableMapping
from typing import Any

import structlog
from opentelemetry import trace
from starlette.types import ASGIApp, Message, Receive, Scope, Send

from app.core.config import Settings
from app.core.redaction import scrub
from app.core.request_context import get_request_id


def _add_context(_: Any, __: str, event_dict: MutableMapping[str, Any]) -> MutableMapping[str, Any]:
    request_id = get_request_id()
    if request_id:
        event_dict.setdefault("request_id", request_id)
    span_ctx = trace.get_current_span().get_span_context()
    if span_ctx.is_valid:
        event_dict.setdefault("trace_id", format(span_ctx.trace_id, "032x"))
        event_dict.setdefault("span_id", format(span_ctx.span_id, "016x"))
    return event_dict


# Fields we set ourselves. Their values (timestamps, hex IDs) can look like phone or card numbers.
_TRUSTED_FIELDS = frozenset(
    {"timestamp", "level", "service", "env", "release", "request_id", "trace_id", "span_id"}
)


def _redact(_: Any, __: str, event_dict: MutableMapping[str, Any]) -> MutableMapping[str, Any]:
    return {k: v if k in _TRUSTED_FIELDS else scrub({k: v})[k] for k, v in event_dict.items()}


def configure_logging(settings: Settings) -> None:
    level = logging.getLevelName(settings.log_level.upper())
    shared: list[structlog.types.Processor] = [
        structlog.contextvars.merge_contextvars,
        structlog.stdlib.add_log_level,
        structlog.processors.TimeStamper(fmt="iso", utc=True, key="timestamp"),
        _add_context,
    ]
    structlog.configure(
        processors=[
            *shared,
            structlog.processors.format_exc_info,
            _redact,
            structlog.processors.JSONRenderer(),
        ],
        wrapper_class=structlog.make_filtering_bound_logger(level),
        logger_factory=structlog.PrintLoggerFactory(sys.stdout),
        cache_logger_on_first_use=True,
    )
    structlog.contextvars.bind_contextvars(
        service=settings.service_name, env=settings.app_env, release=settings.release
    )
    # Uvicorn's own access log duplicates ours without request IDs.
    logging.getLogger("uvicorn.access").disabled = True


def _route_template(scope: Scope) -> str:
    """Full path template (e.g. /api/v1/x/{id}) so logs never carry raw IDs.

    FastAPI >= 0.140 stores routes of included routers relative to their prefix; the full
    template only lives in its (internal) effective route context. Fall back defensively.
    """
    effective = (scope.get("fastapi") or {}).get("effective_route_context")
    path = getattr(effective, "path", None) or getattr(scope.get("route"), "path", None)
    return str(path) if path else "<unmatched>"


class AccessLogMiddleware:
    """One structured line per request: route, method, status, duration_ms."""

    def __init__(self, app: ASGIApp) -> None:
        self.app = app
        self.log = structlog.get_logger("access")

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        start = time.perf_counter()
        status = 500

        async def capture_status(message: Message) -> None:
            nonlocal status
            if message["type"] == "http.response.start":
                status = message["status"]
            await send(message)

        try:
            await self.app(scope, receive, capture_status)
        finally:
            self.log.info(
                "request",
                method=scope["method"],
                route=_route_template(scope),
                status=status,
                duration_ms=round((time.perf_counter() - start) * 1000, 1),
            )
