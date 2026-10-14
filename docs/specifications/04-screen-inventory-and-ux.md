# 04 — Screen Inventory and UX Specification

| Field | Value |
|---|---|
| Status | **PROVISIONAL**. The client has not confirmed the official ~57-screen list (OQ-002). |
| Date | 2026-10-14 |
| Count | **57 screens**: 5 public website (S-W1…S-W5) + 52 application screens. S-03, S-04, S-19, S-25 and S-50 were merged into other screens (see §L). Error pages (403/404/500) and modals are shared and not counted. |

> SOW §2 says an **existing screen inventory** already exists and covers the public website, onboarding, command center, executive offices, boardrooms, knowledge, cases/work, approvals, Content Factory, billing and administration. That inventory has not been provided to us (OQ-002). This list is our proposal and **must be reconciled with the client's inventory before contract signature** (SOW §2, §7). Changes must be recorded in `DECISION_LOG.md`.

## 0. Standard states (apply to every screen unless overridden)
- **Loading**: skeleton matching the layout. No spinner-only full pages. Show a progress label if the wait is longer than 3 s.
- **Empty**: an illustration-free, text-led empty state with one primary CTA (when the role permits it).
- **Error**: inline error panel with the message, retry button and correlation ID ("Reference: abc123") for support. The rest of the page keeps working when possible.
- **Permission**: if the user lacks access, a 403 panel explains the role needed and who the admins are. Restricted actions are hidden, or disabled with a tooltip.
- **Approval** (SOW §2): wherever an action is governed, show the "awaiting approval" state: who must approve, when it expires, a link to the approval, and the read-only payload. After a decision, show approved/executed, rejected (with comment), expired or execution failed (with a retry or contact option).
- **Entitlement**: a feature not in the plan shows an upgrade panel (Owner/Admin) or a "contact your admin" panel (others).
- **Responsive**: desktop ≥1280 (sidebar + content + optional context panel); tablet 768–1279 (collapsible sidebar, the context panel becomes a drawer); mobile 360–767 (bottom/top nav, single column, tables become cards).
- **Standard acceptance**: all states are implemented; keyboard navigable; WCAG 2.2 AA contrast; the API error shape is handled; no cross-tenant data is visible.

Role abbreviations: PA = Platform Admin, O = Owner, A = Admin, M = Member, V = Viewer.

---

## W. Public website (SOW §2)

**S-W1 Home / Landing**: Purpose: explain the product and convert visitors. Roles: public. Components: hero, value propositions, executive team showcase, how-it-works, integrations strip, testimonials (client-supplied only), CTA. Data: CMS or static content (OQ-037). AC: Lighthouse performance ≥ 90 and SEO ≥ 90 on mobile; Concept B styling.

**S-W2 Product / Features**: offices, boardrooms, Org DNA, governance, Content Factory, integrations. AC: as S-W1.

**S-W3 Pricing**: plan cards from `GET /billing/plans` (public), monthly/annual toggle, FAQ, CTA → sign-up with the selected plan. AC: prices match Stripe.

**S-W4 Contact / Book a Demo**: form (rate-limited, spam protection) → email to sales or a GHL contact (if chosen; OQ-008). AC: submission confirmed; no PII in logs.

**S-W5 Legal (Terms, Privacy, Cookies)**: content supplied by the client. A cookie consent banner if required (OQ-015).

## A. Authentication and onboarding

**S-01 Sign In**: Purpose: authenticate. Roles: public. Components: auth provider widget (email/password, SSO), forgot link. Data: none. Actions: sign in. API: auth provider; `GET /me`. Notes: if the user has several orgs → org picker. AC: wrong password gives a generic error; MFA prompt if enabled.

**S-02 Sign Up**: Purpose: register. Roles: public. Components: registration form, terms checkbox. Actions: create account. API: auth provider. AC: no account enumeration; password policy enforced.

*S-03 Email Verification: merged into S-02 as a state of the sign-up flow (an expired link offers resend).*

*S-04 Forgot / Reset Password: merged into S-01 as a state of the sign-in flow (same response whether or not the email exists).*

**S-05 Accept Invitation**: Purpose: join an org. Data: org name, inviter, role. Actions: accept/decline. API: `GET/POST /invitations/{token}`. States: invalid, expired, wrong-account. AC: WF-03 tests.

**S-06 Onboarding — Organization Profile**: Roles: new user. Components: stepper, form (name, industry, size, website, timezone). API: `POST /orgs`. Followed by the step "Build your executive team" (S-15 create mode, multi-select of the five standard templates + "Add custom"). AC: the org is created with exactly the executives the customer selected, within the plan limit.

