# Implementation Status

**As of 2026-10-15: M0 and M1 are implemented locally and committed, not pushed** (the repo is still public, KI-005). No external services, accounts or cloud infrastructure have been created — including no Clerk instance, so M1 has not been exercised against real Clerk yet (KI-011).

## M1 evidence (2026-10-15)
| Exit criterion (roadmap M1, spec 11 §12) | Result |
|---|---|
| Auth provider integration: API verifies Clerk JWTs (JWKS, iss/exp/nbf/aud/azp) | Implemented; unit-tested with locally generated RS256 keys and a fake JWKS (expired, wrong issuer, wrong azp, `alg:none`, HS256, unknown key, key rotation) |
| WF-01 registration: `user.created` webhook idempotent; JIT provisioning; unverified email blocked | AT-01-3 passes (integration). AT-01-1/AT-01-2 are Clerk behaviour: **verify in Clerk dashboard config** (KI-011) |
| WF-02 org creation: org + Owner membership in one transaction; org limit | AT-02-1 (org part) and AT-02-3 pass. Default policies (M8), trial subscription (M11) and the executive-team step (M5) are not in M1 |
| WF-03 invitations: hashed single-use token, 7-day expiry, email match, seat limit, revoke/resend | AT-03-1…4 pass, plus expiry/revocation/rotation, duplicates, hashing. Email delivered to Mailpit over SMTP (verified manually) |
| AZ-01 for identity endpoints | Table-driven test over 4 roles × 9 endpoint rows passes |
| Tenant boundaries on identity routes | Non-member → 403 `org_membership_required` (X-Org-Id) or 404 (`/orgs/{id}`); cross-org membership IDs → 404 |
| Screens S-01, S-02 (Clerk), S-05, S-06, S-49 (with roles tab), S-53 (Clerk), org switcher | Built; build/lint/type/unit tests pass (20 frontend tests incl. S-05 states). **Not clicked through in a browser against real Clerk** (KI-011) |
| Debug endpoint restricted to platform admins | Done (KI-007 resolved) |
| Test totals | Backend 84 (57 unit + 27 integration on a throwaway DB as the app role); frontend 20 |

## M0 evidence (2026-10-15)
| Exit criterion (roadmap M0) | Result |
|---|---|
| Monorepo layout `frontend/`, `backend/`, `infra/`, `docs/`, `.github/` | Done |
| `docker compose up` brings up db (Postgres 16 + pgvector), redis, s3 (SeaweedFS), migrate, api | Verified: all healthy; `/healthz` 200, `/readyz` 200 with DB, migrations-at-head and Redis checks |
| Two DB roles: owner for migrations, `advolevel_app` without BYPASSRLS for the API | Verified (`rolbypassrls` f for the app role); the API container receives no owner credentials |
| Alembic baseline (`vector`, `pgcrypto`), upgrade/downgrade round-trip | Verified locally |
| Structured JSON logs with `request_id` (+ `trace_id` when tracing), full route templates, redaction | Verified (unit tests + container logs) |
| RFC 9457 problem+json errors carrying `request_id` | Verified |
| Sentry (backend and frontend) + OpenTelemetry wiring, scrubbing `before_send` | Wired and unit-tested. **Delivery to Sentry not verified: no DSN exists yet (KI-008)** |
| Backend quality gates: ruff format/check, mypy strict, pytest | 32 tests pass (31 unit + 1 integration against compose) |
| Frontend quality gates: eslint, prettier, tsc, vitest, `next build` | All pass; 13 tests |
| CI workflow (`.github/workflows/ci.yml`): backend, backend-integration, frontend, gitleaks | Written. **Not yet run on GitHub** (nothing pushed) |
| Pre-commit (gitleaks, ruff, prettier) | Config written; install with `uvx pre-commit install` |
| Design tokens (spec 05) as Tailwind v4 theme; placeholder app shell | Done (full shell is M3) |

## Milestones
| Milestone | Status | Started | Completed | Notes |
|---|---|---|---|---|
| M0 Repository foundation | Done locally; CI pending first push | 2026-10-15 | — | Complete after CI passes on GitHub and Sentry delivery is verified (KI-008) |
| M1 Auth, orgs, RBAC | Done locally; needs a Clerk dev instance to verify end to end | 2026-10-15 | — | Clerk chosen (OQ-019); email deferred to Mailpit (OQ-029). "Done when invite → accept → role-scoped access works end to end" is proven by API integration tests, not yet through the browser (KI-011) |
| M2 Tenant isolation & audit | Not started | — | — | |
| M3 Design system & shell | Not started | — | — | Needs OQ-025 |
| M4 Org DNA & RAG | Not started | — | — | Needs OQ-005, OQ-013 |
| M5 Executive Brain & Offices | Not started | — | — | Needs OQ-003, OQ-004, OQ-013 |
| M6 Boardrooms | Not started | — | — | Needs OQ-031 |
| M7 Work management | Not started | — | — | Needs OQ-032 |
| M8 Governance & approvals | Not started | — | — | Needs OQ-021 |
| M9 Integrations | Not started | — | — | Needs OQ-007…010, OQ-017 |
| M10 Content Factory | Not started | — | — | Needs OQ-012, OQ-022 |
| M11 Billing & entitlements | Not started | — | — | Needs OQ-011 |
| M12 Monitoring, backup, admin | Not started | — | — | Needs OQ-014, OQ-018 |
| M13 Hardening | Not started | — | — | |
| M14 Deploy, UAT, handover | Not started | — | — | |

## Documentation status
| Document | Status |
|---|---|
| PROJECT_BASELINE.md | Draft v0.1 |
| specifications/01–15 | Draft v0.1, pending client review and SOW reconciliation |
| Tracking documents | Draft v0.1 |

## Update rule
Update this file at the end of every working day and at each milestone completion. Link the PRs and the test evidence.
