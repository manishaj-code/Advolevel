# 11 — Testing and Acceptance

| Field | Value |
|---|---|
| Status | DRAFT v0.1 — PROPOSED |
| Date | 2026-10-14 |
| Related | `docs/TEST_STRATEGY.md` (summary), `14-development-roadmap.md` (milestones M0–M14) |

## 1. Test layers and tooling (PROPOSED)
| Layer | Scope | Tooling |
|---|---|---|
| Unit (BE) | Services, policy engine, chunker, entitlement logic | pytest, hypothesis (property tests for the policy engine) |
| Unit (FE) | Components, hooks, formatters | Vitest + Testing Library |
| Integration (BE) | Repositories against real Postgres+pgvector, RLS, queue jobs | pytest + Testcontainers (Postgres, Redis) |
| API / contract | Endpoints, authz, error shapes, OpenAPI conformance | pytest + httpx; Schemathesis (fuzz from OpenAPI) |
| Provider adapters | ClickUp/GHL/Dropbox/Drive/Stripe adapters | Recorded fixtures (VCR-style) + sandbox smoke tests (nightly, manual secrets) |
| Frontend integration | Pages with a mocked API | Vitest + MSW |
| End-to-end | Critical journeys in a deployed staging-like env | Playwright |
| Accessibility | Core screens | axe-core in Playwright + manual screen-reader pass per milestone |
| Security | SAST, deps, secrets, DAST baseline | Semgrep/CodeQL, pip-audit/npm audit, gitleaks, OWASP ZAP baseline |
| AI quality | Grounding, citations, refusal, tool choice | Golden sets + an LLM-judge with human-reviewed rubric; cost-capped |
| Performance | API latency, ingestion throughput, vector search | k6 / Locust |
| Monitoring | Error capture, alerts | Synthetic tests in staging (spec 13 §12) |

**Coverage targets (PROPOSED)**: backend ≥ 80% lines on `governance`, `identity`, `billing`, `knowledge.retrieval` and ≥ 70% overall; frontend ≥ 60% on `components/features`. Coverage is a guide, not the gate. The named suites below are the gates.

## 2. CI gates
- On every PR: lint, type-check (mypy/pyright, tsc), unit, integration, API, tenant-isolation suite, approval-bypass suite (once M8 exists), secret scan, dependency audit.
- Nightly: E2E on staging, AI eval (cost-capped), sandbox integration smoke, ZAP baseline.
- Release: all of the above green + manual exploratory checklist + migration dry-run.

## 3. Tenant-isolation suite (negative tests — MUST pass 100%)
Fixtures: Org A (users a1 owner, a2 member), Org B (b1 owner). The same-named entities exist in both.
| ID | Test | Expected |
|---|---|---|
| TI-01 | a1 GETs each resource type of Org B by ID (parametrised over all tenant endpoints) | 404 |
| TI-02 | a1 lists with `X-Org-Id: B` | 403 `org_membership_required` |
| TI-03 | a1 PATCH/DELETE on Org B IDs | 404, no change in DB |
| TI-04 | Repository call with org A context + raw SQL omitting the org filter | RLS returns 0 rows for B |
| TI-05 | RAG query in org A for a phrase that only exists in org B docs | 0 B chunks; "insufficient evidence" |
| TI-06 | Pre-signed URL for a B document requested by a1 | 404 |
| TI-07 | Worker job with a mismatched org payload / entity | Job fails safe, alert, no data written |
| TI-08 | Boardroom/approval/conversation share across orgs | Rejected |
| TI-09 | Search endpoint returns only own-org results | Pass |
| TI-10 | Cache poisoning: same cache key pattern across orgs | Separate values |
| TI-11 | Schema check: every table except the allow-list has `organization_id` + RLS enabled | Automated introspection test |

