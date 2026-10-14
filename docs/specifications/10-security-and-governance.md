# 10 — Security and Governance

| Field | Value |
|---|---|
| Status | DRAFT v0.1 — controls PROPOSED |
| Date | 2026-10-14 |
| Compliance | **No compliance certification is claimed or implied.** Controls are aligned to OWASP ASVS L2 and OWASP Top 10 for LLM Applications as design references only. Required certifications are NEEDS CLARIFICATION (OQ-015). |

## 1. Authentication
- A managed auth provider (DEC-006) handles credentials, email verification, MFA (TOTP/passkeys), optional SSO, brute-force protection and session management.
- The API verifies the JWT signature (JWKS, cached with rotation), `iss`, `aud`, `exp` and `nbf`. Leeway ≤ 60 s.
- Short-lived access tokens (≤ 15 min PROPOSED) with refresh handled by the provider SDK.
- MFA can be enforced per org by the Owner (PROPOSED). Platform admins must use MFA.

## 2. Authorization
- Layer 1: route dependency `require_permission("tasks:update")` → role + capability check (spec 02 matrix).
- Layer 2: object-level check (owner/assignee/share/participant).
- Layer 3: tenant scoping. Every repository call takes a `TenantContext`. Postgres RLS (`app.org_id` set per transaction) blocks any missed filter.
- Platform-admin routes use a separate dependency and do not use tenant RLS bypass, except through explicit, audited admin repositories.
- Resources in other tenants return **404**, not 403.

## 3. Tenant isolation controls
| Control | Where |
|---|---|
| `organization_id` NOT NULL on tenant tables | Schema |
| RLS on all tenant tables; the app DB role is not the table owner and has no `BYPASSRLS` | Database |
| `TenantContext` required by repositories (type-enforced) | Code |
| Object-storage keys `org/{org_id}/…`; pre-signed URLs generated only after an authz check; short TTL (≤ 5 min) | Storage |
| Vector search filter + RLS | RAG |
| Cache keys prefixed with org | Redis |
| Job payloads carry `organization_id`; the worker sets the tenant context before any DB access | Workers |
| Automated cross-tenant test suite (spec 11 §3) | CI |

## 4. Secrets management
- No secrets in code, images or logs. `.env` only for local development (git-ignored). `.env.example` contains no values.
- Production secrets live in the hosting platform's secret store or a dedicated secret manager (OQ-014).
- Integration tokens: envelope encryption. The data key is encrypted by a master key from KMS or the secret store. `key_version` supports rotation.
- Rotation runbook for: DB credentials, Stripe keys, webhook secrets, AI keys, the master encryption key.
- Secret scanning in CI (e.g. gitleaks) plus pre-commit.

## 5. Input validation and output encoding
- Pydantic strict models. Max sizes on all inputs, request body limits, and file type validated by magic bytes, not the extension.
- Rich text is sanitized server-side (allow-list) before storage and rendering.
- Markdown from the AI is rendered with a sanitizer (no raw HTML, safe link schemes only).
- Uploaded files: content-type/magic check, size limit, and malware scan (ClamAV or a provider service. PROPOSED; OQ-015).
- SSRF protection for any URL fetch (block private IP ranges, allow-list the integration hosts).

## 6. Data protection and privacy
- TLS 1.2+ everywhere. HSTS. Secure, HttpOnly, SameSite cookies where cookies are used.
- Encryption at rest: provider-managed disk encryption for the DB, Redis and storage, plus app-level encryption for integration credentials.
- PII from integrations (e.g. GHL contacts) is fetched on demand and not bulk-stored unless needed. It is redacted in logs and traces.
- Data processing agreements with the AI providers. No-training/zero-retention settings where offered (OQ-015).
- Data subject requests: export and delete per user and per org (WF-17, retention spec 07 §5).

