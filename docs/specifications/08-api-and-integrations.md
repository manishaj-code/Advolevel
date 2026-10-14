# 08 — API and Integration Specification

| Field | Value |
|---|---|
| Status | DRAFT v0.1. Endpoints are PROPOSED. Integration operations are PROPOSED until the client confirms them (OQ-007…OQ-012). |
| Date | 2026-10-14 |
| Note | Third-party API details reflect our general knowledge of each provider. **Verify every scope, endpoint and rate limit against the provider's current documentation in the integration milestone** (RSK-010). |

## 1. API conventions
- Base path `/api/v1`. JSON. OpenAPI 3.1 generated from FastAPI, and the frontend client is generated from it.
- **Auth**: `Authorization: Bearer <access JWT from the managed auth provider>`. Tenant routes also require `X-Org-Id`. The server checks the membership on every request.
- **Correlation**: the client may send `X-Request-Id`. The server always returns one, and it appears in logs, traces and error bodies.
- **Idempotency**: all mutating POSTs accept an `Idempotency-Key` header. The response is stored for 24 h per (org, user, key). It is required for: billing actions, approval decisions, action execution, content publish.
- **Pagination**: cursor-based, `?limit=50&cursor=...` → `{ "items": [...], "next_cursor": "..." }`.
- **Validation**: Pydantic models with strict types, max lengths on every string, and enums enforced.
- **Rate limits**: per user and per org (PROPOSED: 600 req/min/user general; 30 AI messages/min/user). Over the limit → 429 with `Retry-After`.
- **Error format** (RFC 9457 problem+json):
```json
{
  "type": "https://docs.advolevel.app/errors/entitlement_exceeded",
  "title": "Plan limit reached",
  "status": 402,
  "code": "entitlement_exceeded",
  "detail": "Your plan allows 5 seats.",
  "request_id": "01J…",
  "errors": [{"field": "email", "message": "…"}]
}
```
| HTTP | code examples |
|---|---|
| 400 | `validation_error` |
| 401 | `unauthenticated` |
| 403 | `forbidden`, `org_membership_required`, `policy_denied` |
| 404 | `not_found` (also used for resources in other tenants, so their existence is not leaked) |
| 409 | `conflict`, `version_conflict`, `idempotency_conflict` |
| 402 | `entitlement_exceeded`, `subscription_inactive`, `ai_credits_exhausted` |
| 422 | `unprocessable` (for example, an unsupported file type) |
| 429 | `rate_limited` |
| 5xx | `internal_error`, `provider_unavailable` |

## 2. Endpoint catalogue (PROPOSED)

### Identity and org
| Method | Path | Purpose | Permission |
|---|---|---|---|
| GET | `/me` | Current user + memberships | auth |
| POST | `/orgs` | Create org (WF-02) | auth |
| GET/PATCH | `/orgs/{org_id}` | Read/update org | member / admin |
| DELETE | `/orgs/{org_id}` | Soft-delete org | owner |
| POST | `/orgs/{org_id}/transfer-ownership` | | owner |
| GET | `/members` | List members | member |
| PATCH/DELETE | `/members/{id}` | Change role/capabilities, remove | admin |
| POST/GET | `/invitations` | Invite / list | admin |
| DELETE | `/invitations/{id}` | Revoke | admin |
| GET | `/invitations/by-token/{token}` | Preview (public, rate-limited) | public |
| POST | `/invitations/by-token/{token}/accept` | Accept | auth |

