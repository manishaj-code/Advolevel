"""Request ID propagation (spec 13 §4).

The ID is accepted from the client when well-formed, otherwise generated, then stored in a
contextvar so logs, Sentry and spans can pick it up, and echoed back in ``X-Request-Id``.
"""

import re
import uuid
from contextvars import ContextVar

from starlette.types import ASGIApp, Message, Receive, Scope, Send

REQUEST_ID_HEADER = "X-Request-Id"
_VALID_REQUEST_ID = re.compile(r"^[A-Za-z0-9._-]{8,128}$")

request_id_var: ContextVar[str | None] = ContextVar("request_id", default=None)


def get_request_id() -> str | None:
    return request_id_var.get()


def _resolve_request_id(scope: Scope) -> str:
    for name, value in scope.get("headers", []):
        if name.decode("latin-1").lower() == REQUEST_ID_HEADER.lower():
            candidate: str = value.decode("latin-1")
            if _VALID_REQUEST_ID.match(candidate):
                return candidate
            break
    return uuid.uuid4().hex


class RequestIdMiddleware:
    """Pure ASGI middleware so the contextvar is set for the whole request, including streams."""

    def __init__(self, app: ASGIApp) -> None:
        self.app = app

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        request_id = _resolve_request_id(scope)
        token = request_id_var.set(request_id)

        async def send_with_header(message: Message) -> None:
            if message["type"] == "http.response.start":
                headers = list(message.get("headers", []))
                headers.append((REQUEST_ID_HEADER.lower().encode(), request_id.encode()))
                message["headers"] = headers
            await send(message)

        try:
            await self.app(scope, receive, send_with_header)
        finally:
            request_id_var.reset(token)
