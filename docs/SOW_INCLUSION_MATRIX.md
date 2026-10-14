# SOW Inclusion Matrix and Documentation Compliance Review

| Field | Value |
|---|---|
| Source | `d:\POC\AdvoLevel_Concise_Integrated_SOW.pdf`: "Consolidated Contractor Scope, UX/UI + Full-Stack Commercial V1" (2 pages, sections 1–7) |
| Reviewed | 2026-10-14 |
| Purpose | (a) the **INCLUDED / EXCLUDED / NEEDS CLARIFICATION matrix for SOW Sections 2–6** required by SOW §7; (b) a review of whether `docs/` fulfils every SOW requirement |
| Status | DRAFT. To be finalized and signed with the client. The detailed master SOW, workflows and existing screen inventory referenced by the SOW are not yet available (OQ-001, OQ-002). |

Legend: **INCLUDED**: in our fixed scope. **EXCLUDED**: not in scope. **NC**: NEEDS CLARIFICATION before signature.
"Doc status" reports the review result: ✅ covered before this review · 🔧 gap found and **fixed in this review** · ⚠️ covered, but an input or decision is still open.

---

## 1. Inclusion matrix — SOW Sections 2–6

### §1 Product outcome
| SOW item | Matrix | Where specified | Doc status |
|---|---|---|---|
| Secure, production-deployed, multi-tenant AI executive OS; per-org workspace, knowledge, configurable executives, boardrooms, governed actions, subscriptions; a functioning SaaS, not a prototype | INCLUDED | Spec 01 §1, §4; spec 14 gate rule | ✅ |

### §2 UX/UI design and frontend
| # | SOW item | Matrix | Where specified | Doc status |
|---|---|---|---|---|
| 2.1 | Editable Figma design system | INCLUDED | Spec 05 §9 F-1, F-2; roadmap D1 | 🔧 Previously "who produces Figma" was open and design effort was excluded. Now vendor-produced, estimated separately as D1 |
| 2.2 | Clickable critical-flow prototype | INCLUDED | Spec 05 §9 F-5 | 🔧 Proposed critical-flow list added. ⚠️ the client must confirm the flows |
| 2.3 | Concept B: deep navy, warm neutrals, restrained gold, premium editorial/executive aesthetic | INCLUDED | Spec 05 §1–§3 | ✅ (serif display type supports the "editorial" look) |
| 2.4 | ~57 core screens from the **existing** inventory: public website, onboarding, command center, executive offices, boardrooms, knowledge, cases/work, approvals, Content Factory, billing, administration | INCLUDED (count) / **NC (exact list)** | Spec 04 §L | 🔧 **Public website was missing.** Added S-W1…S-W5 and merged 5 screens to keep 57. ⚠️ The client's existing inventory must be supplied and reconciled **before signature** (OQ-002) |
| 2.5 | Shared components; responsive desktop/tablet/mobile | INCLUDED | Spec 05 §5, §8; spec 04 §0 | ✅ |
| 2.6 | Loading, empty, error, permission **and approval** states | INCLUDED | Spec 04 §0 | 🔧 **Approval state was missing** from the standard states. Added |
| 2.7 | Deliver editable Figma source, assets, responsive working frontend | INCLUDED | Spec 05 §9; spec 12 §10 handover | 🔧 Ownership and transfer added |

