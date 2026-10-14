# 01 — Product Requirements Document (PRD)

| Field | Value |
|---|---|
| Status | DRAFT v0.1 — pending client SOW reconciliation |
| Date | 2026-10-14 |
| Source basis | **`AdvoLevel_Concise_Integrated_SOW.pdf`** (concise quotation baseline, reviewed 2026-10-14) + `prompt.md`. The detailed master SOW, workflows and design inventory referenced by the SOW are not yet available (KI-001). |
| SOW coverage | See `docs/SOW_INCLUSION_MATRIX.md` |

## Classification legend
- **CONFIRMED**: stated in the concise SOW (cited as "SOW §n") or explicitly requested in the planning brief.
- **PROPOSED**: our recommendation, which needs client approval.
- **ASSUMED**: a working assumption we will use until it is corrected.
- **NEEDS CLARIFICATION**: an open question (see `15-risks-and-open-questions.md`).
- **OUT OF SCOPE**: excluded from commercial V1.

## 1. Product vision
AdvoLevel is a multi-tenant **AI Executive Operating System**. Each subscribing business gets a team of configurable AI specialist executives. The executives:
- know the organization through its *Organizational DNA* and documents,
- work in persistent offices,
- convene in boardrooms,
- turn conversations into cases, projects, tasks and decisions,
- act in the business's tools (ClickUp, GoHighLevel, Dropbox, Google Drive) under human governance and approvals,
- produce content through a Content Factory.

*(Vision statement: PROPOSED wording, derived from the CONFIRMED feature list.)*

## 2. Target users
| User | Description | Classification |
|---|---|---|
| Business owner / founder | Primary buyer; uses executives for strategic and operational advice | ASSUMED |
| Organization administrator | Configures org, executives, integrations, billing, governance | CONFIRMED (role named in brief) |
| Organization member | Uses executives, boardrooms and work items within their permissions | CONFIRMED (role named in brief) |
| Platform administrator | AdvoLevel operator; manages tenants, plans and platform health | CONFIRMED (role named in brief) |
| Target market segment (SMB, agency, mid-market?) | — | NEEDS CLARIFICATION (OQ-034) |

## 3. Business problems addressed (ASSUMED — validate with client)
1. Small and mid-size businesses cannot afford a full C-suite of specialists.
2. Generic AI chat lacks organizational context, continuity, accountability and follow-through.
3. AI advice rarely becomes tracked work or executed actions.
4. Businesses need control: AI must not act in business systems without policy and approval.

## 4. Feature set (commercial V1)