### Executives and conversations
| Method | Path | Purpose |
|---|---|---|
| GET | `/executive-templates` | List the standard templates available to create from |
| GET | `/executives` | List the org's executives (`?status=enabled|disabled`, paginated) |
| POST | `/executives` | Create from `{ "template_id": "…" }` or custom `{ "template_id": null, "role_title": "…", "mandate": "…", … }`. Accepts a batch for onboarding. 402 `entitlement_exceeded` above `executives.max` |
| POST | `/executives/{id}/enable` · `/disable` | Enable checks the limit; disable frees a slot |
| DELETE | `/executives/{id}` | Soft delete; 409 if in an active boardroom or owning open tasks |
| GET/PUT | `/executives/{id}/config` | Persona/role/config (customer-editable fields; platform safety rules are never accepted) |
| GET | `/executives/{id}/config/versions` | Version history; restore by PUT of an old version |
| GET/PUT | `/executives/{id}/tools` | Tool enablement |
| PUT | `/executives/{id}/knowledge-scope` | Collections in scope |
| GET/POST | `/conversations` | List/create |
| GET/PATCH/DELETE | `/conversations/{id}` | |
| POST | `/conversations/{id}/messages` | Send message → `{ message_id, run_id }` |
| GET (SSE) | `/runs/{run_id}/stream` | Event types: `token`, `citation`, `tool_call`, `tool_status`, `proposal`, `approval_required`, `error`, `done` |
| POST | `/runs/{run_id}/cancel` | Stop generation |
| POST | `/proposals/{id}/confirm` · `/reject` | Confirm an AI proposal |

### Boardroom
`GET/POST /boardrooms` · `GET /boardrooms/{id}` · `POST /boardrooms/{id}/start|pause|resume|close` · `POST /boardrooms/{id}/interject` · `GET (SSE) /boardrooms/{id}/stream` · `GET /boardrooms/{id}/summary` · `GET /boardrooms/{id}/export?format=md|pdf`

### Knowledge
`GET /dna` · `GET/PUT /dna/sections/{key}` (with `If-Match` version) · `GET /dna/sections/{key}/versions` · `POST /dna/sections/{key}/draft` (AI draft) · `GET/POST /collections` · `POST /documents/upload-url` → pre-signed PUT · `POST /documents` (register the uploaded object) · `GET /documents` · `GET/DELETE /documents/{id}` · `POST /documents/{id}/reprocess` · `GET/POST/DELETE /knowledge-sources` · `GET /search?q=&types=`

### Work
CRUD: `/cases`, `/projects`, `/tasks`, `/decisions`, `/comments`, `/work-links`. Plus `POST /cases/{id}/close|reopen`, `GET/PUT /cases/{id}/memory` (+ `/versions`), `GET /cases/{id}/timeline`, `POST /decisions/{id}/accept|reject|supersede`, `POST /tasks/{id}/transition`.

### Governance
`GET/POST /policies` · `GET/PUT/DELETE /policies/{id}` · `POST /policies/simulate` · `GET /action-requests` · `GET /approvals?status=pending` · `GET /approvals/{id}` · `POST /approvals/{id}/decision` `{ decision, comment, payload_hash }` (Idempotency-Key required) · `GET /audit-events` · `POST /audit-events/export`

### Integrations
`GET /integrations` · `POST /integrations/{provider}/connect` → OAuth URL (with state + PKCE) · `GET /integrations/{provider}/callback` · `GET/PUT /integrations/{provider}` · `DELETE /integrations/{provider}` · `GET /integrations/{provider}/events` · `POST /integrations/{provider}/test`

### Content
`POST /content/assets/upload-url` · `POST /content/assets` (register; starts transcription when applicable) · `GET /content/assets/{id}` · `GET /content/assets/{id}/transcript` · `POST /content/assets/import` (from Drive/Dropbox) · `GET/POST /content` · `GET/PATCH /content/{id}` · `POST /content/{id}/transform` `{ "source_asset_id", "transformation" }` · `POST /content/{id}/revise` (AI) · `POST /content/{id}/submit` · `POST /content/{id}/schedule` · `POST /content/{id}/publish` · `GET /content/{id}/versions` · `GET /content/summary`

### Billing and usage
`GET /billing/plans` (also public, for the pricing page S-W3) · `GET /billing/subscription` · `POST /billing/checkout-session` · `POST /billing/portal-session` · `GET /usage` · `GET /entitlements`

### Notifications
`GET /notifications` · `PATCH /notifications/{id}` · `POST /notifications/read-all` · `GET (SSE) /notifications/stream` · `GET/PUT /notification-preferences`

### Webhooks (public, signature-verified)
`POST /webhooks/stripe` · `POST /webhooks/auth` · `POST /webhooks/clickup` · `POST /webhooks/ghl` · `POST /webhooks/dropbox` (+ GET challenge) · `POST /webhooks/gdrive` (push notification channel)