### §3 Platform and executive intelligence
| # | SOW item | Matrix | Where specified | Doc status |
|---|---|---|---|---|
| 3.1 | Tenant-isolated authentication, org/team membership, invitations | INCLUDED | Spec 02, 03 WF-01…03, 10 §1–3 | ✅ |
| 3.2 | Backend-enforced roles and permissions | INCLUDED | Spec 02 §2, spec 10 §2, AZ suite | ✅ |
| 3.3 | Customer admin and platform admin | INCLUDED | Spec 02 §1; S-48…S-57 | ✅ |
| 3.4 | One reusable Executive Brain/orchestrator | INCLUDED | Spec 09 §1, §3 | ✅ |
| 3.5 | Five functioning configurable specialist executives | INCLUDED as **five standard templates** | Spec 09 §2; BR-E-01 | ⚠️ The five roles must be defined (OQ-003) |
| 3.6 | Administrators can configure **additional** roles, instructions, tools and permissions without rebuilding the app | INCLUDED. **No fixed limit of five: the customer decides how many executives it has** (create from a template or from scratch). The only cap is the optional plan setting `executives.max`, which can be `-1` = unlimited | DEC-018; BR-E-01…06; WF-07; S-12, S-15 | ✅ Matches SOW. ⚠️ per-plan values (OQ-036) |
| 3.7 | Persistent executive offices | INCLUDED | Spec 09 §3.2; S-13 | ✅ |
| 3.8 | Multi-executive boardrooms | INCLUDED | Spec 09 §6; WF-08 | ✅ ⚠️ semantics (OQ-031) |
| 3.9 | …with case context, decisions, task follow-through | INCLUDED | Spec 09 §3.1, §3.3; WF-10/11 | ✅ |
| 3.10 | …and **searchable history** | INCLUDED | S-10, S-14, S-18 | 🔧 Boardroom history search added (S-18) |
| 3.11 | Organizational DNA: **mission, goals, policies, SOPs, brand, structure** | INCLUDED | WF-04; REQ-007 | 🔧 **SOPs were missing** from the DNA sections. Sections now aligned to the SOW |
| 3.12 | Document upload, parsing, tenant-isolated RAG/source retrieval | INCLUDED | Spec 09 §7; WF-05 | ✅ ⚠️ formats/limits (OQ-005) |
| 3.13 | **Contextual case memory** | INCLUDED | Spec 09 §3.2; spec 07 `case_memory_versions`; S-29 | 🔧 Was only implicit (case context). Now an explicit, versioned case memory |
| 3.14 | **Retention/deletion controls** | INCLUDED | Spec 07 §3.11, §5; S-48 | 🔧 Was "if allowed". Now customer-facing controls within platform bounds. ⚠️ default periods (OQ-016) |
| 3.15 | Native cases, projects, tasks: create, assign, track, update, **close** | INCLUDED | WF-09/10; S-28…S-33 | 🔧 Close/reopen made explicit |
| 3.16 | Link work to decisions **and approvals** | INCLUDED | Spec 07 `work_links`; WF-09 | 🔧 **Approval links were missing**. Added |

