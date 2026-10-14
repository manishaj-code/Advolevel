# 03 — User Journeys and Workflows

| Field | Value |
|---|---|
| Status | DRAFT v0.1 — all workflows PROPOSED unless noted |
| Date | 2026-10-14 |

Each workflow lists: **Actors · Trigger · Prerequisites · Steps · Permissions · Backend operations · Expected result · Failure handling · Acceptance tests (AT)**.
Endpoint names refer to `08-api-and-integrations.md`. Screen IDs (S-xx) refer to `04-screen-inventory-and-ux.md`.

---

## WF-01 Registration
- **Actors**: Prospective user.
- **Trigger**: The user clicks "Sign up" (S-02).
- **Prerequisites**: None.
- **Steps**: 1) Enter name, email, password, or use SSO via the managed auth provider. 2) Verify email (verification state of S-02). 3) Redirect to onboarding.
- **Permissions**: Public.
- **Backend**: The auth provider creates the identity → webhook `user.created` → API upserts `users` (idempotent on `auth_provider_user_id`).
- **Result**: A verified user with no organization lands on S-06.
- **Failures**: Duplicate email → generic message (no account enumeration). Webhook retry is idempotent. Unverified email → access blocked with a resend option (rate-limited).
- **AT**: AT-01-1 new email registers and verifies. AT-01-2 duplicate email does not reveal whether the account exists. AT-01-3 the same `user.created` webhook delivered twice creates one user.

## WF-02 Onboarding (organization creation)
- **Actors**: Newly registered user.
- **Trigger**: First login with no memberships.
- **Prerequisites**: Verified email.
- **Steps**: 1) Organization profile: name, industry, size, website (S-06). 2) Choose a plan or start a trial (S-07; trial existence OQ-030). 3) **Build your executive team**: the five standard templates are shown pre-selected; the customer deselects or adds custom executives within the plan limit (S-15 in create mode, step variant). 4) Org DNA quick start (S-08), which can be skipped. 5) Land on the dashboard (S-09).
- **Permissions**: Authenticated user.
- **Backend**: `POST /orgs` runs in one transaction: create org, membership (Owner), default governance policies, and a free/trial subscription record → Stripe customer created asynchronously. Then `POST /executives` (batch) creates the executives the customer chose.
- **Result**: An org exists with the user as Owner and the executive team the customer chose (0…`executives.max`).
- **Failures**: Stripe customer creation fails → job retry with backoff. The org remains usable on trial. Partial provisioning → transaction rollback.
- **AT**: AT-02-1 the org is created with default policies and exactly the executives selected in step 3. Skipping step 3 is allowed (an empty team with a dashboard prompt to add executives). AT-02-2 a Stripe outage does not block org creation. AT-02-3 a user cannot create a second org beyond the plan/platform limit (OQ-006).

## WF-03 Team invitations
- **Actors**: Owner or Admin (inviter); invitee.
- **Trigger**: Invite from S-49.
- **Prerequisites**: Seats available (`seats.max`).
- **Steps**: 1) Enter email(s) and role. 2) The system emails a signed, single-use link (expires in 7 days). 3) The invitee signs in or registers (S-05) and accepts. 4) The membership becomes active.
- **Permissions**: `members:invite`.
- **Backend**: `POST /orgs/{id}/invitations` → token stored hashed → email job → `POST /invitations/{token}/accept` checks that the email matches (PROPOSED: yes), and that the token is unexpired and unused.
- **Failures**: Seat limit → 402 `entitlement_exceeded`. Expired or used token → clear error with "ask for a new invite". Email bounce → shown on S-49.
- **AT**: AT-03-1 accept creates the membership with the invited role. AT-03-2 the token cannot be reused. AT-03-3 an invite for email A cannot be accepted by user B. AT-03-4 an invite beyond the seat limit is rejected.

