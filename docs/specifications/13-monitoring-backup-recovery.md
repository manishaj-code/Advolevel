# 13 — Monitoring, Backup and Recovery

| Field | Value |
|---|---|
| Status | DRAFT v0.1. Tool choices PROPOSED. Nothing configured. |
| Date | 2026-10-14 |

## 1. Tool evaluation
| Need | Option | Assessment | Recommendation |
|---|---|---|---|
| Error tracking (FE + BE) | **Sentry** | First-class Next.js and FastAPI SDKs, issue grouping, releases, source maps, alerting; affordable team tier | **Adopt** (DEC-010) |
| | Rollbar / Bugsnag | Comparable but a smaller ecosystem for Next.js | — |
| Tracing | **OpenTelemetry** SDK (vendor-neutral) | Instrument FastAPI, SQLAlchemy, httpx, Redis, Celery/Dramatiq; custom spans for AI runs | **Adopt** as the instrumentation standard |
| Trace/metrics/logs backend | Grafana Cloud (Tempo/Prometheus/Loki) | Generous free tier, OTLP-native, good dashboards | **Recommended default** |
| | Datadog / New Relic | Powerful but expensive at scale | Consider if the client already uses them |
| | Sentry Performance | Could cover tracing alone, but less flexible for metrics | Acceptable budget fallback |
| | Host-native (e.g. platform logs) | Minimal, short retention | Not sufficient alone |
| LLM observability | OTel GenAI semantic conventions + our `ai_runs` table; optional Langfuse (self-host or cloud) | Prompt/version analytics | Start with our own tables + OTel. Add Langfuse if needed |
| Uptime / synthetics | Better Stack, Checkly, or Grafana synthetic monitoring | External probes | Adopt one |
| On-call / alert routing | Email + Slack/Teams channel; PagerDuty/Opsgenie if 24×7 is required | Depends on the support SLA (OQ-018) | |

Budget and existing client tooling are NEEDS CLARIFICATION (OQ-013/OQ-014).

## 2. Structured application logs
- JSON logs (structlog) to stdout and collected by the backend.
- Standard fields: `timestamp, level, service, env, release, request_id, trace_id, span_id, org_id, user_id (hashed or internal ID), route, method, status, duration_ms, event`.
- Never logged: request/response bodies by default, tokens, API keys, passwords, document contents, prompts and completions (except under an explicit per-org debug flag with an expiry), raw PII (email/phone are masked).
- Levels: DEBUG off in prod; INFO for lifecycle; WARNING for handled anomalies; ERROR → also goes to Sentry.

## 3. Centralized error tracking (Sentry)
- FE and BE SDKs, with environment and release tagged. Source maps uploaded on release.
- Context: `org_id`, `user_id` (internal), `request_id`, `ai_run_id`, `job_id`. A `before_send` scrubber applies the redaction rules (§10).
- Grouping: default fingerprinting + custom fingerprints for provider errors (`provider:{name}:{error_code}`) so that recurring integration failures group together.
- Issue workflow: new issue → triage label → link to a tracker ticket (§9).

## 4. Correlation IDs
- `X-Request-Id` is generated at the edge (or accepted from the client if well-formed) → stored in a contextvar → added to logs, OTel span attributes, Sentry tags, job payloads (`correlation_id`), outbound integration calls (as a header where allowed) and error responses.
- An AI run carries both `request_id` and `ai_run_id`. Approvals executed later carry the original `request_id` as a span link.

## 5. API and database health
- `/healthz` (process up), `/readyz` (DB, Redis, migration head). The public status page is optional (OQ-018).
- DB metrics: connections, slow queries (`pg_stat_statements`), replication lag, storage, vacuum and bloat, pgvector index size.
- Alert on: readiness failing > 2 min, DB CPU > 80% for 10 min, connections > 85% of the pool, storage > 80%.

## 6. AI execution traces
- An OTel span per run, with child spans: retrieval, llm_call (attributes: provider, model, input/output/cached tokens, latency, stop_reason), tool_call (tool_key, effect, status), governance.
- `ai_runs` / `ai_run_steps` give a per-tenant view (redacted). Admin view on S-57. Tenant usage on S-52.
- Metrics: runs/min, failure rate by provider/model, first-token latency, tokens and cost per org per day, citation-stripped count, insufficient-evidence rate.

## 7. Integration monitoring
- Per provider: request count, error rate by status, latency, rate-limit hits, token refresh failures, connections in `needs_reauth`, webhook lag and dedupe counts.
- Alert: error rate > 10% over 15 min for a provider; any webhook signature-failure spike (possible attack); `needs_reauth` > N orgs.

## 8. Background job monitoring
- Queue depth and age per queue, job duration, failures and retries, dead-letter count. Scheduler heartbeat.
- Alert: oldest job > 10 min on the critical queue; dead-letter > 0 for billing/webhook queues; scheduler heartbeat missing for 5 min.

## 9. Metrics, dashboards, alerts, issues and incidents
**Dashboards**: (1) Service overview (RED: rate, errors, duration), (2) Database, (3) AI & cost, (4) Integrations, (5) Jobs, (6) Business (signups, active orgs, MRR proxy from Stripe events).

