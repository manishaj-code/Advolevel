# 02 — Business Rules and User Roles

| Field | Value |
|---|---|
| Status | DRAFT v0.1 |
| Date | 2026-10-14 |
| Basis | Roles named in the planning brief. Role granularity and the permission matrix are **PROPOSED**. |

## 1. Role model

Two independent scopes:
- **Platform scope**: AdvoLevel staff. This role is never granted through an organization membership.
- **Organization scope**: per-tenant. A user can belong to several organizations and can hold a different role in each.

| Role | Scope | Classification | Summary |
|---|---|---|---|
| Platform Super Admin | Platform | CONFIRMED (platform administrator) | Manages tenants, plans, feature flags, incidents. No default access to tenant content (see BR-PA-02). |
| Platform Support | Platform | PROPOSED | Read-only tenant metadata and health. No tenant content. |
| Org Owner | Org | PROPOSED | Exactly one per org (transferable). Full control, including billing and org deletion. |
| Org Admin | Org | CONFIRMED (organization administrator) | Manages members, executives, integrations, governance. Billing access is configurable (PROPOSED: yes). |
| Org Member | Org | CONFIRMED (organization member) | Uses executives, boardrooms, work items, and content within the granted scope. |
| Org Viewer | Org | PROPOSED | Read-only access to shared work items and decisions. Cannot chat with executives. |

**Capabilities layered on roles** (PROPOSED). These are assignable flags, not separate roles:
- `approver`: can decide approval requests. A policy can name specific approvers.
- `executive_configurator`: can edit executive persona, knowledge scope and tools. Admins have it by default.
- `knowledge_manager`: can upload and delete org documents and edit Org DNA.
- `content_publisher`: can approve Content Factory items for publishing.

## 2. Permission matrix (PROPOSED)

Legend: ✅ allowed · ⚙️ allowed if capability granted · ❌ denied · 👁 read-only

| Action | Owner | Admin | Member | Viewer |
|---|---|---|---|---|
| View org dashboard | ✅ | ✅ | ✅ | 👁 |
| Edit organization settings | ✅ | ✅ | ❌ | ❌ |
| Delete organization | ✅ | ❌ | ❌ | ❌ |
| Transfer ownership | ✅ | ❌ | ❌ | ❌ |
| Invite / remove members | ✅ | ✅ | ❌ | ❌ |
| Change member roles | ✅ | ✅ (not Owner) | ❌ | ❌ |
| Manage billing / plan | ✅ | ⚙️ (default ✅) | ❌ | ❌ |
| Edit Organizational DNA | ✅ | ✅ | ⚙️ knowledge_manager | 👁 |
| Upload / delete documents | ✅ | ✅ | ⚙️ knowledge_manager | ❌ |
| Chat in Executive Office | ✅ | ✅ | ✅ | ❌ |
| Create / delete executive | ✅ | ✅ | ⚙️ executive_configurator | ❌ |
| Configure / enable / disable executive | ✅ | ✅ | ⚙️ executive_configurator | ❌ |
| Create Boardroom session | ✅ | ✅ | ✅ | ❌ |
| Participate in Boardroom (invited) | ✅ | ✅ | ✅ | 👁 |
| Create / edit cases, projects, tasks | ✅ | ✅ | ✅ (own + assigned) | ❌ |
| Record decision | ✅ | ✅ | ✅ | ❌ |
| Approve request | ⚙️ | ⚙️ | ⚙️ | ❌ |
| Edit governance policies | ✅ | ✅ | ❌ | ❌ |
| Connect / disconnect integrations | ✅ | ✅ | ❌ | ❌ |
| Create content drafts | ✅ | ✅ | ✅ | ❌ |
| Publish content | ✅ | ✅ | ⚙️ content_publisher | ❌ |
| View audit log | ✅ | ✅ | ❌ | ❌ |

## 3. Business rules

### Tenancy
- **BR-T-01**: Every tenant-owned record has a non-null `organization_id`. No query may read tenant data without an organization scope.
- **BR-T-02**: The active organization is chosen per session or request, and the server checks it against the user's memberships on every request.
- **BR-T-03**: Org deletion is a soft-delete followed by a hard purge after the retention window (default 30 days PROPOSED; OQ-016).

### Platform admin
- **BR-PA-01**: Platform admin endpoints are a separate route group with separate authorization.
- **BR-PA-02**: Platform admins cannot read tenant conversations or documents by default. Support access ("break-glass") needs tenant Owner consent, is time-boxed and is audited. Whether this feature is wanted is NEEDS CLARIFICATION (OQ-033).