## WF-04 Organizational DNA
- **Actors**: Owner, Admin, knowledge_manager.
- **Trigger**: Onboarding step or S-22/S-23.
- **Steps**: 1) Fill the structured sections. **CONFIRMED by SOW §3**: Mission, Goals, Policies, **SOPs**, Brand, Structure. PROPOSED additions: Products/Services, Customers & Markets. SOPs and Policies support both structured entries and attached documents (ingested into RAG and tagged as DNA). 2) Optionally have an executive draft sections from uploaded documents, with the user reviewing the draft. 3) Save. This creates a version.
- **Backend**: `PUT /orgs/{id}/dna/sections/{key}` → new `org_dna_versions` row → cache invalidation of the executive context.
- **Result**: Every subsequent executive run includes the current DNA (summarized to a token budget).
- **Failures**: Concurrent edit → optimistic-lock 409 with a diff prompt.
- **AT**: AT-04-1 an edit appears in the next executive response context (trace check). AT-04-2 version history restores the previous version. AT-04-3 a Member without the capability gets 403.

## WF-05 Document ingestion
- **Actors**: Owner, Admin, knowledge_manager; system (sync).
- **Trigger**: Upload (upload panel on S-24) or a scheduled/linked folder sync (S-27).
- **Prerequisites**: Within `storage.max_gb` and `documents.max_count`. The file type is supported (OQ-005).
- **Steps**: 1) Upload, or select Drive/Dropbox files or folders. 2) The file is stored in object storage under the org prefix. 3) Background job: virus/type check → parse → chunk → embed → index. 4) Status visible on S-24/S-26.
- **Backend**: `POST /documents` (pre-signed upload) → `document.uploaded` job → status transitions `pending → processing → ready | failed`.
- **Result**: Chunks are searchable only within the org and within the configured knowledge scope.
- **Failures**: Unsupported or corrupt file → `failed` with a reason. Embedding provider error → retry ×5 with exponential backoff, then `failed` with a manual retry button. Over quota → rejected before upload.
- **AT**: AT-05-1 a PDF becomes `ready` and answers cite it. AT-05-2 a document from org A is never retrieved for org B. AT-05-3 deleting a document removes its chunks and embeddings, and it is no longer cited. AT-05-4 a duplicate upload (same hash) is detected.

## WF-06 AI conversation (Executive Office)
- **Actors**: Member+; executive.
- **Trigger**: The user sends a message on S-13.
- **Prerequisites**: The executive is enabled, AI credits remain, and the user has chat permission.
- **Steps**: 1) Message saved. 2) Executive Brain run: assemble context (persona + DNA + case context + retrieved chunks + recent history), call the model, stream tokens. 3) Tool calls go through governance. 4) Final message saved with citations, usage and trace ID. 5) Proposed tasks or decisions are shown as confirmable cards.
- **Backend**: `POST /conversations/{id}/messages` → SSE stream `/runs/{run_id}/stream`. `ai_runs`, `ai_run_steps` and `usage_events` are recorded.
- **Failures**: Provider timeout → one automatic fallback-model retry (if configured) → friendly error with "retry". Credit exhaustion → 402 with an upgrade CTA. Tool denied → the executive explains that the action is not permitted.
- **AT**: AT-06-1 the response streams and persists. AT-06-2 citations link to the source chunks. AT-06-3 with no evidence the executive states it is uncertain (golden test). AT-06-4 usage is recorded per run.

## WF-07 Executive team management (create, configure, enable/disable, delete)
- **Actors**: Owner, Admin, executive_configurator.
- **Trigger**: "Add executive" on S-12, or edit on S-15/S-16/S-17.
- **Prerequisites**: To create or enable: enabled-executive count < `executives.max`. To create from scratch: `executives.custom_allowed`.
- **Steps (create)**: 1) Choose a standard template or "Custom". 2) Set the role title, mandate/responsibilities, display name, avatar, tone, focus areas and custom instructions. 3) Choose the knowledge scope. 4) Enable tools (only those permitted by governance). 5) Optional: preview with a test question. 6) Save → the executive is enabled and its Office is available.
- **Steps (configure)**: Edit any customer-editable field (BR-E-02) → save as a new config version (history kept, restorable).
- **Steps (disable / delete)**: Disable → hidden from members, history kept, frees a plan slot. Delete → confirmation (type the name) → soft delete per BR-E-04.
- **Backend**: `POST /executives` (entitlement check inside the transaction, counted with a row lock so concurrent creates cannot exceed the limit) · `PUT /executives/{id}/config` · `POST /executives/{id}/enable|disable` · `DELETE /executives/{id}`. Every change is audited.
- **Failures**: Limit reached → 402 `entitlement_exceeded` with an upgrade CTA. A tool blocked by policy → validation error. Delete blocked by an active boardroom or open tasks → 409 with the list of blockers.
- **AT**: AT-07-1 platform safety rules cannot be changed via the API. AT-07-2 the knowledge scope restricts retrieval (test with out-of-scope docs). AT-07-3 with `executives.max=3`, creating or enabling a 4th returns 402, including two concurrent creates at count 2 (exactly one succeeds). AT-07-4 `executives.max=-1` allows creation without a limit. AT-07-5 a custom executive created from scratch answers in its defined role. AT-07-6 a deleted executive's conversations remain readable but no new messages can be sent. AT-07-7 a disabled executive does not count toward the limit.

