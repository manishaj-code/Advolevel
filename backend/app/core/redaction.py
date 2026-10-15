"""Shared scrubber for logs, Sentry events and span attributes (spec 13 §10, test SD-01)."""

import re
from collections.abc import Mapping
from typing import Any

REDACTED = "[REDACTED]"

_SENSITIVE_KEY = re.compile(r"token|secret|password|api[_-]?key|authorization|cookie", re.I)
_DENY_LIST_KEYS = frozenset({"content", "prompt", "completion", "text"})

_EMAIL = re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}")
_CARD = re.compile(r"\b(?:\d[ -]?){13,19}\b")
_PHONE = re.compile(r"(?<![\w-])\+?\d{1,3}[ .-]?\(?\d{2,4}\)?[ .-]?\d{3,4}[ .-]?\d{3,4}(?![\w-])")
_BEARER = re.compile(r"\bBearer\s+[A-Za-z0-9._~+/-]+=*", re.I)


def is_sensitive_key(key: str) -> bool:
    return bool(_SENSITIVE_KEY.search(key)) or key.lower() in _DENY_LIST_KEYS


def scrub_string(value: str) -> str:
    value = _BEARER.sub("Bearer " + REDACTED, value)
    value = _EMAIL.sub(REDACTED, value)
    value = _CARD.sub(REDACTED, value)
    return _PHONE.sub(REDACTED, value)


def scrub(value: Any, _depth: int = 0) -> Any:
    """Return a redacted copy of ``value``. Containers are walked; other types pass through."""
    if _depth > 20:
        return REDACTED
    if isinstance(value, str):
        return scrub_string(value)
    if isinstance(value, Mapping):
        return {
            k: REDACTED if isinstance(k, str) and is_sensitive_key(k) else scrub(v, _depth + 1)
            for k, v in value.items()
        }
    if isinstance(value, list | tuple | set):
        return type(value)(scrub(v, _depth + 1) for v in value)
    return value