### §4 Governance, integrations and Content Factory
| # | SOW item | Matrix | Where specified | Doc status |
|---|---|---|---|---|
| 4.1 | Central allow/deny/require-approval policy checks | INCLUDED | Spec 10 §8 | ✅ |
| 4.2 | Human approval queue | INCLUDED | S-36/S-37; WF-12 | ✅ |
| 4.3 | Complete audit trail | INCLUDED | Spec 10 §7 | ✅ |
| 4.4 | Approved internal and external actions **actually execute**, with authorization, safe retries and failure reporting | INCLUDED | Spec 10 §8.2; spec 13 §11; S-47, S-57 | ✅ |
| 4.5 | ClickUp: task/work synchronization | INCLUDED | Spec 08 §4.1 | ⚠️ **NC**: exact operations and sync direction (OQ-007) |
| 4.6 | GoHighLevel: CRM/contact/**workflow** operations | INCLUDED | Spec 08 §4.2 | 🔧 **Workflow operations were missing** (add/remove contact to workflow, tags). Added. ⚠️ **NC**: final operations, install model (OQ-008) |
| 4.7 | Dropbox: authorized document access/import | INCLUDED (read/import) | Spec 08 §4.3 | 🔧 Write ops reduced to "only if chosen as the export destination" |
| 4.8 | Google Drive: authorized document access/import | INCLUDED (read/import) | Spec 08 §4.4 | 🔧 Same as Dropbox. ⚠️ scope approach (OQ-010) |
| 4.9 | Stripe: monthly/annual billing, plan entitlements, customer management | INCLUDED | Spec 08 §4.5; WF-15; S-07, S-51 | ✅ ⚠️ plans and prices (OQ-011) |
| 4.10 | AI model APIs | INCLUDED | Spec 08 §4.6; spec 09 §4 | ✅ ⚠️ provider/budget (OQ-013) |
| 4.11 | Exact read/write operations listed in the signed inclusion matrix | **NC** | §2 below | ⚠️ Proposed list in spec 08 §4; the client must sign it |
| 4.12 | Content Factory: **media/document intake** | INCLUDED | WF-14; S-42; spec 07 `content_assets` | 🔧 **Was missing** (only briefs existed) |
| 4.13 | **Transcription when applicable** | INCLUDED (via a third-party STT API) | Spec 08 §4.6; spec 09 §7.1 | 🔧 **Conflict fixed**: audio/video had been marked out of scope |
| 4.14 | AI drafting/transformation | INCLUDED | WF-14; `POST /content/{id}/transform` | 🔧 "Transformation" (repurposing) made explicit |
| 4.15 | Review/approval, status tracking | INCLUDED | WF-14; S-43, S-44 | ✅ |
| 4.16 | **At least one** agreed functional publish/export destination | INCLUDED (one) | Spec 08 §4.7; DEC-017 | ⚠️ **NC**: the destination must be named before signature (OQ-012) |
| 4.17 | Use existing APIs/services; no custom media editor | INCLUDED as a constraint | WF-14 | ✅ |

### §5 Cost-efficient engineering principles
| SOW item | Matrix | Where specified | Doc status |
|---|---|---|---|
| Proven frameworks, modular app, reusable UI, single configurable executive engine, shared governance/workflow services, established LLM APIs, managed infra, documented third-party APIs | INCLUDED | Spec 06; DEC-001…012 | ✅ |
| Suggested stack: Next.js/React, Python/FastAPI, PostgreSQL/pgvector, Stripe, managed storage/auth | INCLUDED (exact match) | Spec 06 §2 | ✅ |
| No proprietary model training | EXCLUDED | Spec 01 §5 | ✅ |
| No custom billing engine | EXCLUDED | Spec 01 §5 | 🔧 Now listed explicitly |
| No full video editor | EXCLUDED | Spec 01 §5 | 🔧 Now listed explicitly |

### §6 Quality, deployment and ownership
| # | SOW item | Matrix | Where specified | Doc status |
|---|---|---|---|---|
| 6.1 | Automated testing: critical flows, tenant isolation, access control, approval-bypass prevention, billing, AI orchestration, document retrieval, integrations, failed-action handling | INCLUDED | Spec 11 §3–§10 (TI, AZ, AB, BL, AI, RAG, §7, §8) | ✅ |
| 6.2 | **Manual** testing of critical flows | INCLUDED | Spec 11 §12 | 🔧 A scripted manual pass per gate added |
| 6.3 | Deploy into **AdvoLevel-controlled** infrastructure and accounts | INCLUDED | Spec 12 §10 | 🔧 Ownership changed from "PROPOSED" to CONFIRMED. ⚠️ **Conflict**: the current repo is under a personal account (KI-006) |
| 6.4 | Provide source repository | INCLUDED | Spec 12 §10 item 1 | ⚠️ Must be transferred to an AdvoLevel org |
| 6.5 | Editable Figma files | INCLUDED | Spec 05 §9 | ✅ |
| 6.6 | **Configurations/prompts** | INCLUDED | Spec 12 §10 item 3 | 🔧 Added explicitly |
| 6.7 | Deployment instructions | INCLUDED | Spec 12 §10 item 4 | ✅ |
| 6.8 | **Credentials inventory** | INCLUDED | Spec 12 §10 item 5 | 🔧 Added explicitly (no secret values) |
| 6.9 | Monitoring/backup basics | INCLUDED | Spec 13 | ✅ (our spec goes beyond "basics". See §3 note) |
| 6.10 | Technical documentation | INCLUDED | `docs/` | ✅ |
| 6.11 | IP: source, designs and artifacts belong to AdvoLevel on payment; third-party licences disclosed | INCLUDED | Spec 12 §10 item 8 | 🔧 Licence inventory/SBOM added |
| 6.12 | Defined defect-correction/warranty terms | INCLUDED (vendor to propose) | Spec 12 §10 | 🔧 Starting-point terms added. ⚠️ commercial decision (OQ-018) |

### Items in our specs that go beyond the SOW (scope control)
These are PROPOSED additions. For the fixed price, each must be listed as INCLUDED or downgraded before signature.
| Item | Recommendation |
|---|---|
| Content Factory scheduling/calendar | Keep (low cost, supports status tracking) |
| Full observability stack (Grafana dashboards, cost-anomaly alerts, incident records) beyond "monitoring/backup basics" | Keep Sentry + health + backups + core alerts as INCLUDED; mark the advanced dashboards as optional |
| Executive follow-through scheduler for executive-owned tasks | Keep (it is "task follow-through", SOW §3) |
| Platform admin incidents screen (S-57) | Keep a simplified version |
| ClickUp two-way sync | NC until OQ-007 |

---

## 2. Integration operations to sign (proposed; from spec 08 §4)
| Integration | Proposed INCLUDED operations | NC |
|---|---|---|
| ClickUp | List workspaces/spaces/lists; read tasks; create task; update status/assignee/due; add comment; status webhook | Two-way vs one-way; mapping model |
| GoHighLevel | Search/read contacts; create/update contact; read pipelines/opportunities; create/update opportunity; add note/task; read calendars; list workflows; add/remove contact to workflow; add/remove tags; contact/opportunity webhooks | Outbound SMS/email in scope? Agency vs sub-account install |
| Dropbox | Browse folders; download/import files; change webhook for sync | Upload only if it is the export destination |
| Google Drive | Picker-based file selection; download/export; change watch | Folder auto-sync (restricted scope); upload only if it is the export destination |
| Stripe | Customer, Checkout (monthly/annual), Customer Portal, subscription/invoice webhooks | Metered overage billing; Stripe Tax |
| AI model APIs | LLM chat/tool use (streaming); embeddings; speech-to-text | Providers and budget |
| Publish/export destination | **One** to be agreed. Fallback: export to Drive/Dropbox/download | **Destination name** (OQ-012) |

---

## 3. SOW §7 proposal requirements: documentation readiness
| Requirement | Status in docs |
|---|---|
| One all-inclusive fixed total | ❌ **Not in the technical docs (commercial).** Effort ranges (spec 14: ~48–80 ew + 8–14 dw) are inputs only (OQ-038) |
| INCLUDED/EXCLUDED/NC matrix for §2–6 | ✅ This document (§1) |
| Reconciled 57-screen list | ⚠️ Provisional 57 in spec 04 §L; the client's inventory is needed (OQ-002) |
| Exact integration actions / publishing destination(s) | ⚠️ Proposed (§2); destination NC |
| Milestone amounts | ❌ Commercial (OQ-038). Milestone structure and gates are ready (spec 14) |
| Objective acceptance tests per milestone | ✅ Spec 11 §12 |
| Functioning software at each gate; no mockups or simulated AI | 🔧 Gate rule added (spec 14, spec 11 §12, spec 01 §9 item 10) |
| Disclose third-party recurring service charges separately | ⚠️ Service list below; prices must be quoted by the commercial owner (OQ-038) |
| Staffing and design ownership | ⚠️ Team shape in `DEVELOPMENT_PLAN.md` §4; design ownership confirmed (AdvoLevel) |
| Dependencies, warranties, exclusions | ✅ Spec 15; spec 12 §10; spec 01 §5 (warranty terms to be finalized) |
| Scope changes need written approval | ✅ `DEVELOPMENT_PLAN.md` §5 |

### Third-party recurring services to disclose (billed to AdvoLevel's own accounts; prices not stated here)
| Service | Purpose | Pricing basis |
|---|---|---|
| Hosting/PaaS or cloud (compute) | web, API, workers | Monthly, usage/instance based |
| Managed PostgreSQL (pgvector) | Primary DB | Monthly by size + storage + backups |
| Managed Redis | Queue/cache | Monthly |
| Object storage | Documents, media | Per GB + egress |
| Managed auth provider | Login, MFA | Per MAU, often with a free tier |
| LLM provider(s) | Executives, boardrooms, content | Per token (largest variable cost) |
| Embeddings provider | RAG | Per token |
| Speech-to-text provider | Transcription | Per audio minute |
| Stripe | Billing | % + fixed fee per transaction |
| Transactional email | Invites, notifications | Monthly tier |
| Sentry | Error tracking | Monthly tier |
| Logs/metrics/traces backend | Observability | Monthly tier / usage |
| Uptime monitoring | Synthetics | Monthly tier |
| Malware scanning (if required) | Upload safety | Usage/monthly |
| GoHighLevel / ClickUp / Dropbox / Google | Customer-side accounts; possible marketplace/app fees | Per provider terms |
| Domain + TLS | — | Annual (TLS usually free) |
| Figma | Design files | Per editor seat |

---

## 4. Review summary
- **SOW items checked:** 58.
- **Already covered:** 33. Some of these still have open inputs (⚠️).
- **Gaps fixed in this review:** 25. The most important were:
  1. Public website screens
  2. The approval UI state
  3. Figma as a vendor deliverable, with its effort
  4. SOPs in Org DNA
  5. Contextual case memory
  6. Retention controls
  7. Work↔approval links
  8. GHL workflow operations
  9. Content Factory intake and **transcription** (this fixed a conflict)
  10. Drive/Dropbox reduced to import-only
  11. AdvoLevel ownership of all accounts
  12. Handover items: configurations/prompts, credentials inventory, licence inventory
  13. Warranty terms
  14. The functioning-software gate rule
  15. Manual testing
- **Still open before contract signature** (these block a fixed price):
  1. OQ-001: the master SOW, workflows and design inventory
  2. OQ-002: the existing screen inventory
  3. OQ-003: the five standard executive templates
  4. OQ-007 / OQ-008: exact ClickUp and GHL operations
  5. OQ-012: the publish/export destination
  6. OQ-011: plans and prices
  7. OQ-013: AI providers and budget
  8. OQ-018: warranty acceptance
  9. OQ-038: the commercial proposal itself
- **Conflicts with the SOW:**
  - The repository is under a personal, public GitHub account (KI-005, KI-006). Make it private and transfer it to AdvoLevel.