### Platform admin (`/admin/*`, platform roles only)
`GET /admin/orgs` · `GET/PATCH /admin/orgs/{id}` (suspend, overrides) · `GET/PUT /admin/plans` · `GET/POST/PUT /admin/executive-templates` · `GET /admin/health` · `GET/POST /admin/incidents` · `POST /admin/incidents/{id}/events` · `GET /admin/jobs?status=failed` · `POST /admin/jobs/{id}/retry`

### Example contract: send message
```http
POST /api/v1/conversations/{id}/messages
Idempotency-Key: 7d1f…
{ "content": "Draft a Q4 pricing plan", "attachments": ["doc_…"], "case_id": "case_…" }
→ 202 { "message_id": "msg_…", "run_id": "run_…", "stream_url": "/api/v1/runs/run_…/stream" }
```

## 3. Webhook handling (all providers)
1. Verify the signature or token **before** parsing the body (Stripe: `Stripe-Signature` with the endpoint secret and timestamp tolerance; Dropbox: `X-Dropbox-Signature` HMAC; GHL: the signature header per marketplace docs; ClickUp: `X-Signature` HMAC; Google: channel token check).
2. Insert into `webhook_events` with UNIQUE(provider, event_id). If it is a duplicate, return 200 and stop.
3. Enqueue processing and return 2xx quickly (< 2 s).
4. The worker processes it with retries. Failures are recorded and alerted (spec 13).

## 4. Integration operations matrix

**All operations below are PROPOSED. The client must confirm the exact set (OQ-007 … OQ-012).** "Gov" = default governance effect (BR-G-02): reads default to Allow, writes default to Require Approval.

### 4.1 ClickUp (OAuth 2.0)
| Op | Dir | Use | Gov | Trigger |
|---|---|---|---|---|
| List workspaces/spaces/folders/lists | Read | Mapping setup | Allow | Settings |
| Read tasks in a mapped list | Read | Context for executives; sync status | Allow | Executive tool / scheduled sync |
| Create task | Write | Push an accepted AdvoLevel task | Require Approval | Executive tool / user action |
| Update task (status, assignee, due) | Write | Follow-through | Require Approval | Executive tool |
| Add comment | Write | Progress notes | Require Approval | Executive tool |
| Webhook: taskUpdated / taskStatusUpdated | Inbound | Two-way status sync | — | Webhook |
- Credentials: an OAuth app owned by ? (OQ-017). Tokens are encrypted.
- Retries: 3× with exponential backoff on 429/5xx, honouring rate-limit headers.
- Acceptance: create a task in a sandbox list from an approved proposal. The status change in ClickUp reflects back within 1 min.
- Questions: Is the sync two-way or one-way? Which object is master? Map to projects/lists how? (OQ-007)

### 4.2 GoHighLevel (OAuth 2.0 marketplace app, or Private Integration token)
| Op | Dir | Use | Gov |
|---|---|---|---|
| Search/read contacts | Read | Customer context | Allow (PII. See spec 10 §6) |
| Create/update contact | Write | CRM hygiene | Require Approval |
| Read pipelines & opportunities | Read | Sales executive context | Allow |
| Create/update opportunity (stage, value) | Write | Pipeline management | Require Approval |
| Add note / task to contact | Write | Follow-up | Require Approval |
| Send SMS/email via conversations | Write (external comms) | Outreach | **Require Approval (cannot be relaxed to Allow — PROPOSED)** |
| **Add contact to / remove contact from a workflow** | Write (triggers automations, which may send comms) | SOW §4, "workflow operations" | **Require Approval** (treated as `external_comm`) |
| List workflows | Read | Choose a workflow in the tool UI | Allow |
| Add/remove contact tags (often used to trigger workflows) | Write | Workflow triggering | Require Approval |
| Read calendars/appointments | Read | Scheduling context | Allow |
| Webhooks: contact/opportunity events | Inbound | Keep context fresh | — |
- Questions: Agency-level or sub-account (location) install? Which modules? Is outbound messaging in scope at all? Marketplace app approval timeline? (OQ-008)

