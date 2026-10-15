"""WF-01…03 acceptance tests and identity rules (spec 03, spec 02, spec 08)."""

import json
from datetime import UTC, datetime, timedelta
from typing import Any

import pytest

from app.core.config import get_settings
from tests.auth_helpers import clerk_user_payload, svix_headers
from tests.integration.conftest import Harness, new_uuid

pytestmark = pytest.mark.integration

API = "/api/v1"


def _count(h: Harness, table: str) -> int:
    row = h.owner_conn.execute(f"SELECT count(*) FROM {table}").fetchone()  # noqa: S608
    assert row is not None
    return int(row[0])


# ---- authentication -----------------------------------------------------------------------


def test_requests_without_or_with_bad_tokens_are_401(harness: Harness) -> None:
    harness.user("alice")
    for headers in (
        {},
        {"Authorization": "Basic abc"},
        {"Authorization": "Bearer not-a-jwt"},
        {"Authorization": f"Bearer {harness.key.token('user_alice', exp=1)}"},
        {"Authorization": f"Bearer {harness.key.token('user_alice', iss='https://evil')}"},
    ):
        response = harness.client.get(f"{API}/me", headers=headers)
        assert response.status_code == 401, headers
        assert response.json()["code"] == "unauthenticated"


def test_first_request_provisions_user_just_in_time(harness: Harness) -> None:
    me = harness.me(harness.user("alice"))
    assert me["user"]["email"] == "alice@example.com"
    assert me["memberships"] == []
    harness.me(harness.user("alice"))
    assert _count(harness, "users") == 1


def test_unverified_email_is_blocked(harness: Harness) -> None:
    response = harness.client.get(f"{API}/me", headers=harness.user("bob", verified=False))
    assert response.status_code == 403
    assert response.json()["code"] == "email_unverified"


# ---- WF-01 webhooks -----------------------------------------------------------------------


def test_at_01_3_duplicate_user_created_webhook_creates_one_user(harness: Harness) -> None:
    body = json.dumps(
        {"type": "user.created", "data": clerk_user_payload("user_w", "W@Example.com")}
    ).encode()
    for _ in range(2):
        response = harness.client.post(
            f"{API}/webhooks/clerk", content=body, headers=svix_headers(body)
        )
        assert response.status_code == 204, response.text
    row = harness.owner_conn.execute(
        "SELECT email, email_verified FROM users WHERE auth_provider_user_id = 'user_w'"
    ).fetchall()
    assert row == [("w@example.com", True)]


def test_webhook_with_bad_signature_is_rejected(harness: Harness) -> None:
    body = json.dumps({"type": "user.created", "data": clerk_user_payload("u", "u@x.io")}).encode()
    headers = svix_headers(body, secret="whsec_" + "QUJD" * 8)
    response = harness.client.post(f"{API}/webhooks/clerk", content=body, headers=headers)
    assert response.status_code == 401
    assert _count(harness, "users") == 0


def test_user_deleted_webhook_revokes_access(harness: Harness) -> None:
    headers = harness.user("carol")
    harness.me(headers)
    body = json.dumps({"type": "user.deleted", "data": {"id": "user_carol"}}).encode()
    assert (
        harness.client.post(f"{API}/webhooks/clerk", content=body, headers=svix_headers(body))
    ).status_code == 204
    assert harness.client.get(f"{API}/me", headers=headers).status_code == 401


# ---- WF-02 organizations ------------------------------------------------------------------


def test_at_02_1_create_org_makes_caller_owner(harness: Harness) -> None:
    alice = harness.user("alice")
    org = harness.create_org(alice, "Acme Légal & Co")
    assert org["slug"] == "acme-legal-co"
    assert org["timezone"] == "UTC"
    me = harness.me(alice)
    assert [(m["organization"]["id"], m["role"]) for m in me["memberships"]] == [
        (org["id"], "owner")
    ]
    # Same name again gets a distinct slug.
    assert harness.create_org(alice, "Acme Légal & Co")["slug"] != org["slug"]


def test_create_org_validates_input(harness: Harness) -> None:
    response = harness.client.post(
        f"{API}/orgs",
        json={"name": " ", "timezone": "Mars/Base", "size_band": "huge", "extra": 1},
        headers=harness.user("alice"),
    )
    assert response.status_code == 400
    fields = {e["field"] for e in response.json()["errors"]}
    assert {"name", "timezone", "size_band", "extra"} <= fields