## 7. Audit logging
Audited events (minimum): sign-in anomalies (from the provider), membership/role changes, invitations, org settings changes, executive config changes, policy changes, every `action_request` and approval decision, integration connect/disconnect/re-auth, document deletion, data exports, billing plan changes, platform-admin actions (incl. entitlement overrides, suspensions, job retries, support access).
- Append-only table. The app DB role has INSERT/SELECT only. Hash chaining (`prev_hash`, `hash`) gives tamper evidence.
- Visible to Owner/Admin (S-40). Exportable, and the export itself is audited.

## 8. Governance engine: Allow / Deny / Require Approval

### 8.1 Evaluation
`evaluate(ctx, tool_key, payload) → {effect, policy_id, approvers, reason}`
1. Collect enabled org policies whose subject matches (executive, tool, action class, integration).
2. Evaluate conditions (e.g. `amount > 500`, `recipient_domain not in allow-list`, `object_type == contact`).
3. **Precedence: Deny > Require Approval > Allow.** Among equal effects, the highest priority policy wins for approver selection.
4. No matching policy → the default: reads Allow; writes, external_comm, publish and financial → Require Approval.
5. **Platform floor rules** (not overridable by orgs, PROPOSED): `external_comm` and `financial` classes can never be Allow without approval; actions on deleted or disconnected integrations are Deny.

### 8.2 Execution path (the only path to side effects)
```
tool call → schema validation → evaluate → action_request (payload snapshot + SHA-256 hash)
   → Allow: execute_action(request_id)
   → Require Approval: status=pending_approval → approval decision → execute_action(request_id)
   → Deny: status=denied
execute_action: lock row (SELECT … FOR UPDATE) → assert status ∈ {approved, allowed}
   → assert stored hash == hash(stored payload) → assert not expired → status=executing
   → call adapter with idempotency_key → status=succeeded|failed → audit
```

### 8.3 Approval-bypass prevention
| Threat | Control |
|---|---|
| Code path that calls an adapter's write methods directly | Adapter write methods require an `ExecutionToken` that only `execute_action` can mint. Import-linter rule plus a unit test that scans call sites |
| Model fabricates "approved" in a tool arg | Approval state lives only in the DB. Tool args are never trusted for status |
| Payload changed after approval | Approval stores `payload_hash_at_decision`. Execution re-hashes and compares |
| Replay or double execution | Status machine + row lock + `idempotency_key` UNIQUE + provider idempotency keys where supported |
| Self-approval | `decided_by != requested_by` unless the policy allows it |
| Non-approver approves | The approver eligibility check is server-side at decision time, not only at creation |
| Cross-tenant approval | RLS + org check on the approval ID |
| Policy downgraded after the request | The request keeps `policy_id` + version. A later relaxation does not auto-approve pending requests |
| Expired approval used | Expiry is checked inside `execute_action` |
| Platform admin forces execution | Not possible. Admins can retry only *failed* executions of already-approved requests, and this is audited |
| Prompt injection causing an action | Governance is independent of the model. High-risk classes always require approval |

### 8.4 Testing the bypass controls
See spec 11 §4: a dedicated "approval-bypass suite". It must pass with 100% success before any integration write operation is enabled in any environment.

## 9. Secure webhooks
Signature verification with a constant-time compare. Timestamp tolerance (Stripe 5 min). Raw-body verification before JSON parsing. Event-ID deduplication. Fast 2xx. No sensitive data in the response. Separate secrets per environment. Endpoint-specific rate limits.

## 10. Application security hygiene
- Dependency scanning (Dependabot/Renovate + `pip-audit`/`npm audit`), SAST (Semgrep or CodeQL), container image scanning.
- Security headers: CSP (strict, nonce-based), X-Content-Type-Options, Referrer-Policy, frame-ancestors none.
- CORS restricted to the app origins.
- Rate limiting and abuse protection on auth-adjacent and AI endpoints.
- A third-party penetration test before production launch is recommended (budget OQ-015).

## 11. LLM-specific risks (OWASP LLM Top 10 reference)
Prompt injection (spec 09 §9), sensitive information disclosure (redaction, tenant isolation), excessive agency (governance), insecure output handling (sanitized rendering), unbounded consumption (credits, rate limits, max tool iterations), supply chain (pinned SDKs).