**Alert severities (PROPOSED)**
| Sev | Example | Route | Response target |
|---|---|---|---|
| SEV1 | Prod down, data exposure suspected, billing webhooks failing | On-call page + channel | 15 min (business hours vs 24×7: OQ-018) |
| SEV2 | AI provider outage, one integration failing for all orgs | Channel | 1 h |
| SEV3 | Elevated errors for one tenant, slow queries | Ticket | Next business day |

**Issue tracking**: Sentry issues and alerts create tickets in the team's tracker (tool OQ-018). Each ticket includes the Sentry link, request IDs, affected orgs (count, not names, in public channels).

**Incident timeline**: `incidents` + `incident_events` (S-57). Every SEV1/SEV2 gets an incident record with timestamps (detected, acknowledged, mitigated, resolved), a commander, actions taken, and a postmortem link within 5 business days.

## 10. Recorded data, access and retention
| Data | Recorded | Who can access | Retention (PROPOSED) |
|---|---|---|---|
| App logs | Metadata fields (§2), no bodies | Engineering on-call | 30 days hot; 90 days archive |
| Sentry events | Stack trace, redacted context | Engineering | 90 days (plan-dependent) |
| Traces | Span metadata, no prompt text | Engineering | 14–30 days, sampled 10–20%; 100% for errors |
| Metrics | Aggregates | Engineering, platform admins | 13 months |
| `ai_runs` | Usage, cost, status | Platform admins (aggregate); tenant admins (own org usage) | 13 months |
| `ai_run_steps` | Redacted step details | Platform admins on incident (audited) | 30 days |
| Audit events | spec 10 §7 | Tenant Owner/Admin; platform admins via an audited path | Plan-based, min 365 days |
| Incidents | Timeline | Platform admins | 3 years |

**Redaction**: a shared scrubber (used by logs, Sentry `before_send` and OTel span processors) removes or masks: `Authorization` headers, cookies, keys matching `*token*|*secret*|*password*|*api_key*`, email/phone patterns, credit-card patterns, and any field on a deny-list (`content`, `prompt`, `completion`, `text`). It is unit-tested (SD-01).

## 11. Safe retries and recovery
- Jobs are idempotent by design (natural keys/upserts, idempotency keys).
- Automatic retries: exponential backoff with jitter, a maximum number of attempts per job type, then dead-letter.
- Manual retry from S-57 by platform admins only. Every retry is audited with the reason. Governed actions can be retried only if they are `failed` (never `pending_approval`/`rejected`), with the same payload hash.
- Tenant-facing retry buttons (e.g. document reprocess, integration sync) are limited by role and rate.

## 12. Backups and recovery
| Asset | Method (PROPOSED) | Frequency | Retention |
|---|---|---|---|
| PostgreSQL | Managed automated backups + PITR (WAL) | Continuous | 7–30 days PITR (OQ-016) |
| PostgreSQL | Logical snapshot (`pg_dump`) to separate storage/account | Daily | 30 daily + 12 monthly |
| Object storage | Versioning + lifecycle; cross-region replication if required | Continuous | 30 days of noncurrent versions |
| Redis | Not a system of record. No backup required (queues are re-creatable from `job_records`) | — | — |
| Config/secrets | Secret manager versioning + infra-as-code in git | On change | — |

**Targets**: RPO ≤ 5 min (PITR) / ≤ 24 h (logical). RTO ≤ 4 h (PROPOSED NFR-09).

**Recovery procedures (runbooks to write in M12)**
1. *Full DB restore*: PITR to a new instance at time T → run verification queries (row counts, latest audit hash chain) → switch `DATABASE_URL` → restart services → post-incident review.
2. *Single-tenant data recovery*: restore to a scratch instance → export the affected org's rows → re-import under change control → audit.
3. *Object recovery*: restore a noncurrent version by key.
4. *Credential compromise*: rotate the affected secret → re-encrypt the token vault if the master key changed → force re-auth for integrations if needed → audit.
5. *Integration provider outage*: feature-flag pause of write tools → queue holds → resume and drain.

**Drill**: quarterly restore test into staging, timed against the RTO and recorded.

## 13. Usage and cost monitoring
- Per org: AI tokens and cost (from `usage_events`), embeddings, storage, seats, content items vs entitlements (S-52).
- Platform: daily AI spend by provider/model, cost per active org, top-spending orgs, anomaly alerts (an org's daily spend > 3× its 7-day average).
- Provider-side budget alerts configured in each AI provider console (client account; OQ-017).

## 14. Monitoring verification tests
| ID | Test | Pass condition |
|---|---|---|
| MON-01 | Trigger a test exception via the admin-only `/admin/debug/raise` (staging) | Appears in Sentry within 1 min with request_id, org_id, release; no PII |
| MON-02 | Trigger the same error 50× with different request IDs | Grouped into 1 Sentry issue |
| MON-03 | Provider error fingerprints | ClickUp 429s across orgs group into one issue |
| MON-04 | Synthetic alert (force readiness fail in staging) | Alert delivered to the channel within 5 min |
| MON-05 | Log redaction scan on a scripted run with planted secrets | 0 matches in logs/Sentry/traces |
| MON-06 | Correlation: one request_id found in FE error, API log, trace and job log | All four linked |
| MON-07 | Non-admin attempts job retry / incident edit | 403 + audit event |
| MON-08 | Admin retries a dead-letter job | Executes once; audited |
| MON-09 | Restore drill | Completed within the RTO; verification queries pass |
| MON-10 | Cost anomaly alert with synthetic usage | Alert fires |