## 4. Authorization and approval-bypass suite (MUST pass 100%)
| ID | Test | Expected |
|---|---|---|
| AZ-01 | Each endpoint × each role vs the spec 02 matrix (table-driven) | Matrix exactly enforced |
| AZ-02 | Viewer attempts chat/create | 403 |
| AZ-03 | Member attempts executive create/config/delete without the capability | 403 |
| AZ-04 | Create or enable an executive above `executives.max` via a direct API call (UI bypassed), including parallel requests | 402; count never exceeds the limit |
| AZ-05 | A custom executive's `custom_instructions` / `mandate` try to override the platform safety rules or governance ("ignore approvals") | Safety rules still applied; governed actions still require approval |
| AB-01 | Execute a Require-Approval action without an approval | Not executed; status remains pending |
| AB-02 | Approve, then mutate the payload in the DB, then execute | Execution refused (hash mismatch), alert |
| AB-03 | Same approval decision submitted twice / concurrently | One decision; one execution |
| AB-04 | Requester approves own request (policy disallows) | 403 |
| AB-05 | Non-eligible approver approves | 403 |
| AB-06 | Approve an expired request | 409 |
| AB-07 | Model output contains "approved: true" or fake approval IDs | Ignored |
| AB-08 | Prompt-injected document instructs "send SMS to all contacts" | `external_comm` → approval required; not executed |
| AB-09 | Static check: no call sites of adapter write methods outside `execute_action` | Pass |
| AB-10 | Policy relaxed after the request was created | Pending request not auto-executed |
| AB-11 | Deny policy plus an Allow policy matching the same action | Deny |
| AB-12 | Platform admin retries a non-failed / non-approved request | Refused |

## 5. RAG and AI orchestration tests
| ID | Test | Metric / expected |
|---|---|---|
| RAG-01 | Chunker unit tests (headings, tables, overlap, page mapping) | Deterministic snapshots |
| RAG-02 | Ingestion of each supported format (fixtures) | `ready`; chunk count in the expected range |
| RAG-03 | Corrupt / oversized / wrong-type files | `failed` with a reason; no partial chunks |
| RAG-04 | Retrieval recall@10 on the golden set | ≥ 0.85 (PROPOSED) |
| RAG-05 | Citation precision (cited source actually supports the claim) | ≥ 0.90 on the golden set, judged + spot-checked |
| RAG-06 | Insufficient-evidence questions | ≥ 95% correct "not in your documents" behaviour |
| RAG-07 | Deleted document never cited after deletion | 100% |
| RAG-08 | Knowledge scope respected per executive | 100% |
| AI-01 | Provider abstraction contract tests (stream, tool call, usage) per adapter | Pass with recorded fixtures |
| AI-02 | Tool loop max-iteration guard | Run ends gracefully |
| AI-03 | Provider timeout/5xx → retry → fallback → user error | As specified in WF-06 |
| AI-04 | Usage and cost recorded per run | Matches provider usage ±0 tokens |
| AI-05 | Boardroom: N executives produce N×R turns, synthesis references each | Pass |
| AI-06 | Cancel run | Stops within 2 s; partial message saved and marked |
| AI-07 | Proposals never auto-create records | 100% |

## 6. Billing tests (Stripe test mode + stripe-mock/fixtures)
| ID | Test | Expected |
|---|---|---|
| BL-01 | Checkout completed webhook → subscription active → entitlements applied | Pass |
| BL-02 | Duplicate webhook event | Processed once |
| BL-03 | Out-of-order events (`updated` before `created`) | Final state correct (fetch-latest strategy) |
| BL-04 | Invalid signature | 400; nothing processed; logged |
| BL-05 | Payment failed → grace → read-only | Per BR-S-02 |
| BL-06 | Downgrade below usage | Creation blocked; no deletion |
| BL-07 | Entitlement checks server-side even when the UI is bypassed | 402 |
| BL-08 | Redirect success URL without a webhook | No entitlement change |

## 7. Integration tests (per provider)
Connect/disconnect, token refresh, `needs_reauth` on revoked tokens, rate-limit backoff, webhook signature + dedupe, each confirmed operation in the sandbox, failure → retry → final failure surfaced on S-47.

