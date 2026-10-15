"""RFC 9457 problem+json errors (spec 08 §1). Every error body carries the request ID."""

from http import HTTPStatus
from typing import Any

import sentry_sdk
import structlog
from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException
from starlette.types import ASGIApp, Receive, Scope, Send

from app.core.request_context import get_request_id

PROBLEM_JSON = "application/problem+json"
ERROR_TYPE_BASE = "https://docs.advolevel.app/errors/"

log = structlog.get_logger(__name__)

_DEFAULT_CODES = {
    400: "validation_error",
    401: "unauthenticated",
    403: "forbidden",
    404: "not_found",
    405: "method_not_allowed",
    409: "conflict",
    422: "unprocessable",
    429: "rate_limited",
}


class AppError(Exception):
    """Raise from services and handlers to return a typed problem response."""

    def __init__(
        self,
        status: int,
        code: str,
        detail: str | None = None,
        *,
        title: str | None = None,
        errors: list[dict[str, str]] | None = None,
    ) -> None:
        super().__init__(detail or code)
        self.status = status
        self.code = code
        self.detail = detail
        self.title = title
        self.errors = errors


def problem_response(
    status: int,
    code: str,
    detail: str | None = None,
    *,
    title: str | None = None,
    errors: list[dict[str, str]] | None = None,
) -> JSONResponse:
    body: dict[str, Any] = {
        "type": ERROR_TYPE_BASE + code,
        "title": title or HTTPStatus(status).phrase,
        "status": status,
        "code": code,
        "request_id": get_request_id(),
    }
    if detail:
        body["detail"] = detail
    if errors:
        body["errors"] = errors
    return JSONResponse(body, status_code=status, media_type=PROBLEM_JSON)


async def _app_error(_: Request, exc: Exception) -> JSONResponse:
    assert isinstance(exc, AppError)
    return problem_response(exc.status, exc.code, exc.detail, title=exc.title, errors=exc.errors)


async def _http_error(_: Request, exc: Exception) -> JSONResponse:
    assert isinstance(exc, StarletteHTTPException)
    code = _DEFAULT_CODES.get(
        exc.status_code, "internal_error" if exc.status_code >= 500 else "error"
    )
    detail = (
        exc.detail
        if isinstance(exc.detail, str) and exc.detail != HTTPStatus(exc.status_code).phrase
        else None
    )
    return problem_response(exc.status_code, code, detail)


async def _validation_error(_: Request, exc: Exception) -> JSONResponse:
    assert isinstance(exc, RequestValidationError)
    errors = [
        {
            "field": ".".join(str(p) for p in err["loc"][1:]) or str(err["loc"][0]),
            "message": err["msg"],
        }
        for err in exc.errors()
    ]
    return problem_response(400, "validation_error", "The request is invalid.", errors=errors)


def register_error_handlers(app: FastAPI) -> None:
    app.add_exception_handler(AppError, _app_error)
    app.add_exception_handler(StarletteHTTPException, _http_error)
    app.add_exception_handler(RequestValidationError, _validation_error)


class UnhandledErrorMiddleware:
    """Turns unhandled exceptions into a 500 problem response.

    It sits inside RequestIdMiddleware, so the response still carries the request ID (Starlette's
    own ServerErrorMiddleware is outermost and would lose it). Exceptions go to Sentry from here.
    """

    def __init__(self, app: ASGIApp) -> None:
        self.app = app

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        response_started = False

        async def tracking_send(message: Any) -> None:
            nonlocal response_started
            if message["type"] == "http.response.start":
                response_started = True
            await send(message)

        try:
            await self.app(scope, receive, tracking_send)
        except Exception as exc:
            sentry_sdk.capture_exception(exc)
            log.error("unhandled_exception", error=type(exc).__name__, exc_info=exc)
            if response_started:
                raise
            await problem_response(500, "internal_error")(scope, receive, send)
