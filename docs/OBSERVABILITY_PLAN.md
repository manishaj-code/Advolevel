# Observability Plan (summary)

The full design is in `specifications/13-monitoring-backup-recovery.md`.

## Stack (PROPOSED — DEC-010)
- **Errors**: Sentry (Next.js + FastAPI + workers).
- **Traces/metrics**: OpenTelemetry SDKs → OTLP → Grafana Cloud (Tempo, Prometheus/Mimir, Loki), or the client's existing vendor.
- **Logs**: structlog JSON to stdout → log backend.
- **Synthetics/uptime**: one external probe service.
- **AI**: `ai_runs`/`ai_run_steps` tables + OTel GenAI spans; Langfuse optional later.

## Phased rollout
| Phase | Milestone | What lands |
|---|---|---|
| 1 | M0 | Request IDs, JSON logs, Sentry FE/BE, OTel auto-instrumentation, `/healthz` `/readyz`, redaction scrubber with tests |
| 2 | M4–M5 | Job metrics, AI run spans and usage/cost metrics, ingestion metrics |
| 3 | M9 | Integration metrics, webhook metrics, provider error fingerprints |
| 4 | M12 | Dashboards, alert rules + routing, incidents (S-57), cost anomaly alerts, backups + restore drill, runbooks |

## Golden signals and first alerts
| Signal | Alert |
|---|---|
| API 5xx rate | > 2% for 5 min (SEV2), > 10% (SEV1) |
| API p95 latency (non-AI) | > 1 s for 10 min |
| Readiness | Failing > 2 min (SEV1) |
| AI run failure rate | > 10% for 10 min per provider (SEV2) |
| Queue age (critical) | > 10 min |
| Stripe webhook failures | Any dead-letter (SEV1) |
| Webhook signature failures | Spike > 20/min |
| Daily AI spend | > budget threshold or an org > 3× its 7-day average |

## Data handling rules
No prompts, completions, document text, tokens or secrets in logs, traces or Sentry by default. Internal IDs instead of emails. A shared redaction scrubber, verified by SD-01 and MON-05. Retention per spec 13 §10.

## Open dependencies
Hosting/budget (OQ-014), support model and on-call hours (OQ-018), the client's existing tooling (OQ-020).