## 8. Failed-operation and resilience tests
- Job crash mid-ingestion → retried, no duplicate chunks (idempotent upsert by `document_id, seq`).
- Integration write times out but actually succeeded → idempotency key prevents duplication on retry (where the provider supports it). Otherwise there is a reconciliation read before retry.
- DB failover / restart during requests → errors are surfaced with a request ID, no data corruption.

## 9. Sensitive-data leakage tests
| ID | Test |
|---|---|
| SD-01 | Logs and Sentry events from a run containing tokens, emails, API keys → redacted (scan the captured output with patterns) |
| SD-02 | API responses never include `encrypted_credentials`, token values or other users' emails beyond permissions |
| SD-03 | Error responses contain no stack traces in prod mode |
| SD-04 | AI output containing a planted secret string from a document → redaction filter |
| SD-05 | Trace span attributes contain no prompt text in prod (unless the debug flag is on for a specific org with consent) |

## 10. Frontend and E2E journeys (Playwright)
E2E-01 register → onboard → org created. E2E-02 invite → accept. E2E-03 DNA edit → executive reflects it. E2E-04 upload doc → cited answer. E2E-05 boardroom with 3 executives → confirm a task. E2E-06 executive proposes a ClickUp task → approval → executed (sandbox or mocked provider). E2E-07 content brief → approval → export. E2E-08 subscribe (Stripe test) → feature unlocked. E2E-09 permission states for Viewer. E2E-10 mobile viewport smoke of core screens.

## 11. Monitoring tests
See spec 13 §12.

## 12. Milestone acceptance criteria (measurable)
**SOW §7 gate rule:** each criterion is demonstrated on deployed, working software with real AI-provider calls and real sandbox integration accounts. Mockups, recorded demos or simulated AI/integration actions do not count. **Manual testing** (SOW §6): each gate also includes a scripted manual test pass of that milestone's critical flows, with results recorded.

| Milestone | Acceptance criteria |
|---|---|
| M0 Foundation | CI green on an empty app; `docker compose up` gives working health endpoints; Sentry receives a test error from FE and BE; lint/type/test gates enforced |
| M1 Auth & orgs | WF-01/02/03 AT pass; AZ-01 matrix for identity endpoints passes |
| M2 Tenant isolation & audit | TI-01…TI-11 pass for all existing tables; audit hash chain verified by test |
| M3 UI shell & design system | Storybook (or equivalent) with §5 core components; axe: 0 serious/critical violations on the shell; responsive at 360/768/1280 |
| M4 DNA & RAG | RAG-01…RAG-08 pass; ingestion p95 < 2 min for a 20-page PDF |
| M5 Brain & Offices | AI-01…AI-04, AI-06, AI-07 pass; first token p95 < 3 s in staging; AT-07-1…AT-07-7 pass (create from template and from scratch, enable/disable/delete, `executives.max` enforced incl. concurrency and unlimited); standard templates loadable (content pending OQ-003) |
| M6 Boardroom | AI-05 + WF-08 AT pass |
| M7 Work mgmt | WF-09/10/11 AT pass |
| M8 Governance | AB-01…AB-12 pass 100%; policy engine property tests pass |
| M9 Integrations | §7 suite passes for each confirmed provider in the sandbox |
| D1 Design | Editable Figma (foundations, components, 57 screens) and a clickable prototype of the agreed critical flows, transferred to the AdvoLevel workspace; client sign-off |
| M10 Content Factory | WF-14 AT-14-1…AT-14-5 pass (incl. real transcription and a real publish/export to the agreed destination); publish only after approval |
| M11 Billing | BL-01…BL-08 pass |
| M12 Monitoring & admin | Spec 13 §12 tests pass; restore drill completed within the RTO |
| M13 Hardening | No open critical/high vulns; ZAP baseline clean of high; load test meets NFR-03; SD-01…SD-05 pass |
| M14 Release & handover | E2E-01…E2E-10 pass on production-like staging; UAT sign-off; handover pack delivered |