**S-07 Onboarding — Plan Selection**: Roles: O. Components: plan cards, monthly/annual toggle, Checkout redirect. API: `GET /billing/plans`, `POST /billing/checkout-session`. AC: returning from Checkout shows "activating…" until the webhook confirms.

**S-08 Onboarding — Org DNA Quick Start**: Roles: O/A. Components: 3–5 key DNA questions, optional document upload, skip. API: `PUT /dna/sections/*`, `POST /documents`. AC: can be skipped; progress is saved.

## B. Core

**S-09 Executive Dashboard (Home)**: Purpose: daily command centre. Roles: O/A/M/V. Components: executive team strip (one card per enabled executive, horizontally scrollable; "Add executive" card for O/A when under the limit), my tasks, pending approvals (approvers), recent decisions, active cases, recent boardrooms, DNA completeness, usage meter (O/A). API: `GET /dashboard`. Empty: guided checklist. AC: loads in < 1.5 s p95; widgets fail independently.

**S-10 Global Search**: Purpose: find anything. Components: command palette (Ctrl/Cmd-K), grouped results (conversations, cases, tasks, decisions, documents, content). API: `GET /search?q=`. AC: results are permission-filtered; keyboard-only operable.

**S-11 Notifications Center**: Components: list, filters, mark read, preferences link. API: `GET /notifications`, `PATCH /notifications/{id}`. AC: real-time badge update (SSE or polling).

## C. Executives and offices

**S-12 Executive Directory (My Executive Team)**: Purpose: see and manage the org's executive team. Components: a grid of executive cards (avatar, role, template or "Custom" badge, focus, status, last activity), a usage indicator "N of max executives" (or "Unlimited"), an "Add executive" button, filters (enabled/disabled), search. Actions: open office; configure, enable/disable, delete (O/A/configurator). API: `GET /executives`, `GET /entitlements`. Empty: "Build your executive team" with the five standard templates. AC: disabled executives are shown greyed for admins and hidden for members; "Add" is disabled with an upgrade prompt at the limit; the grid stays usable with 50+ executives (pagination/virtualisation).

**S-13 Executive Office**: Purpose: persistent 1:1 workspace. Components: conversation thread (streaming), composer with attachments, case selector, citations panel, proposed-action cards (task/decision/approval), office sidebar (pinned notes, recent conversations, linked cases). Actions: send, stop generation, regenerate, attach doc, confirm proposal, share conversation. API: `POST /conversations`, `POST /conversations/{id}/messages`, SSE `/runs/{id}/stream`. States: streaming, tool-awaiting-approval, credit-exhausted, provider-error. Responsive: on mobile the citations open in a sheet. AC: WF-06 tests; the stop button cancels the run within 2 s.

**S-14 Conversation History**: Components: list by executive/date/case, search, filters, delete. API: `GET /conversations`. AC: only own + shared conversations are listed.

**S-15 Executive Create / Profile & Configuration**: Roles: O/A/configurator. Modes: **create** (step 1: choose a standard template gallery card or "Start from scratch"; step 2: configure; step 3: preview and test; step 4: save) and **edit**. Components: role title, mandate/responsibilities, display name, avatar picker, tone options, focus areas, custom instructions, model tier (if allowed), a read-only "Platform safety rules" panel, version history with restore, a test-chat preview panel, danger zone (disable/delete). API: `GET /executive-templates`, `POST /executives`, `GET/PUT /executives/{id}/config`, `POST /executives/{id}/enable|disable`, `DELETE /executives/{id}`. States: limit reached (upgrade panel), custom not allowed on plan. AC: WF-07 tests; platform safety rules immutable through the UI and the API.

**S-16 Executive Tool Permissions**: Components: tool list grouped by integration, toggle, effective policy indicator (Allow/Approval/Deny). API: `GET/PUT /executives/{id}/tools`. AC: a tool cannot be enabled beyond the org policy.

**S-17 Executive Knowledge Scope**: Components: collection/folder selector, include/exclude, preview of in-scope doc count. API: `PUT /executives/{id}/knowledge-scope`. AC: retrieval honours the scope.

## D. Boardrooms

**S-18 Boardroom List & History**: Components: sessions table (topic, executives, status, date, owner), **full-text search across session topics, transcripts and summaries**, filters (executive, case, date). The create session panel (formerly S-19) opens as a drawer. API: `GET /boardrooms?q=`. AC: only sessions the user participates in (or all, for Admins); search results are permission-filtered.

