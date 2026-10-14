# 12 — Deployment and DevOps

| Field | Value |
|---|---|
| Status | DRAFT v0.1. Nothing has been deployed or configured. Hosting provider NEEDS CLARIFICATION (OQ-014). |
| Date | 2026-10-14 |

## 1. Environments
| Env | Purpose | Data | Deploy trigger |
|---|---|---|---|
| local | Developer machines | Seed/fake data | `docker compose up` |
| preview (optional) | Per-PR frontend previews | Shared staging API or mocks | PR opened |
| staging | Integration, E2E, UAT | Synthetic + client demo data; **never production data** | Merge to `main` |
| production | Live tenants | Real | Tagged release + manual approval |

Separate cloud projects/accounts or isolated namespaces per environment. Separate Stripe test/live keys, separate OAuth apps or redirect URIs, and separate Sentry environments.

## 2. Environment variables (names only — never values)
| Variable | Service | Notes |
|---|---|---|
| `APP_ENV` | all | local/staging/production |
| `DATABASE_URL` | api, worker | App role (no BYPASSRLS) |
| `DATABASE_MIGRATION_URL` | migration job | Owner role, used only by migrations |
| `REDIS_URL` | api, worker | |
| `S3_BUCKET`, `S3_REGION`, `S3_ENDPOINT`, `S3_ACCESS_KEY_ID`, `S3_SECRET_ACCESS_KEY` | api, worker | Prefer workload identity over keys where the host supports it |
| `AUTH_ISSUER`, `AUTH_AUDIENCE`, `AUTH_JWKS_URL`, `AUTH_SECRET_KEY`, `AUTH_WEBHOOK_SECRET` | api | Names depend on the provider |
| `NEXT_PUBLIC_AUTH_PUBLISHABLE_KEY`, `NEXT_PUBLIC_API_BASE_URL` | web | Public by design |
| `ANTHROPIC_API_KEY`, `OPENAI_API_KEY`, `EMBEDDINGS_API_KEY` | api, worker | Per provider chosen |
| `STRIPE_SECRET_KEY`, `STRIPE_WEBHOOK_SECRET`, `NEXT_PUBLIC_STRIPE_PUBLISHABLE_KEY` | api / web | |
| `CLICKUP_CLIENT_ID/SECRET`, `GHL_CLIENT_ID/SECRET`, `DROPBOX_APP_KEY/SECRET`, `GOOGLE_CLIENT_ID/SECRET` | api, worker | + per-provider webhook secrets |
| `ENCRYPTION_MASTER_KEY` or `KMS_KEY_ID` | api, worker | Token vault |
| `SENTRY_DSN`, `NEXT_PUBLIC_SENTRY_DSN`, `SENTRY_ENVIRONMENT`, `SENTRY_RELEASE` | all | |
| `OTEL_EXPORTER_OTLP_ENDPOINT`, `OTEL_EXPORTER_OTLP_HEADERS`, `OTEL_SERVICE_NAME` | all | |
| `EMAIL_PROVIDER_API_KEY`, `EMAIL_FROM` | worker | |
| `CORS_ORIGINS`, `APP_BASE_URL` | api | |

Configuration is validated at startup (Pydantic Settings). The app fails fast if a required variable is missing.

## 3. Repository and branching (PROPOSED)
- Monorepo: `frontend/`, `backend/`, `infra/`, `docs/`, `.github/`.
- Trunk-based: short-lived feature branches → PR → `main`. Conventional commits. Required reviews: 1 (2 for `governance/`, `identity/`, `billing/`, migrations).
- Branch protection: CI required, no force-push to `main`.

## 4. CI/CD pipeline (PROPOSED: GitHub Actions)
1. **PR**: install (cached) → lint → type-check → unit → integration (Testcontainers) → API/contract → security scans → build images → (optional) preview deploy.
2. **main**: build and push versioned images (`git sha`) → run migrations on staging (job) → deploy staging → smoke tests → E2E (nightly or on-demand).
3. **release**: tag `vX.Y.Z` → manual approval → production migration job → deploy api/worker/web (rolling) → smoke → Sentry release + source maps uploaded → release notes.

