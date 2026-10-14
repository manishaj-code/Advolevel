# Development Plan — Starting Tomorrow

The milestone detail is in `specifications/14-development-roadmap.md`. This file is the operational plan: what happens first, what needs approval, and how work is run.

## 1. Approvals needed before coding starts (review session)
| # | Item | Ref | Needed for |
|---|---|---|---|
| 1 | Approve or adjust the stack decisions DEC-001…DEC-011 | DECISION_LOG | M0 |
| 2 | ~~Confirm where the git repository lives~~ Answered: `github.com/manishaj-code/Advolevel` (DEC-019). **Still to decide: make it private** (KI-005) and whether it later moves to a client-owned org | OQ-017 | M0 day 1 |
| 3 | Confirm there is no existing codebase or mandated stack | OQ-020 | M0 |
| 4 | Agree that M0–M2 may proceed while the SOW reconciliation runs in parallel | RSK-001 | M0 |
| 5 | Send the client the "Ask first" and "Ask this week" questions | OPEN_QUESTIONS | M1–M5 |

If items 1–3 are not approved, **do not scaffold**. Spend the day on SOW reconciliation and the questions instead.

## 2. Day 1 plan (M0 start)
1. Set `manishaj-code/Advolevel` to private. In `D:\Projects\Advolevel`: `git init -b main`, add a `.gitignore` (including `.env*` except `.env.example`, `prompt.md` if it shouldn't be shared), `git remote add origin https://github.com/manishaj-code/Advolevel.git`, commit `docs/`, push. Then enable branch protection on `main` (PR required, CI required, no force-push).
2. Create the monorepo layout (`frontend/`, `backend/`, `infra/`, `docs/`) and `README.md` with setup steps.
3. Backend skeleton: FastAPI app factory, settings validation, `/healthz` and `/readyz`, structured logging, request-ID middleware, Sentry + OTel bootstrap (DSNs optional locally).
4. Frontend skeleton: Next.js App Router + TypeScript + Tailwind with the spec 05 tokens; placeholder shell.
5. `docker-compose.yml`: Postgres 16 + pgvector, Redis, MinIO; Alembic initialized (empty baseline migration).
6. CI workflow: lint, type-check, unit tests, secret scan, for both apps.
7. `.env.example` with variable names only (spec 12 §2).
8. Update `IMPLEMENTATION_STATUS.md`.

## 3. First two weeks (indicative order, no date commitments)
| Order | Work | Milestone |
|---|---|---|
| 1 | Finish M0 (CI green, compose, Sentry test event) | M0 |
| 2 | Auth provider integration + users/orgs/memberships + invitations | M1 |
| 3 | RLS + TenantContext + TI suite harness + audit log | M2 |
| 4 | Entitlement service framework with a stub plan (so later features call it) | M11 (early slice) |
| 5 | Design tokens + core components + app shell (in parallel, by the frontend engineer) | M3 |
| 6 | SOW reconciliation: update the specs and the traceability matrix | Docs |

## 4. Suggested team shape (ASSUMED — adjust to the real team)
| Role | Focus |
|---|---|
| Tech lead / backend | M0, M2, M8, architecture ownership |
| Backend / AI engineer | M4, M5, M6, eval sets |
| Full-stack / frontend engineer | M3, screens across milestones |
| Integrations engineer (from M9) | M9, M11 |
| QA (part-time → full-time from M7) | Suites, E2E, release checks |
| Designer (client or vendor; OQ-025) | Figma F-1…F-7 |

## 5. Working agreements
- **Definition of Done (per PR)**: tests added and green; types and lint clean; tenant scope respected; no secrets; docs updated if behaviour or a contract changed; new tables have org_id + RLS or are allow-listed.
- **Definition of Done (per milestone)**: the acceptance criteria in spec 11 §12 are met with evidence; `IMPLEMENTATION_STATUS.md`, `REQUIREMENTS_TRACEABILITY.md` and `KNOWN_ISSUES.md` updated; demo given.
- **Decisions**: any change to a PROPOSED decision gets a `DECISION_LOG.md` entry.
- **Scope changes**: anything outside CONFIRMED scope is a change request, recorded and approved before work.
- **Feature flags**: integration write operations and publishing are behind flags until their test suites pass.

## 6. Parallelisation guide
- Parallel from the start: M3 (UI) alongside M1/M2.
- After M2: M11 billing and M4 RAG can run in parallel.
- After M5: M6, M7 and M8 can partly overlap. M8 must finish before any M9 write operation is enabled.
- M12 monitoring work is continuous. Formal completion happens before M13.