### Executives
- **BR-E-01** (CONFIRMED, user instruction 2026-10-14): **The customer decides how many executives their organization has.** The platform supplies five standard executive templates (the SOW's five specialist executives; identities NEEDS CLARIFICATION, OQ-003). An org can create any number of executives up to its plan's `executives.max`, and may leave some templates unused.
- **BR-E-01a**: Ways to create an executive: (a) **from a standard template**, which pre-fills the role and defaults; (b) **from scratch (custom)**, where the customer defines the role title, mandate, focus areas, persona, knowledge scope and tools. The same template may be used more than once (e.g. two sales executives for different regions), with a unique display name per org.
- **BR-E-01b** (PROPOSED): Onboarding offers the five standard templates, pre-selected. The customer can deselect any of them or add custom executives. Default: activate all five (within the plan limit).
- **BR-E-02**: Customers configure everything about their executives **except the platform safety rules and governance obedience**. These are always prepended and cannot be edited or overridden. Whether template-based executives can also change their core role mandate (or only extend it) is NEEDS CLARIFICATION (OQ-004).
- **BR-E-03**: An executive can never be granted a tool permission broader than the org's governance policy allows.
- **BR-E-04**: Executives can be **disabled** (hidden from members, history kept) or **deleted**. Deletion is a soft delete: conversations and decisions remain read-only with the executive shown as "(deleted)"; it is purged after the retention window (OQ-016). An executive that is in an active Boardroom session or that owns open tasks cannot be deleted until those are closed or reassigned.
- **BR-E-05**: `executives.max` counts **enabled** executives (PROPOSED). Disabled executives don't count, so customers can swap executives without deleting history. A downgrade below the current count follows BR-S-03: no new executives can be enabled, and nothing is auto-disabled.
- **BR-E-06**: The platform admin sets `executives.max` per plan, using `-1` for unlimited, and can override it per org.

### Conversations and offices
- **BR-C-01**: Office conversations are private to the user who created them by default. They can be shared with specific members or with the whole org (PROPOSED).
- **BR-C-02**: Conversation history persists until the user or an admin deletes it, or until the retention policy removes it (OQ-016).

### Boardrooms
- **BR-B-01**: The creator becomes the session owner. Invited human participants can post and read. Viewers can read only.
- **BR-B-02**: A session includes 2 to `boardroom.max_executives` executives (PROPOSED default 5, set per plan), chosen from the org's enabled team, however large that team is. The executives contribute in a coordinated order, and a moderator synthesis produces the summary.
- **BR-B-03**: Proposals created in a Boardroom (decisions and tasks) need human confirmation.

### Work management
- **BR-W-01**: A task has exactly one owner, either a human or an executive (an "executive task" means follow-through by the AI). It can have several watchers.
- **BR-W-02**: Members can edit work items they created, own or are assigned to. Admins can edit all of them.
- **BR-W-03**: A decision records: statement, rationale, alternatives considered, decision-maker (human), contributing executives, source conversation/boardroom, date, status (proposed / accepted / rejected / superseded).
- **BR-W-04**: Executives can *propose* a decision but cannot *accept* one. Acceptance is a human action.

### Governance and approvals
- **BR-G-01**: Every tool invocation that reads from or writes to an external system, sends a communication, publishes content or spends money goes through the policy engine.
- **BR-G-02**: The evaluation result is Allow, Deny or Require Approval. When no policy matches, the default is **Require Approval for writes** and **Allow for reads** (PROPOSED).
- **BR-G-03**: Approvers cannot approve a request they triggered themselves, unless the policy explicitly allows self-approval. The default is to disallow it (PROPOSED).
- **BR-G-04**: An approval binds to an immutable snapshot of the action payload, using a hash. If the payload changes, the approval is invalidated.
- **BR-G-05**: Approvals expire after 72 h by default (PROPOSED, configurable).
- **BR-G-06**: An approved action executes at most once (idempotency key).

### Subscription entitlements (structure PROPOSED, values NEEDS CLARIFICATION — OQ-011)
| Entitlement key | Type | Example semantics |
|---|---|---|
| `seats.max` | int | Maximum active members |
| `executives.max` | int (`-1` = unlimited) | Maximum enabled executives the org may have (BR-E-05) |
| `executives.custom_allowed` | bool | Whether creating from scratch is allowed, or only from standard templates (PROPOSED; plan-dependent) |
| `boardroom.enabled` | bool | Boardroom feature access |
| `boardroom.max_executives` | int | Executives per session |
| `ai.monthly_credits` | int | Metered AI usage units |
| `storage.max_gb` | int | Document storage |
| `documents.max_count` | int | Ingested documents |
| `integrations.allowed` | list | Which providers |
| `content_factory.enabled` | bool | |
| `content_factory.monthly_items` | int | |
| `audit_log.retention_days` | int | |

- **BR-S-01**: Entitlements are checked on the server at the point of use. The UI hides or disables features as a convenience only.
- **BR-S-02**: Past-due subscription: there is a grace period (PROPOSED 7 days), then the org becomes read-only. Data is not deleted.
- **BR-S-03**: When an org downgrades below its current usage (for example, too many seats), it cannot create new items until it is back within limits. Nothing is auto-deleted.
- **BR-S-04**: Hard AI usage cap per plan: on reaching it, executive chat is blocked with an upgrade prompt. Overage billing is NEEDS CLARIFICATION (OQ-011).