## 5. Database migrations
- Alembic, linear history. One migration per PR where possible.
- **Expand → migrate → contract** pattern: never drop or rename a column in the same release that stops using it.
- Migrations run as a separate job before the app rollout, using the owner role. The app uses the restricted role.
- Every migration is tested: upgrade on a copy of staging data, downgrade where feasible, RLS policy presence checked by TI-11.
- Long operations (index builds) use `CREATE INDEX CONCURRENTLY` and are scheduled.

## 6. Deployment
- Container images (multi-stage, non-root user, minimal base, pinned digests).
- Rolling deploys with health checks: `/healthz` (liveness), `/readyz` (DB + Redis reachable, migrations at head).
- Workers drain gracefully (SIGTERM → finish the current job or re-queue).
- Feature flags for incomplete or risky features (e.g. integration write ops per provider).

## 7. Secrets
Stored in the host's secret manager. Injected at runtime. Access limited to deployers. Rotated per the runbook (spec 10 §4). Never echoed in CI logs (masked). Separate per environment.

## 8. TLS and domains
- Managed TLS certificates (auto-renew) on all public endpoints. HSTS.
- Domains (PROPOSED): `app.<domain>` (web), `api.<domain>` (API), webhooks under `api.<domain>/api/v1/webhooks/*`. The domain is NEEDS CLARIFICATION (OQ-017).

## 9. Rollback
- App: redeploy the previous image tag (one command/click). Target < 10 min.
- DB: the expand/contract discipline makes app rollback safe without DB rollback. Destructive data issues → PITR restore (spec 13).
- Feature-flag kill switches for AI features, integration writes and Content publishing.

## 10. Infrastructure ownership and handover
**CONFIRMED (SOW §6):** deployment goes into **AdvoLevel-controlled infrastructure and accounts**. All commissioned source, designs and custom artifacts belong to AdvoLevel on payment.

| Asset | Owner | Status |
|---|---|---|
| Cloud/hosting account | AdvoLevel (vendor gets delegated admin access during the build) | CONFIRMED owner; provider OQ-014 |
| Domain/DNS | AdvoLevel | Domain name OQ-017 |
| Git repository | AdvoLevel. The current repo `manishaj-code/Advolevel` is under a personal account and **must be transferred to, or recreated in, an AdvoLevel-controlled GitHub organization** (KI-006) | Action required |
| Figma workspace | AdvoLevel | CONFIRMED |
| Stripe, AI providers, transcription, integration developer apps (ClickUp, GHL, Dropbox, Google), Sentry, observability, email | AdvoLevel-owned accounts; vendor uses invited/delegated access | CONFIRMED owner; access timing OQ-017 |

**Handover pack (CONFIRMED contents, SOW §6):**
1. Source repository (full history) in an AdvoLevel organization.
2. Editable Figma files and exported assets.
3. **Configurations and prompts**: executive templates, platform safety rules, prompt files, model routing table, governance default policies, plan/entitlement definitions, all exported as versioned files in the repo.
4. Deployment instructions (README + runbooks: deploy, rollback, migrations, restore, key rotation, incident response).
5. **Credentials inventory**: every account, key and secret (name, purpose, location in the secret store, owner, rotation procedure). It lists **no secret values**.
6. Monitoring and backup basics: configured Sentry, dashboards, alerts, backups, plus a restore-drill record.
7. Technical documentation: these specs updated to as-built, API reference (OpenAPI), data model.
8. **Third-party licence inventory**: all open-source dependencies with licences (generated SBOM), fonts, icon sets and paid services.
9. Known issues and the technical debt register.
10. A recorded walkthrough session.

**Warranty and defect correction (to be PROPOSED by the vendor; SOW §6 requires defined terms):** suggested starting point for the commercial proposal: a 90-day warranty after production acceptance; defects classified Critical/High/Medium/Low with response targets; fixes for defects against the accepted specs at no charge; exclusions for third-party outages, client-modified code and scope changes. Final terms are a commercial decision (OQ-018).

## 11. Release checklist
- [ ] All CI gates green; no open critical/high vulnerabilities
- [ ] Migrations reviewed; expand/contract verified; backup taken before migration
- [ ] Tenant-isolation and approval-bypass suites green
- [ ] Feature flags set as intended for production
- [ ] Sentry release created; source maps uploaded
- [ ] Smoke tests pass post-deploy; dashboards normal for 30 min
- [ ] Release notes and `IMPLEMENTATION_STATUS.md` updated
- [ ] Rollback plan confirmed for this release