| ID | Feature | Classification | Notes |
|---|---|---|---|
| REQ-001 | Multi-tenant SaaS with organization isolation | CONFIRMED | |
| REQ-002 | ~57 core screens | CONFIRMED (count approx.) | Official list NEEDS CLARIFICATION (OQ-002) |
| REQ-003 | Five functioning, configurable specialist executives, delivered as **five standard executive templates** | CONFIRMED | Identities NEEDS CLARIFICATION (OQ-003); configuration boundaries NEEDS CLARIFICATION (OQ-004) |
| REQ-003a | **Customer-defined executive team**: each organization decides how many executives it has. It can create executives from a standard template or from scratch, configure them, enable/disable them and delete them, up to its plan limit `executives.max` (which may be unlimited) | CONFIRMED (user instruction, 2026-10-14) | See DEC-018 |
| REQ-004 | Reusable Executive Brain (shared orchestration engine) | CONFIRMED | |
| REQ-005 | Persistent Executive Offices (per-executive workspace + history) | CONFIRMED | |
| REQ-006 | Multi-executive Boardrooms | CONFIRMED | Interaction model NEEDS CLARIFICATION (OQ-031) |
| REQ-007 | Organizational DNA covering **mission, goals, policies, SOPs, brand and structure** | CONFIRMED (SOW §3) | Sections in spec 03 WF-04 |
| REQ-008 | Document upload, parsing, tenant-isolated RAG/source retrieval | CONFIRMED (SOW §3) | Formats/limits NEEDS CLARIFICATION (OQ-005) |
| REQ-008a | **Contextual case memory** | CONFIRMED (SOW §3) | Spec 09 §3.2 |
| REQ-008b | **Retention/deletion controls** (customer-facing) | CONFIRMED (SOW §3) | Default periods OQ-016; S-48 |
| REQ-005a | **Searchable history** for offices and boardrooms | CONFIRMED (SOW §3) | S-10, S-14, S-18 |
| REQ-009 | Native cases, projects and tasks: create, assign, track, update, close, and **link work to decisions and approvals** | CONFIRMED (SOW §3) | Case definition NEEDS CLARIFICATION (OQ-032) |
| REQ-010 | Projects | CONFIRMED | |
| REQ-011 | Tasks | CONFIRMED | |
| REQ-012 | Decisions (recorded, traceable) | CONFIRMED | |
| REQ-013 | Governance policies (Allow / Deny / Require Approval) | CONFIRMED | |
| REQ-014 | Human approvals | CONFIRMED | |
| REQ-015 | ClickUp integration | CONFIRMED | Operations NEEDS CLARIFICATION (OQ-007) |
| REQ-016 | GoHighLevel integration: **CRM/contact/workflow operations** | CONFIRMED (SOW §4) | Exact operations must be listed in the signed inclusion matrix (OQ-008) |
| REQ-017 | Dropbox: **authorized document access/import** | CONFIRMED (SOW §4) | Write access only if chosen as the Content Factory export destination (OQ-009) |
| REQ-018 | Google Drive: **authorized document access/import** | CONFIRMED (SOW §4) | Same as Dropbox (OQ-010) |
| REQ-019 | Stripe: **monthly/annual billing, plan entitlements, customer management** | CONFIRMED (SOW §4) | |
| REQ-020 | Content Factory: **media/document intake, transcription when applicable, AI drafting/transformation, review/approval, status tracking, at least one agreed functional publish/export destination**. Use existing APIs/services; no custom media editor | CONFIRMED (SOW §4) | Destination and content types NEEDS CLARIFICATION (OQ-012, OQ-022) |
| REQ-020a | Approved internal and external actions **actually execute**, with authorization, safe retries and failure reporting | CONFIRMED (SOW §4) | Spec 10 §8 |
| REQ-021 | Subscription billing | CONFIRMED | Plans NEEDS CLARIFICATION (OQ-011) |
| REQ-022 | Entitlements enforcement | CONFIRMED | |
| REQ-023 | Security | CONFIRMED | Compliance targets NEEDS CLARIFICATION (OQ-015) |
| REQ-024 | Testing | CONFIRMED | |
| REQ-025 | Monitoring | CONFIRMED | |
| REQ-026 | Deployment | CONFIRMED | Hosting NEEDS CLARIFICATION (OQ-014) |
| REQ-027 | Handover: source repository, editable Figma files, configurations/prompts, deployment instructions, credentials inventory, monitoring/backup basics, technical documentation | CONFIRMED (SOW §6) | Spec 12 §10 |
| REQ-027a | Deployment into **AdvoLevel-controlled infrastructure and accounts** | CONFIRMED (SOW §6) | |
| REQ-027b | All commissioned source, designs and artifacts belong to AdvoLevel on payment; third-party licences disclosed; defined defect correction/warranty terms | CONFIRMED (SOW §6) | Warranty terms to be proposed by the vendor (OQ-018) |
| REQ-028 | Premium "Concept B" visual design (deep navy, warm neutrals, restrained gold, premium editorial/executive aesthetic) | CONFIRMED (SOW §2) | |
| REQ-028a | **Editable Figma design system + clickable critical-flow prototype**, editable Figma source and assets, produced by the contractor | CONFIRMED (SOW §2) | Spec 05 §9 |
| REQ-028b | **Public website** screens within the ~57-screen inventory | CONFIRMED (SOW §2) | S-W1…S-W5 |
| REQ-028c | Responsive desktop/tablet/mobile; loading, empty, error, permission and **approval** states | CONFIRMED (SOW §2) | Spec 04 §0 |
| REQ-029 | Audit log of security-relevant and AI tool actions | PROPOSED | Needed for governance |
| REQ-030 | Configurable AI model providers | PROPOSED | |
| REQ-031 | Source-referenced answers; explicit "insufficient evidence" behaviour | PROPOSED | |
| REQ-032 | In-app notifications | PROPOSED | Email/other channels NEEDS CLARIFICATION (OQ-028) |
| REQ-033 | Platform admin console | PROPOSED | Scope NEEDS CLARIFICATION (OQ-033) |
| REQ-034 | Usage metering (AI tokens, storage, seats) | PROPOSED | Needed for entitlements and cost control |
| REQ-035 | Team invitations | PROPOSED (brief lists the workflow) | |
| REQ-036 | MFA for users | PROPOSED | |

## 5. Exclusions
**CONFIRMED OUT OF SCOPE (SOW §4–§5):** proprietary model training; a custom billing engine (Stripe is used); a full video editor or custom media editor (existing APIs/services are used).

**ASSUMED OUT OF SCOPE** (must be listed as EXCLUDED in the inclusion matrix and confirmed before signature):
- Native mobile apps (iOS/Android). The web app will be responsive.
- Voice/telephony interfaces to executives.
- On-premise or single-tenant deployments.
- Marketplace of third-party integrations beyond the five named.
- Formal compliance certification (SOC 2, ISO 27001, HIPAA). We design toward good practice but **claim no certifications**.
- Multi-language UI (i18n): NEEDS CLARIFICATION (OQ-023). English only is assumed.
- Autonomous actions without any governance gate.

