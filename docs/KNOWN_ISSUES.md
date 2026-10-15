# Known Issues

Planning- and process-level issues were found on 2026-10-14; code-level issues from M0 (2026-10-15) onward.

| ID | Issue | Impact | Workaround / next step | Status |
|---|---|---|---|---|
| KI-001 | The concise SOW (`d:\POC\AdvoLevel_Concise_Integrated_SOW.pdf`) was reviewed on 2026-10-14 and the specs were updated (`SOW_INCLUSION_MATRIX.md`). The **detailed master SOW, workflows and existing screen inventory** it references are still not available. | Remaining conflicts or omissions are possible | Request them (OQ-001, OQ-002); reconcile in writing before award | Partly resolved |
| KI-002 | `prompt.md` is truncated at line 300 (`docs/RE…`). One or more requested tracking documents are unknown. | Possible missing deliverable(s) | Created `docs/README.md` as an index; obtain the full brief (OQ-027) | Open |
| KI-003 | The local project directory was not a git repository; the remote was empty. | No history, no review, risk of loss | Repo initialised and connected to the remote; `docs/` pushed (`5fb77e6`). M0 code is committed locally only until KI-005 is resolved. Branch protection still to enable | Partly resolved |
| KI-006 | The repo `manishaj-code/Advolevel` is under a personal account. SOW §6 requires the source repository to be AdvoLevel's | Ownership and handover non-compliance | Transfer it to an AdvoLevel GitHub organization (GitHub Settings → Transfer), or create the repo there and push | Open |
| KI-005 | The GitHub repository `manishaj-code/Advolevel` is **public** | Specs and code for a commercial product would be publicly visible | Change visibility to private before pushing M0 (repo Settings → Danger Zone), unless the client decides otherwise | Open |
| KI-004 | No credentials or accounts exist for any service | Blocks environment setup beyond local | Ownership checklist OQ-017 | Open |
| KI-007 | `POST /api/v1/admin/debug/raise` (MON-01) has no authentication; it is only gated by `DEBUG_ENDPOINTS_ENABLED`, which settings forbid in production | Anyone reaching a staging API with the flag on can trigger 500s | Require platform admin once auth exists (`TODO(M1)` in `backend/app/admin/debug.py`); keep the flag off in staging until then | Open (M1) |
| KI-008 | Sentry delivery (MON-01) is wired but unverified for backend and frontend: no Sentry project/DSN exists (KI-004). Frontend source maps are not uploaded (`withSentryConfig` not used yet) | First real error reports may be missing or unreadable | When a DSN exists: set `SENTRY_DSN`/`NEXT_PUBLIC_SENTRY_DSN`, hit the debug endpoint and `/debug/sentry`, confirm events carry `request_id` and no PII; add source-map upload in CI | Open |
| KI-009 | Running the API natively on Windows (`uvicorn` outside Docker) fails DB calls: async psycopg cannot use the Proactor event loop | Windows devs must run the API in compose (tests already switch loops in `conftest.py`) | Use `docker compose up`; containers and CI are Linux | Open (by design) |
