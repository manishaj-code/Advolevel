# Technical Debt Register

Code-level debt is recorded from M0 (2026-10-15) onward.

## How to record debt
Each entry gives: what was compromised, why, the risk if left, the payoff plan, and the target milestone. Debt that touches tenant isolation, governance or secrets is never "accepted". It must be scheduled.

| ID | Area | Description | Reason incurred | Risk | Payoff plan | Target | Status |
|---|---|---|---|---|---|---|---|
| TD-000 | Process | Local folder not under version control; no CI | Greenfield | Lost work, no review trail | Repo connected; CI workflow written (M0). Remaining: first CI run and branch protection after the push (KI-005) | M0 | Partly paid |
| TD-001 | Frontend deps | `npm audit` reports 5 high advisories, all **dev-only** (braces/micromatch via `eslint-config-next`). Production deps: 0 | Upstream fix not yet released in the Next 16.4 lint config | Low: not shipped to users, affects lint tooling only | CI gates `npm audit --omit=dev --audit-level=high`; re-check on each Next upgrade | M13 | Open |
| TD-002 | Observability | Access-log route template reads FastAPI's internal `scope["fastapi"]["effective_route_context"]` (FastAPI ≥ 0.140 stores included-router routes relative to their prefix) | No public API for the full template | A FastAPI upgrade could drop it; the fallback logs the relative path | Covered by `test_access_log_uses_full_route_template`; replace if FastAPI adds a public API | M13 | Open |
| TD-003 | Tests | `starlette.testclient` warns that `httpx` use is deprecated in favour of `httpx2` | Current FastAPI TestClient still uses it | Breaks on a future Starlette major | Switch when FastAPI's TestClient moves | M13 | Open |

## Planned / anticipated debt (accepted deliberately in the plan — PROPOSED)
| ID | Description | Why acceptable for V1 | Revisit trigger |
|---|---|---|---|
| TD-P01 | A single Postgres for OLTP + vectors | Simplicity; adequate at the assumed scale | > ~5M chunks or p95 retrieval > 300 ms |
| TD-P02 | Fixed governance condition set (no general expression language) | Reduces bypass/complexity risk | Client needs custom conditions |
| TD-P03 | Sequential boardroom turns only | Predictable cost and UX | Latency complaints |
| TD-P04 | `usage_events` not partitioned | Low volume initially | Table > 50M rows |
| TD-P05 | Light content area + dark sidebar only (no full dark theme) | Pending OQ-035 | Client request |