### 4.3 Dropbox (OAuth 2.0 with PKCE + offline refresh tokens)
| Op | Dir | Use | Gov |
|---|---|---|---|
| List folder / metadata | Read | Choose knowledge sources | Allow |
| Download file | Read | Ingestion | Allow |
| Upload file (e.g. content exports) | Write | **Only if Dropbox is the agreed Content Factory export destination.** SOW §4 lists Dropbox for access/import only | Require Approval |
| Webhook (list_folder changes) | Inbound | Incremental sync | — |
- Scopes (PROPOSED minimum): `files.metadata.read`, `files.content.read`; `files.content.write` only if uploads are confirmed. App folder vs full Dropbox access is OQ-009.

### 4.4 Google Drive (OAuth 2.0)
| Op | Dir | Use | Gov |
|---|---|---|---|
| Pick files/folders (Google Picker) | Read | Choose sources | Allow |
| Download/export file (Docs → text/PDF) | Read | Ingestion | Allow |
| Watch changes | Inbound | Incremental sync | — |
| Create/upload file | Write | **Only if Drive is the agreed Content Factory export destination.** SOW §4 lists Drive for access/import only; `drive.file` covers files the app creates | Require Approval |
- **Scope risk**: `drive.file` (per-file access via the Picker) avoids restricted-scope verification. `drive.readonly`/`drive` are **restricted scopes** that require Google OAuth verification and an annual third-party security assessment (time and cost). PROPOSED: start with `drive.file` + Picker (DEC-013, RSK-008). Folder-level auto-sync may need broader scopes: OQ-010.

### 4.5 Stripe
| Op | Dir | Use |
|---|---|---|
| Create customer | Write (system) | On org creation |
| Create Checkout session | Write (user-initiated) | Subscribe / change plan |
| Create Customer Portal session | Write (user-initiated) | Self-service billing |
| Webhooks: `checkout.session.completed`, `customer.subscription.created/updated/deleted`, `invoice.paid`, `invoice.payment_failed`, `customer.subscription.trial_will_end` | Inbound | Subscription state → entitlements |
| Usage reporting (if metered billing is chosen) | Write (system) | Overage (OQ-011) |
- Stripe actions are not executive tools. Executives never initiate billing changes (PROPOSED).
- Acceptance: the full test-mode lifecycle (spec 11 §6).

### 4.6 AI providers
| Op | Use | Notes |
|---|---|---|
| Chat/messages (streaming, tool use) | Executive reasoning, boardroom, synthesis, content | Default: Anthropic Claude (model tier configurable: e.g. `claude-sonnet-5-5` default, `claude-opus-5-5` premium, `claude-haiku-5-5` for routing/summaries). The final selection depends on budget (OQ-013) |
| Embeddings | RAG | A dedicated embeddings provider (e.g. Voyage AI or OpenAI embeddings). Final choice OQ-013 |
| Moderation / safety | Content screening | Optional |
| **Speech-to-text (transcription)** | Content Factory media intake (SOW §4) | A third-party STT API (e.g. OpenAI transcription, Deepgram or AssemblyAI; choice OQ-013). Async job; long files are chunked; speaker labels if the provider supports them. Usage metered as `transcription_seconds` |
- Credentials: platform-owned keys (default) or customer BYO keys (OQ-013).
- Retries: 2× on 429/529/5xx with jitter. Fallback model configurable. A per-run timeout is enforced.

### 4.7 Content Factory publishing destination
**Unknown. NEEDS CLARIFICATION (OQ-012).** Candidates to ask about: GoHighLevel social planner/blog, WordPress, LinkedIn, Meta, email newsletters, or export-only (Drive/Dropbox/download). V1 fallback, PROPOSED: **export to Google Drive / Dropbox / download**, which uses already-confirmed integrations. Every publish action is governed (Require Approval).

## 5. Credential handling (all integrations)
- OAuth `state` is bound to the user session, org and nonce. PKCE is used where supported.
- Tokens are stored in `integration_connections.encrypted_credentials` (envelope encryption, `key_version` for rotation). They are never logged and never returned to the frontend.
- The refresh is done by the worker before expiry. On failure → `needs_reauth`, notify admins, and audit.
- Disconnect → provider revoke endpoint (where it exists) → delete credentials → audit.