*S-19 Create Boardroom Session: merged into S-18 as a drawer.* Components: topic/agenda, executive multi-select (searchable, from the org's enabled team; 2 to `boardroom.max_executives`), case link, documents, human invitees, rounds setting. API: `POST /boardrooms`. AC: entitlement `boardroom.max_executives` enforced.

**S-20 Boardroom Session (live)**: Components: participant rail, threaded turns with executive identity colours, "now speaking" indicator, interject composer, pause/resume/close controls, live notes. API: `POST /boardrooms/{id}/start|interject|close`, SSE stream. AC: WF-08 tests; reconnect resumes the stream.

**S-21 Boardroom Summary / Minutes**: Components: synthesis, agreements/disagreements, proposed decisions and tasks with confirm/reject, transcript, export (PDF/Markdown). API: `GET /boardrooms/{id}/summary`, `POST /proposals/{id}/confirm`. AC: the confirmed proposals link back to the session.

## E. Organizational DNA and knowledge

**S-22 Org DNA Overview**: Components: section cards with completeness, last edited, "draft with executive". API: `GET /dna`. AC: completeness is calculated server-side.

**S-23 Org DNA Section Editor**: Components: structured fields + rich text, AI-draft suggestion diff, version history, restore. API: `GET/PUT /dna/sections/{key}`, `GET /dna/sections/{key}/versions`. AC: optimistic locking.

**S-24 Knowledge Library**: Components: documents table (name, source, collection, status, size, updated), collections, filters, bulk actions, and the upload panel (formerly S-25): drag-and-drop, type/size validation, collection selector, progress per file, "Import from Drive/Dropbox". API: `GET /documents`, `POST /documents/upload-url`, `POST /documents`. AC: status updates live; rejects unsupported types client- and server-side.

*S-25 Document Upload: merged into S-24 as an upload panel.*

**S-26 Document Detail**: Components: metadata, processing log, chunk preview, "used in" citations, reprocess, delete. API: `GET /documents/{id}`. AC: delete asks for confirmation and purges the embeddings.

**S-27 Knowledge Source Connections**: Components: linked Drive/Dropbox folders, sync schedule, last sync, errors. API: `GET/POST /knowledge-sources`. AC: removing a source optionally removes its documents.

## F. Work management

**S-28 Cases List**: table/kanban by status, filters, create. API `GET /cases`.

**S-29 Case Detail**: Components: header (status, priority, owner, close/reopen), overview, **case memory panel** (AI-maintained summary of key facts, editable by the owner), linked conversations, boardrooms, decisions, **approvals**, tasks, documents, activity timeline, "ask executive about this case". API: `GET /cases/{id}` + sub-resources. AC: executive chats launched here carry the case context.

**S-30 Projects List**: table with progress bars, ClickUp sync badge. API `GET /projects`.

**S-31 Project Detail**: Components: milestones, task list/board, members, linked case, ClickUp link. API `GET /projects/{id}`.

**S-32 Tasks**: Components: list/board/calendar views, filters (mine, executive-owned, overdue), quick-add. API `GET /tasks`. AC: drag between statuses obeys the allowed transitions.

**S-33 Task Detail**: Components: fields, owner (human or executive), checklist, comments, executive follow-through log, external link. API `GET/PATCH /tasks/{id}`.

**S-34 Decisions Log**: Components: table (statement, status, decided by, date, source), filters. API `GET /decisions`.

**S-35 Decision Detail**: Components: statement, rationale, alternatives, contributors, source link, spawned tasks, supersession chain. Actions: accept/reject (human only). API `GET/PATCH /decisions/{id}`.

## G. Governance

**S-36 Approvals Inbox**: Roles: approvers, O/A. Components: pending/decided tabs, urgency, expiry countdown. API `GET /approvals`. AC: shows only requests the user is eligible to decide.

**S-37 Approval Detail**: Components: action summary in plain language, exact payload (diff view), requesting executive and user, policy that triggered it, context link, approve/reject with comment. API `GET /approvals/{id}`, `POST /approvals/{id}/decision`. AC: the payload hash is displayed; self-approval is blocked per policy.

**S-38 Governance Policies**: Components: policy list by tool/integration/action class, effect, conditions, approvers. API `GET /policies`.

**S-39 Policy Editor**: Components: rule builder (subject: executive/tool/action; conditions: amount, recipient domain, object type; effect: Allow/Deny/Require Approval; approvers). Simulation ("what would happen if…"). API `PUT /policies/{id}`, `POST /policies/simulate`. AC: validation prevents an unreachable or empty approver list.

**S-40 Audit Log**: Roles: O/A. Components: immutable event table, filters (actor, type, date), export CSV. API `GET /audit-events`. AC: entries are read-only; export is itself audited.

## H. Content Factory

**S-41 Content Factory Dashboard**: pipeline counts by status, recent items, usage vs quota. API `GET /content/summary`.

**S-42 Content Intake & Brief**: Components: media/document intake (upload audio/video/documents or import from Drive/Dropbox), transcription status and transcript viewer (read-only, timestamped), transformation type (e.g. transcript → blog, article → social posts), brief fields (type, channel, goal, audience, key messages), executive, reference docs. API `POST /content/assets`, `POST /content`. States: transcribing, transcription failed. AC: WF-14 AT-14-4.

**S-43 Content Editor & Review**: Components: rich editor, AI revise actions, comments, version compare, brand-voice checklist, submit for approval. API `GET/PATCH /content/{id}`, `POST /content/{id}/submit`.

**S-44 Content Calendar / Publishing Queue**: Components: calendar + list, status, destination, schedule, retry failed. API `GET /content?view=calendar`, `POST /content/{id}/schedule`. Destinations: OQ-012.

## I. Integrations

**S-45 Integrations Hub**: cards for ClickUp, GoHighLevel, Dropbox, Google Drive, Stripe (status only); connect/disconnect. API `GET /integrations`.

**S-46 Integration Detail & Settings**: Components: connection status, account identity, granted scopes, mapping (e.g. ClickUp space/list ↔ projects), enabled operations, reconnect. API `GET/PUT /integrations/{provider}`.

**S-47 Integration Activity Log**: Components: operations, webhooks received, failures, retry (A). API `GET /integrations/{provider}/events`.

## J. Settings and account

**S-48 Organization Settings**: name, logo, timezone, **data retention & deletion controls** (SOW §3: retention periods for conversations, documents and content within platform bounds; bulk delete; org data export), danger zone (delete org, Owner only). All changes are audited.

**S-49 Team, Roles & Permissions**: members table, roles, capabilities, pending invites, resend/revoke, and a "Roles & permissions" tab (formerly S-50) with the role matrix and capability assignment. API `/members`, `/invitations`. Custom roles are not in V1 (ASSUMED).

*S-50 Roles & Permissions: merged into S-49 as a tab.*

**S-51 Billing & Subscription**: current plan, renewal, payment status, invoices (from Stripe), "Manage billing" → Customer Portal, change plan. API `GET /billing/subscription`, `POST /billing/portal-session`.

**S-52 Usage & Limits**: meters for seats, AI credits, storage, documents, content items; per-executive AI usage breakdown. API `GET /usage`.

**S-53 User Profile & Security**: name, avatar, MFA, sessions, notification preferences, personal API tokens (OUT OF SCOPE V1, ASSUMED).

## K. Platform administration (PA only)

**S-54 Tenants List**: orgs, plan, status, seats, usage, created, health flags. API `GET /admin/orgs`.

**S-55 Tenant Detail**: subscription, entitlement overrides, usage, integration health, suspend/reactivate (audited). Tenant content is not visible by default (BR-PA-02).

**S-56 Plans & Entitlements**: plan definitions mapped to Stripe prices, entitlement values (including `executives.max` with an "Unlimited" option and `executives.custom_allowed`), feature flags, and **management of the standard executive templates** (create/edit/version/retire). API `/admin/plans`, `/admin/executive-templates`.

**S-57 System Health & Incidents**: service health, queue depth, AI provider status, error rates, open incidents with timeline, authorized job retries. API `/admin/health`, `/admin/incidents`, `/admin/jobs`.

---

## L. Count reconciliation
| Group | Screens | Count |
|---|---|---|
| Public website | S-W1…S-W5 | 5 |
| Auth & onboarding | S-01, S-02, S-05, S-06, S-07, S-08 | 6 |
| Command center (core) | S-09, S-10, S-11 | 3 |
| Executive offices | S-12…S-17 | 6 |
| Boardrooms | S-18, S-20, S-21 | 3 |
| Knowledge | S-22, S-23, S-24, S-26, S-27 | 5 |
| Cases/work | S-28…S-35 | 8 |
| Approvals & governance | S-36…S-40 | 5 |
| Content Factory | S-41…S-44 | 4 |
| Integrations | S-45…S-47 | 3 |
| Settings & billing | S-48, S-49, S-51, S-52, S-53 | 5 |
| Platform administration | S-54…S-57 | 4 |
| **Total** | | **57** |

## Navigation (PROPOSED)
Primary sidebar: Home · Executives · Boardroom · Work (Cases, Projects, Tasks, Decisions) · Knowledge (Org DNA, Library) · Content Factory · Approvals (with badge) · Integrations · Settings. Platform admins get a separate "Admin" area with a distinct accent colour, so they never confuse it with a tenant view.