def test_at_02_3_org_limit_per_user(harness: Harness, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(get_settings(), "max_orgs_per_user", 1)
    alice = harness.user("alice")
    harness.create_org(alice)
    response = harness.client.post(f"{API}/orgs", json={"name": "Second"}, headers=alice)
    assert response.status_code == 402
    assert response.json()["code"] == "entitlement_exceeded"


def test_org_read_update_delete_permissions(harness: Harness) -> None:
    owner = harness.user("owner")
    org = harness.create_org(owner)
    admin = harness.join(owner, org["id"], "adele", "admin")
    member = harness.join(owner, org["id"], "mike", "member")
    stranger = harness.user("stranger")
    url = f"{API}/orgs/{org['id']}"

    assert harness.client.get(url, headers=member).status_code == 200
    assert harness.client.get(url, headers=stranger).status_code == 404  # existence not leaked
    assert harness.client.patch(url, json={"name": "X"}, headers=member).status_code == 403
    response = harness.client.patch(
        url, json={"name": "Renamed", "timezone": "Europe/London"}, headers=admin
    )
    assert response.status_code == 200
    assert (response.json()["name"], response.json()["timezone"]) == ("Renamed", "Europe/London")
    assert harness.client.delete(url, headers=admin).status_code == 403
    assert harness.client.delete(url, headers=owner).status_code == 204
    assert harness.client.get(url, headers=owner).status_code == 404
    assert harness.me(owner)["memberships"] == []


def test_transfer_ownership(harness: Harness) -> None:
    owner = harness.user("owner")
    org = harness.create_org(owner)
    member = harness.join(owner, org["id"], "mike", "member")
    mike_id = harness.me(member)["user"]["id"]

    response = harness.client.post(
        f"{API}/orgs/{org['id']}/transfer-ownership",
        json={"new_owner_user_id": mike_id},
        headers=owner,
    )
    assert response.status_code == 204, response.text
    assert harness.me(member)["memberships"][0]["role"] == "owner"
    assert harness.me(owner)["memberships"][0]["role"] == "admin"
    assert (
        harness.client.get(f"{API}/orgs/{org['id']}", headers=owner).json()["owner_user_id"]
        == mike_id
    )


# ---- WF-03 invitations --------------------------------------------------------------------


def test_at_03_1_and_2_invite_accept_once(harness: Harness) -> None:
    owner = harness.user("owner")
    org = harness.create_org(owner)
    response, token = harness.invite(owner, org["id"], "Bea@Example.com", "admin")
    assert response.status_code == 201, response.text
    assert response.json()["email"] == "bea@example.com"
    assert token is not None
    assert harness.mail.sent[-1].to == "bea@example.com"

    preview = harness.client.post(f"{API}/invitations/preview", json={"token": token})
    assert preview.status_code == 200
    assert preview.json()["organization_name"] == "Acme Legal"
    assert preview.json()["email_hint"] == "b***@example.com"

    bea = harness.user("bea")
    accepted = harness.client.post(f"{API}/invitations/accept", json={"token": token}, headers=bea)
    assert accepted.status_code == 200, accepted.text
    assert accepted.json()["role"] == "admin"
    assert harness.me(bea)["memberships"][0]["organization"]["id"] == org["id"]

    again = harness.client.post(f"{API}/invitations/accept", json={"token": token}, headers=bea)
    assert (again.status_code, again.json()["code"]) == (410, "invitation_used")


def test_at_03_3_invite_for_a_cannot_be_accepted_by_b(harness: Harness) -> None:
    owner = harness.user("owner")
    org = harness.create_org(owner)
    _, token = harness.invite(owner, org["id"], "anna@example.com")
    response = harness.client.post(
        f"{API}/invitations/accept", json={"token": token}, headers=harness.user("brian")
    )
    assert response.status_code == 403
    assert response.json()["code"] == "invitation_email_mismatch"
    assert "anna" not in response.text  # masked


def test_at_03_4_seat_limit(harness: Harness, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(get_settings(), "default_seats_max", 2)
    owner = harness.user("owner")
    org = harness.create_org(owner)
    assert harness.invite(owner, org["id"], "one@example.com")[0].status_code == 201
    response, token = harness.invite(owner, org["id"], "two@example.com")
    assert response.status_code == 402
    assert response.json()["code"] == "entitlement_exceeded"
    assert token is None  # nothing emailed


def test_expired_revoked_and_rotated_tokens(harness: Harness) -> None:
    owner = harness.user("owner")
    org = harness.create_org(owner)
    headers = {**owner, "X-Org-Id": org["id"]}

    _, expired = harness.invite(owner, org["id"], "exp@example.com")
    harness.owner_conn.execute(
        "UPDATE invitations SET expires_at = %s WHERE email = 'exp@example.com'",
        (datetime.now(UTC) - timedelta(minutes=1),),
    )
    response = harness.client.post(f"{API}/invitations/preview", json={"token": expired})
    assert (response.status_code, response.json()["code"]) == (410, "invitation_expired")

    response, revoked = harness.invite(owner, org["id"], "rev@example.com")
    invitation_id = response.json()["id"]
    assert (
        harness.client.delete(f"{API}/invitations/{invitation_id}", headers=headers).status_code
        == 204
    )
    response = harness.client.post(f"{API}/invitations/preview", json={"token": revoked})
    assert (response.status_code, response.json()["code"]) == (410, "invitation_revoked")

    response, old = harness.invite(owner, org["id"], "rot@example.com")
    resent = harness.client.post(
        f"{API}/invitations/{response.json()['id']}/resend", headers=headers
    )
    assert resent.status_code == 200
    new = harness.mail.sent[-1].body_text.split("#token=")[1].split()[0]
    assert new != old
    assert harness.client.post(f"{API}/invitations/preview", json={"token": old}).status_code == 404
    assert harness.client.post(f"{API}/invitations/preview", json={"token": new}).status_code == 200

    listed = harness.client.get(f"{API}/invitations", headers=headers).json()["items"]
    assert [i["email"] for i in listed] == ["rot@example.com"]  # only pending ones


def test_duplicate_invites_and_existing_members_conflict(harness: Harness) -> None:
    owner = harness.user("owner")
    org = harness.create_org(owner)
    harness.join(owner, org["id"], "mike", "member")
    assert harness.invite(owner, org["id"], "new@example.com")[0].status_code == 201

    dup, _ = harness.invite(owner, org["id"], "NEW@example.com")
    assert (dup.status_code, dup.json()["code"]) == (409, "invitation_pending")
    member, _ = harness.invite(owner, org["id"], "mike@example.com")
    assert (member.status_code, member.json()["code"]) == (409, "already_member")


def test_invitation_tokens_are_stored_hashed(harness: Harness) -> None:
    owner = harness.user("owner")
    org = harness.create_org(owner)
    _, token = harness.invite(owner, org["id"], "x@example.com")
    assert token is not None
    stored = harness.owner_conn.execute("SELECT token_hash FROM invitations").fetchone()
    assert stored is not None and token not in stored[0] and len(stored[0]) == 64


def test_owner_role_cannot_be_granted_by_invitation(harness: Harness) -> None:
    owner = harness.user("owner")
    org = harness.create_org(owner)
    response, _ = harness.invite(owner, org["id"], "x@example.com", "owner")
    assert response.status_code == 400


# ---- members ------------------------------------------------------------------------------


def test_members_list_update_remove(harness: Harness) -> None:
    owner = harness.user("owner")
    org = harness.create_org(owner)
    admin = harness.join(owner, org["id"], "adele", "admin")
    harness.join(owner, org["id"], "mike", "member")
    harness.join(owner, org["id"], "vera", "viewer")
    headers = {**admin, "X-Org-Id": org["id"]}

    first = harness.client.get(f"{API}/members?limit=3", headers=headers).json()
    assert len(first["items"]) == 3 and first["next_cursor"]
    rest = harness.client.get(
        f"{API}/members?limit=3&cursor={first['next_cursor']}", headers=headers
    ).json()
    members = {m["user"]["email"]: m for m in first["items"] + rest["items"]}
    assert rest["next_cursor"] is None
    assert len(members) == 4

    mike = members["mike@example.com"]["id"]
    response = harness.client.patch(
        f"{API}/members/{mike}",
        json={"role": "viewer", "capabilities": ["approver", "approver"]},
        headers=headers,
    )
    assert response.status_code == 200
    assert (response.json()["role"], response.json()["capabilities"]) == ("viewer", ["approver"])

    owner_membership = members["owner@example.com"]["id"]
    for call in (
        harness.client.patch(
            f"{API}/members/{owner_membership}", json={"role": "member"}, headers=headers
        ),
        harness.client.delete(f"{API}/members/{owner_membership}", headers=headers),
    ):
        assert (call.status_code, call.json()["code"]) == (409, "owner_protected")

    assert harness.client.delete(f"{API}/members/{mike}", headers=headers).status_code == 204
    assert (
        harness.client.patch(
            f"{API}/members/{mike}", json={"role": "admin"}, headers=headers
        ).status_code
        == 404
    )


def test_tenant_boundaries(harness: Harness) -> None:
    alice, bob = harness.user("alice"), harness.user("bob")
    org_a, org_b = harness.create_org(alice, "A"), harness.create_org(bob, "B")
    b_members = harness.client.get(
        f"{API}/members", headers={**bob, "X-Org-Id": org_b["id"]}
    ).json()["items"]

    # Not a member of B.
    response = harness.client.get(f"{API}/members", headers={**alice, "X-Org-Id": org_b["id"]})
    assert (response.status_code, response.json()["code"]) == (403, "org_membership_required")
    # Admin of A cannot reach B's membership through A's context.
    response = harness.client.delete(
        f"{API}/members/{b_members[0]['id']}", headers={**alice, "X-Org-Id": org_a["id"]}
    )
    assert response.status_code == 404
    # Unknown or malformed org IDs.
    assert (
        harness.client.get(f"{API}/members", headers={**alice, "X-Org-Id": new_uuid()}).status_code
        == 403
    )
    assert (
        harness.client.get(f"{API}/members", headers={**alice, "X-Org-Id": "nope"}).status_code
        == 400
    )


# ---- AZ-01: identity endpoints x roles ----------------------------------------------------

# (method, path template, body, roles allowed). Mirrors spec 02 §2 and spec 08 §2.
MATRIX: list[tuple[str, str, dict[str, Any] | None, set[str]]] = [
    ("GET", "/orgs/{org}", None, {"owner", "admin", "member", "viewer"}),
    ("PATCH", "/orgs/{org}", {"industry": "Law"}, {"owner", "admin"}),
    ("GET", "/members", None, {"owner", "admin", "member", "viewer"}),
    ("PATCH", "/members/{target}", {"capabilities": []}, {"owner", "admin"}),
    ("GET", "/invitations", None, {"owner", "admin"}),
    ("POST", "/invitations", {"email": "az@example.com"}, {"owner", "admin"}),
    ("POST", "/orgs/{org}/transfer-ownership", {"new_owner_user_id": "{target_user}"}, {"owner"}),
    ("DELETE", "/members/{target}", None, {"owner", "admin"}),
    ("DELETE", "/orgs/{org}", None, {"owner"}),
]


@pytest.mark.parametrize("role", ["owner", "admin", "member", "viewer"])
def test_az_01_identity_matrix(harness: Harness, role: str) -> None:
    owner = harness.user("owner")
    org = harness.create_org(owner)
    actor = owner if role == "owner" else harness.join(owner, org["id"], role, role)
    target_headers = harness.join(owner, org["id"], "target", "member")
    target_user = harness.me(target_headers)["user"]["id"]
    members = harness.client.get(f"{API}/members", headers={**owner, "X-Org-Id": org["id"]}).json()[
        "items"
    ]
    target = next(m["id"] for m in members if m["user"]["id"] == target_user)

    for method, template, body, allowed in MATRIX:
        path = template.format(org=org["id"], target=target)
        payload = (
            json.loads(json.dumps(body).replace("{target_user}", target_user)) if body else None
        )
        response = harness.client.request(
            method, API + path, json=payload, headers={**actor, "X-Org-Id": org["id"]}
        )
        expected_ok = role in allowed
        assert (response.status_code < 400) == expected_ok, (
            method,
            path,
            role,
            response.status_code,
            response.text,
        )
        if not expected_ok:
            assert response.json()["code"] == "forbidden"
        if expected_ok and path.endswith("transfer-ownership"):
            # Hand ownership back so the remaining rows run with the same roles.
            back = harness.client.post(
                f"{API}/orgs/{org['id']}/transfer-ownership",
                json={"new_owner_user_id": harness.me(owner)["user"]["id"]},
                headers=target_headers,
            )
            assert back.status_code == 204, back.text


def test_debug_endpoint_requires_platform_admin(harness: Harness) -> None:
    alice = harness.user("alice")
    harness.me(alice)
    assert harness.client.post(f"{API}/admin/debug/raise", headers=alice).status_code == 404
    harness.owner_conn.execute(
        "UPDATE users SET is_platform_admin = true WHERE auth_provider_user_id = 'user_alice'"
    )
    assert harness.client.post(f"{API}/admin/debug/raise", headers=alice).status_code == 500


def test_webhook_unconfigured_is_503(harness: Harness, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(get_settings(), "auth_webhook_secret", None)
    assert harness.client.post(f"{API}/webhooks/clerk", content=b"{}").status_code == 503
