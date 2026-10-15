# Technical Debt Register

Code-level debt is recorded from M0 (2026-10-15) onward.

## How to record debt
Each entry gives: what was compromised, why, the risk if left, the payoff plan, and the target milestone. Debt that touches tenant isolation, governance or secrets is never "accepted". It must be scheduled.

| ID | Area | Description | Reason incurred | Risk | Payoff plan | Target | Status |
|---|---|---|---|---|---|---|---|
| TD-000 | Process | Local folder not under version control; no CI | Greenfield | Lost work, no review trail | Repo connected; CI workflow written (M0). Remaining: first CI run and branch protection after the push (KI-005) | M0 | Partly paid |
| TD-001 | Frontend deps | `npm audit` reports 5 high advisories, all **dev-only** (braces/micromatch via `eslint-config-next`). Production deps: 0 | Upstream fix not yet released in the Next 16.4 lint config | Low: not shipped to users, affects lint tooling only | CI gates `npm audit --omit=dev --audit-level=high`; re-check on each Next upgrade | M13 | Open |
| TD-002 | Observability | Access-log route template reads FastAPI's internal `scope["fastapi"]["effective_route_context"]` (FastAPI ≥ 0.140 stores included-router routes relative to their prefix) | No public API for the full template | A FastAPI upgrade could drop it; the fallback logs the relative path | Covered by `test_access_log_uses_full_route_template`; replace if FastAPI adds a public API | M13 | Open |
| TD-004 | Identity | Invitation emails are sent with FastAPI `BackgroundTasks` after commit: no retry, and failures are only logged; bounces are not shown on S-49 | No worker yet (DEC-025) | Lost invite emails (the admin can resend) | Move to a retried job and track delivery status | M4 | Open |
| TD-005 | Identity | Audit events go to the structured log only (`app/core/audit.py`) | `audit_events` table is M2 scope | No tamper-evident record of M1 membership changes | M2 swaps the implementation; call sites stay | M2 | Open |
| TD-006 | Identity | `POST /invitations/preview` (public) is not rate limited | Rate limiting is M2 scope | Token guessing is infeasible (256-bit tokens) but the endpoint can be hammered | Per-IP limit in M2 | M2 | Open |
| TD-007 | Identity | Seat and org-count limits come from settings (`DEFAULT_SEATS_MAX`, `MAX_ORGS_PER_USER`, default unlimited) | Plans and entitlements are M11 (OQ-011, OQ-006) | Limits not enforced per plan | `app/core/entitlements.py` reads plans in M11 | M11 | Open |
| TD-008 | Frontend | UI primitives (`components/ui/*`) are minimal and hand-rolled; S-49 tables are not yet responsive cards on mobile | Design system is M3 | Inconsistent UI until M3 | Replace with the M3 component library | M3 | Open |
| TD-003 | Tests | `starlette.testclient` warns that `httpx` use is deprecated in favour of `httpx2` | Current FastAPI TestClient still uses it | Breaks on a future Starlette major | Switch when FastAPI's TestClient moves | M13 | Open |

## Planned / anticipated debt (accepted deliberately in the plan — PROPOSED)
| ID | Description | Why acceptable for V1 | Revisit trigger |
|---|---|---|---|
| TD-P01 | A single Postgres for OLTP + vectors | Simplicity; adequate at the assumed scale | > ~5M chunks or p95 retrieval > 300 ms |
| TD-P02 | Fixed governance condition set (no general expression language) | Reduces bypass/complexity risk | Client needs custom conditions |
| TD-P03 | Sequential boardroom turns only | Predictable cost and UX | Latency complaints |
| TD-P04 | `usage_events` not partitioned | Low volume initially | Table > 50M rows |
| TD-P05 | Light content area + dark sidebar only (no full dark theme) | Pending OQ-035 | Client request |