## 6. Functional requirements (summary — details in specs 02–09)
| ID | Requirement |
|---|---|
| FR-01 | A user can register, verify their email, create an organization, and become its Owner/Admin. |
| FR-02 | Admins can invite members by email, assign roles, and revoke access. |
| FR-03 | Each organization has its own Organizational DNA (structured profile), which is injected into every executive's context. |
| FR-04 | Users with permission can upload documents or link Drive/Dropbox folders. Documents are parsed, chunked, embedded and searchable only within the organization. |
| FR-05 | The organization builds its own executive team. Authorized users create executives (from one of the five standard templates or from scratch), up to the plan limit. Each executive has a persistent Office with a conversation history, configurable persona/role, knowledge scope and tool permissions. |
| FR-06 | A user can open a Boardroom with 2 to `boardroom.max_executives` (PROPOSED default 5) of the org's executives on a topic. The executives contribute in turn, and the session produces a synthesized summary with proposed decisions and tasks. |
| FR-07 | Executives can propose cases, projects, tasks and decisions. A user confirms them before they are created (PROPOSED default). |
| FR-08 | Every executive tool action is evaluated by the governance engine (Allow / Deny / Require Approval) before execution. |
| FR-09 | Approvers receive approval requests, can approve or reject them with a comment, and an approved action executes exactly once. |
| FR-10 | Integrations connect per organization via OAuth or API key. Tokens are encrypted. Supported operations are listed in spec 08. |
| FR-11 | The Content Factory produces content drafts from briefs, using Org DNA brand voice. Drafts go through review and approval, then are published or exported to the agreed destination(s). |
| FR-12 | Organizations subscribe to a plan via Stripe Checkout and manage it via the Stripe Customer Portal. Entitlements limit features and usage. |
| FR-13 | The platform admin can view tenants, plans, system health and incidents. |
| FR-14 | Answers grounded in documents show source references. When evidence is insufficient, the executive says so. |

## 7. Non-functional requirements (PROPOSED targets — the client must confirm them)
| ID | Category | Target |
|---|---|---|
| NFR-01 | Tenant isolation | Zero cross-tenant data access. Enforced in the application layer and in Postgres RLS. Covered by automated negative tests. |
| NFR-02 | Availability | 99.5% monthly for the web/API, excluding scheduled maintenance (ASSUMED; OQ-014). |
| NFR-03 | Performance | p95 non-AI API < 500 ms. AI first token < 3 s (p95, provider-dependent). Document ingestion of a 20-page PDF < 2 min. |
| NFR-04 | Scale (initial) | ASSUMED 100 orgs × 25 users. NEEDS CLARIFICATION (OQ-006, OQ-014). |
| NFR-05 | Security | OWASP ASVS L2-aligned controls. Encrypted at rest and in transit. Secrets never in code or logs. |
| NFR-06 | Accessibility | WCAG 2.2 AA for core flows. |
| NFR-07 | Browser support | Latest 2 versions of Chrome, Edge, Safari and Firefox. Responsive from 360 px. |
| NFR-08 | Observability | Every request and AI run has a correlation ID. Errors go to central tracking. See spec 13. |
| NFR-09 | Recoverability | RPO ≤ 24 h (≤ 5 min with PITR, PROPOSED). RTO ≤ 4 h. |
| NFR-10 | Auditability | Every governed action and every approval is recorded immutably. |
| NFR-11 | Cost control | Per-tenant AI usage is metered. Plan limits are enforced. |

## 8. Success metrics (PROPOSED)
- Activation: % of new orgs that complete Org DNA and at least 1 executive conversation within 7 days.
- Engagement: weekly active users per org; Boardroom sessions per org per week.
- Follow-through: % of executive-proposed tasks accepted and completed.
- Trust: % of grounded answers with citations; rate of approvals vs rejections.
- Reliability: error rate, AI run failure rate, integration sync failure rate.
- Commercial: trial→paid conversion, churn, AI cost per tenant vs plan revenue.

## 9. Product-level acceptance criteria (V1)
1. All CONFIRMED features REQ-001…REQ-028 are implemented and demonstrable.
2. The final screen inventory (client-approved) is implemented with loading, empty, error and permission states.
3. The automated cross-tenant isolation suite passes with zero failures.
4. The approval-bypass test suite passes with zero failures (spec 10 §8).
5. All five standard templates produce working executives, and a custom executive created from scratch works. All of them answer with Org DNA context and cited RAG sources in a demo tenant. Creating an executive beyond the plan's `executives.max` is blocked.
6. At least one end-to-end governed write action per integration succeeds in a sandbox account.
7. A Stripe test-mode subscription lifecycle works: subscribe, upgrade, cancel, failed payment.
8. Monitoring, alerting and backup restore are demonstrated (spec 13).
9. Handover pack delivered (spec 12 §10).
10. (SOW §7) Every acceptance gate is passed by **demonstrating working software deployed in an environment and transferring that milestone's deliverables**. Visual mockups or simulated AI or integration actions do not count as completion.