## WF-08 Boardroom session
- **Actors**: Session owner, invited members, 2 to `boardroom.max_executives` of the org's enabled executives.
- **Trigger**: "New Boardroom" (create drawer on S-18).
- **Steps**: 1) Set the topic or agenda, select executives (from the org's enabled team), optionally attach a case and documents, and invite members. 2) Start. The moderator (orchestrator) plans the order and each executive contributes, in rounds (configurable 1–3). 3) Humans can interject at any time. 4) The owner closes the session → synthesis: summary, points of agreement and disagreement, proposed decisions, proposed tasks. 5) The owner confirms the proposals → they become records.
- **Backend**: `boardroom_sessions`, `boardroom_participants`, `boardroom_turns`. One `ai_run` per turn plus a synthesis run. A per-session lock ensures one active generation at a time.
- **Failures**: One executive's turn fails → it is marked skipped and the session continues. Budget exceeded mid-session → pause with a notice.
- **AT**: AT-08-1 three executives each contribute and the synthesis references each contribution. AT-08-2 proposals are not created without confirmation. AT-08-3 a non-invited member cannot access the session.

## WF-09 Cases and projects
- **Actors**: Member+.
- **Trigger**: Manual creation (S-28/S-30), or confirmation of an executive proposal.
- **Steps**: Create a case (a business problem or matter under work: title, description, status, priority, owner, linked executives, documents, conversations). Projects group tasks toward a deliverable and can belong to a case. Lifecycle per SOW §3: **create → assign → track → update → close**. Any case, project or task can be **linked to decisions and to approvals** (action requests). The exact semantics are OQ-032.
- **Backend**: CRUD plus activity log, `work_links` (work item ↔ decision / approval). The case memory is updated on significant events (spec 09 §3.2). Optional ClickUp sync (WF-13).
- **AT**: AT-09-1 the case detail aggregates linked conversations, boardrooms, decisions, approvals and tasks. AT-09-2 executive responses in a case include the case context and the case memory. AT-09-3 a closed case is read-only except for reopen (Admin). AT-09-4 a task created from an approved action links back to the approval.

## WF-10 Tasks
- **Actors**: Member+; executives (proposal and follow-through).
- **Steps**: Create or confirm a task → assign an owner (human or executive) → status flow `todo → in_progress → blocked → done | cancelled` → due date reminders. Executive-owned tasks: a scheduled follow-through job lets the executive report progress or ask for input. It never takes governed actions without policy evaluation.
- **AT**: AT-10-1 status transitions follow the allowed flow. AT-10-2 an overdue task generates a notification. AT-10-3 an executive follow-through action needing approval creates an approval request.

## WF-11 Decisions
- **Steps**: An executive or human proposes → a human accepts or rejects (BR-W-04) → an accepted decision can spawn tasks → it can later be superseded by a newer decision (linked).
- **AT**: AT-11-1 an executive cannot accept a decision via a tool. AT-11-2 the decision log is filterable and links to its source.

## WF-12 Governance approval
- **Actors**: Executive (requester on behalf of a user), approver(s).
- **Trigger**: The policy engine returns Require Approval.
- **Steps**: 1) Action snapshot saved and hashed. 2) Approval request created and approvers notified (S-36). 3) The approver reviews the payload diff and context (S-37) → approve or reject with a comment. 4) If approved: the execution job runs with an idempotency key and the result is recorded. 5) The requesting conversation is updated.
- **Failures**: Expiry → `expired`, and the executive is informed. The execution fails after approval → retry per the integration's policy. It does not re-require approval if the payload is unchanged.
- **AT**: see spec 10 §8 (approval-bypass suite).

