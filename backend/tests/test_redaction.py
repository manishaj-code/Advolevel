"""SD-01: the shared scrubber removes secrets and PII."""

import pytest

from app.core.redaction import REDACTED, scrub, scrub_string


@pytest.mark.parametrize(
    "key",
    ["Authorization", "cookie", "access_token", "client_secret", "password", "api_key", "API-KEY"],
)
def test_sensitive_keys_are_redacted(key: str) -> None:
    assert scrub({key: "value"}) == {key: REDACTED}


@pytest.mark.parametrize("key", ["content", "prompt", "completion", "text"])
def test_deny_list_keys_are_redacted(key: str) -> None:
    assert scrub({key: "the board approved the merger"}) == {key: REDACTED}


@pytest.mark.parametrize(
    ("raw", "leaked"),
    [
        ("contact jane.doe@example.com today", "jane.doe@example.com"),
        ("card 4111 1111 1111 1111 on file", "4111 1111 1111 1111"),
        ("call +1 415-555-0134 now", "415-555-0134"),
        ("header Bearer eyJhbGciOi.abc.def", "eyJhbGciOi.abc.def"),
    ],
)
def test_pii_patterns_in_strings(raw: str, leaked: str) -> None:
    result = scrub_string(raw)
    assert leaked not in result
    assert REDACTED in result


def test_nested_structures_are_walked() -> None:
    event = {"user": {"email": "a@b.co", "id": 7}, "items": [{"token": "x"}, "ok"]}
    assert scrub(event) == {
        "user": {"email": REDACTED, "id": 7},
        "items": [{"token": REDACTED}, "ok"],
    }


def test_safe_values_are_untouched() -> None:
    data = {"route": "/api/v1/orgs", "status": 200, "duration_ms": 12.5, "date": "2026-10-15"}
    assert scrub(data) == data