## WF-13 Integrations (connect, operate, disconnect)
- **Actors**: Owner/Admin (connect); executives (operate under governance); system (webhooks/sync).
- **Steps**: 1) Connect from S-45 via OAuth (ClickUp, Dropbox, Google Drive, GoHighLevel) or API key/Private Integration token (GHL alternative). Choose the scopes. 2) Tokens are encrypted and stored. 3) Health check. 4) Operations become available as tools (spec 08 matrix). 5) Disconnect revokes the token at the provider where supported and deletes it locally.
- **Failures**: Token expired → refresh. Refresh fails → status `needs_reauth` and Admin notified. Provider rate limit → backoff using the provider's headers.
- **AT**: AT-13-1 connect and disconnect round trip. AT-13-2 a revoked token produces `needs_reauth` and no silent failures. AT-13-3 a webhook signature failure is rejected and logged.

## WF-14 Content Factory
- **Actors**: Member+ (create), content_publisher (publish), executives (drafting).
- **Steps** (per SOW §4): 1) **Intake**: upload media or documents (audio, video, PDF, DOCX, text), or import from Drive/Dropbox (S-42). 2) **Transcription when applicable**: audio and video are transcribed by a third-party speech-to-text API (spec 08 §4.6). The transcript is stored with timestamps. 3) Brief: type, goal, audience, channel, executive. 4) **AI drafting/transformation**: the executive drafts or transforms the source (e.g. transcript → blog, article → social posts, long → summary) using Brand DNA and RAG. 5) Edit and comment (S-43). This is a text editor; **no custom media or video editor**. 6) Submit for review → approval (governance). 7) Publish or export to the **agreed destination(s)** (OQ-012; at least one must work end to end). 8) Status tracked throughout (S-44): `intake → transcribing → drafting → in_review → approved → scheduled → published/exported | failed`.
- **Failures**: Transcription failure → retry ×3, then `failed` with the reason and a manual retry. Unsupported or oversized media → rejected at intake (limits OQ-005). Publish failure → retry per destination policy, failure reported on S-44 and in notifications.
- **AT**: AT-14-1 a draft reflects the brand voice fields (rubric-based eval). AT-14-2 publishing without approval is impossible (bypass suite). AT-14-3 a scheduled publish runs once at the scheduled time. AT-14-4 an uploaded audio/video file is transcribed and transformed into a draft. AT-14-5 the agreed destination receives the approved content in a real (sandbox) account; a simulation does not count.

## WF-15 Billing
- **Steps**: Select a plan → Stripe Checkout → webhook `checkout.session.completed` / `customer.subscription.*` → subscription and entitlements updated → manage via the Customer Portal (S-51) → `invoice.payment_failed` → grace → read-only (BR-S-02).
- **AT**: AT-15-1 the entitlements change only after a verified webhook, not on the redirect. AT-15-2 a duplicate webhook event is processed once. AT-15-3 a downgrade beyond usage blocks creation but does not delete data.

## WF-16 Monitoring (operator)
- **Actors**: Platform admin, on-call engineer.
- **Steps**: An alert fires (spec 13) → incident opened (S-57) → triage using the correlation ID across logs, traces and Sentry → mitigate → resolve → postmortem.
- **AT**: AT-16-1 a forced test error appears in Sentry with org ID and correlation ID, and without PII. AT-16-2 a synthetic alert reaches the on-call channel.

## WF-17 Recovery
- **Actors**: Platform admin (authorized).
- **Scenarios**: a) A failed background job: authorized manual retry from S-57 (audited). b) A failed integration action: retry respecting idempotency. c) Data restore: PITR to a new instance → verify → cut over (runbook in spec 13). d) Tenant-level restore of soft-deleted items within the retention window.
- **AT**: AT-17-1 a quarterly restore drill succeeds within the RTO. AT-17-2 a retry by a non-admin is denied. AT-17-3 a retry of an already-succeeded action is a no-op.
