# 15 — Risks and Open Questions

| Field | Value |
|---|---|
| Status | DRAFT v0.1 — living document |
| Date | 2026-10-14 |
| Tracking | Day-to-day status is mirrored in `docs/OPEN_QUESTIONS.md`. This spec is the authoritative list. |

Severity: **Critical** (blocks multiple milestones / commercial risk) · **High** (blocks a milestone) · **Medium** (affects design or quality) · **Low**.
Owner: **Client**, **Vendor** (our team), **Joint**.
Blocks: the milestone that cannot be *completed* without an answer. "Start" means the milestone also cannot *start* without it.

## 1. Open questions

| ID | Question | Sev | Owner | Dependency / affects | Blocks |
|---|---|---|---|---|---|
| OQ-001 | *Partly answered 2026-10-14*: the **concise integrated SOW** was received and reviewed (`SOW_INCLUSION_MATRIX.md`). Still needed: the **detailed master SOW, workflows and design inventory** that the SOW's contracting note says remain supporting specifications. | Critical | Client | All specs | Contract signature (conflicts must be reconciled in writing before award) |
| OQ-002 | Provide the **existing screen inventory** referred to in SOW §2, to reconcile against our provisional 57 (spec 04 §L) before signature. | Critical | Client | Spec 04, D1, M3–M12 | Contract signature |
| OQ-003 | What are the **five standard executive templates** (title, mandate, responsibilities, default tools, boundaries)? They are the starting points customers pick from (DEC-018). | Critical | Client | Spec 09, M5, F-6 | M5 completion |
| OQ-004 | **Executive customization boundaries**: *Partly answered 2026-10-14*: customers decide how many executives they have and configure them; they can add, disable and delete them (DEC-018). Still open: can a template-based executive's mandate be fully replaced or only extended? Is model choice per executive allowed? | Medium | Client | BR-E-02, S-15 | — |
| OQ-037 | **Public website**: page list, copy and imagery source, CMS needed or static pages acceptable, blog included? | Medium | Client | S-W1…S-W5 | M3 |
| OQ-038 | **Proposal commercial items** (SOW §7): one all-inclusive fixed price, milestone amounts, staffing plan, separate disclosure of third-party recurring charges (see `SOW_INCLUSION_MATRIX.md` §4), exclusions and warranty. This is not a technical document; it must be prepared by the commercial owner before signature. | Critical | Vendor | Proposal | Contract signature |
| OQ-039 | **Transcription**: expected media volume/duration per month, languages, and whether transcripts should also feed the RAG knowledge base | Medium | Client | WF-14, cost | M10 |
| OQ-036 | **Executive limits per plan**: the value of `executives.max` for each plan (including whether any plan is unlimited), `boardroom.max_executives`, and whether creating custom executives (from scratch) is available on all plans or only higher tiers | High | Client | BR-E-05/06, OQ-011 | M11 |
| OQ-005 | **Supported file formats and limits** (types, max size, pages, OCR of scans, spreadsheets, images/audio)? | High | Client | Spec 09 §7.1, M4 | M4 |
| OQ-006 | **User and organization limits**: seats per plan, orgs per user, documents/storage per org, expected tenant count at launch and year 1? | High | Client | Entitlements, scaling, NFR-04 | M11, M13 |
| OQ-007 | **ClickUp**: exact operations, one-way or two-way sync, master of record, mapping model? | High | Client | Spec 08 §4.1 | M9 (ClickUp) |
| OQ-008 | **GoHighLevel**: agency or sub-account install; modules (contacts, opportunities, calendars, conversations); is outbound SMS/email in scope? Marketplace app or private integration? | High | Client | Spec 08 §4.2 | M9 (GHL) |
| OQ-009 | **Dropbox**: read-only knowledge source, or also write outputs? App-folder or full access? | Medium | Client | Spec 08 §4.3 | M9 (Dropbox) |
| OQ-010 | **Google Drive**: is per-file Picker access (`drive.file`) acceptable, or is folder auto-sync (restricted scope + security assessment) required? | High | Client | DEC-013, RSK-008 | M9 (Drive) |
| OQ-011 | **Subscription plans and entitlements**: tiers, prices, trial, annual billing, AI usage caps, overage billing, taxes (Stripe Tax?), currencies? | Critical | Client | BR-S-*, M11 | M11 |
| OQ-012 | **Content Factory publishing destinations** (e.g. GHL social/blog, WordPress, LinkedIn, Meta, email) or export-only? | Critical | Client | Spec 08 §4.7, M10 | M10 |
| OQ-013 | **AI models and budget**: preferred providers, platform-paid vs customer BYO keys, monthly AI budget, per-tenant cost ceilings, embeddings provider, data-retention requirements with providers? | Critical | Joint | DEC-009, cost model | M5 start |
| OQ-014 | **Hosting and scale**: cloud preference (AWS/GCP/Azure/PaaS), region/data residency, availability target, budget for infrastructure and observability? | High | Joint | Spec 12/13 | M12, M14; M0 partly |
| OQ-015 | **Security and compliance**: any required standards (SOC 2, GDPR, HIPAA, CCPA)? DPA requirements? Pentest budget? Malware scanning required? | High | Client | Spec 10 | M13 |
| OQ-016 | **Retention and deletion**: default retention for conversations, documents, audit logs, backups; deletion SLAs; legal hold? | High | Client | Spec 07 §5, spec 13 | M12 |
| OQ-017 | **Credentials and account access**: *owner answered by SOW §6: AdvoLevel owns all infrastructure and accounts.* Still open: when will delegated access be granted to each account? Product domain name? Which AdvoLevel GitHub org receives the repo (KI-006)? | Critical | Client | All environments | M0 (repo), M9, M11, M14 |
| OQ-018 | **Warranty, support and maintenance**: SOW §6 requires the **vendor to propose** defined defect-correction/warranty terms (starting point in spec 12 §10). Client to state the SLA expectation (business hours vs 24×7) and any post-launch maintenance needs. | High | Vendor (propose) / Client (accept) | Proposal | Contract signature |
| OQ-019 | Managed **auth provider** preference (Clerk/WorkOS/Auth0/other)? SSO/SAML required in V1? | High | Joint | DEC-006 | M1 start |
| OQ-020 | Is there **an existing codebase or design** elsewhere? (The repository was empty.) Any mandated stack? | Critical | Client | Spec 06 | M0 start |
| OQ-021 | **Approval model**: single vs multi-approver, approval chains, delegation, default expiry, self-approval allowed? | Medium | Client | BR-G-*, M8 | M8 |
| OQ-022 | Content Factory **content types** (posts, blogs, emails, ads, scripts, images?) | High | Client | M10 | M10 |
| OQ-023 | Languages / i18n needed in V1? | Low | Client | M3 | — |
| OQ-024 | Web-only responsive confirmed (no native apps)? | Low | Client | Scope | — |
| OQ-025 | *Answered by SOW §2/§6*: the vendor produces the editable Figma design system, prototype and screens, and AdvoLevel owns them. Still open: AdvoLevel brand assets (logo, fonts) and the list of prototype critical flows. | Medium | Client | Spec 05 §9, D1 | D1 |
| OQ-026 | Data residency requirements (e.g. EU/US only)? | Medium | Client | Hosting, AI provider choice | M0 (region) |
| OQ-027 | Provide the **remainder of `prompt.md`** after line 300 (the tracking-document list was cut off at `docs/RE…`). | Medium | Vendor/Client | Tracking docs | — |
| OQ-028 | Notification channels: in-app only, email, Slack/Teams? | Medium | Client | REQ-032 | M7 |
| OQ-029 | Transactional email provider and sending domain? | Medium | Joint | M1 | M1 |
| OQ-030 | Free trial? Length? Card required? | Medium | Client | WF-02, M11 | M11 |
| OQ-031 | **Boardroom semantics**: number of executives, rounds, human participants, real-time multi-user viewing, debate vs advisory format? | High | Client | Spec 09 §6 | M6 |
| OQ-032 | Definitions of **cases vs projects**: what is a "case" in the client's domain? | High | Client | Spec 07 §3.6 | M7 |
| OQ-033 | Platform admin scope: tenant impersonation/support access, entitlement overrides, refunds? | Medium | Client | BR-PA-02, M12 | M12 |
| OQ-034 | Target market and ideal customer profile (SMB, agencies, specific industries)? | Medium | Client | UX copy, onboarding | — |
| OQ-035 | Dark mode required in V1? | Low | Client | Spec 05 | — |

## 2. Risk register

| ID | Risk | Likelihood | Impact | Mitigation | Owner |
|---|---|---|---|---|---|
| RSK-001 | Building from an SOW summary leads to rework once the full SOW is read | High | High | Reconcile the SOW before M0 ends; keep the classification labels; start with foundation milestones that are scope-neutral | Joint |
| RSK-002 | Executive roles undefined → Brain built without real templates → quality tuning late | High | High | Build the engine template-agnostic; get OQ-003 answered before M5 mid-point | Client |
| RSK-003 | AI cost exceeds the plan revenue (especially boardrooms) | Medium | High | Metering, caps, model tiering, prompt caching, cost dashboards from M5 | Vendor |
| RSK-004 | Cross-tenant data leak | Low | Critical | RLS + app scoping + TI suite in CI from M2 | Vendor |
| RSK-005 | Governance bypass via a new code path | Low | Critical | ExecutionToken, import-linter, AB suite | Vendor |
| RSK-006 | Prompt injection through documents or CRM data triggers harmful actions | Medium | High | Untrusted-data wrapping, mandatory approvals for high-risk classes | Vendor |
| RSK-007 | RAG quality poor on client documents (scans, tables) | Medium | High | Early sample documents from the client; golden sets; OCR decision | Joint |
| RSK-008 | Google restricted-scope verification delays Drive folder sync | Medium | Medium | Start with `drive.file` + Picker; begin verification early if needed | Joint |
| RSK-009 | GHL marketplace approval / API constraints delay integration | Medium | Medium | Private integration token fallback for early testing; confirm the install model early | Client |
| RSK-010 | Third-party API details differ from our assumptions | Medium | Medium | Verify against current docs at the start of M9; contract tests with recorded fixtures | Vendor |
| RSK-011 | Credentials/accounts not provided on time | High | High | Ownership checklist (OQ-017) with needed-by milestone | Client |
| RSK-012 | 57 screens without approved designs → UI churn | Medium | Medium | Design system first; approve templates before screen batches | Joint |
| RSK-013 | Scope creep in the Content Factory (many destinations/types) | Medium | High | Lock V1 destinations; extra destinations as change requests | Joint |
| RSK-014 | Stripe webhook mishandling causes wrong entitlements | Low | High | Idempotent processing, fetch-latest strategy, BL suite | Vendor |
| RSK-015 | No version control today → lost work, no audit trail | High (until fixed) | Medium | Initialize git in M0 day 1 | Vendor |
| RSK-016 | Pgvector filtered-search recall degrades at scale | Low | Medium | Iterative scan / partial indexes; monitor; a dedicated vector DB is a later option | Vendor |
| RSK-019 | **Fixed-price commitment** (SOW §7) while many items are still NEEDS CLARIFICATION (integration operations, destination, screen list, executive templates) | High | High | Resolve the NC items in the inclusion matrix before signature; state assumptions and exclusions explicitly; handle changes by written change request | Vendor |
| RSK-020 | The repo sits under a personal GitHub account and is public, which conflicts with SOW §6 ownership and confidentiality ("Confidential contractor review") | High | Medium | Make it private now; transfer it to the AdvoLevel org (KI-005, KI-006) | Joint |
| RSK-018 | Customer-defined executives (large teams, poorly written custom mandates) increase AI cost and produce low-quality or off-role answers | Medium | Medium | Plan limits (`executives.max`, `boardroom.max_executives`), per-org AI credits, mandate validation and length limits, guided creation from templates, the generic custom-executive eval suite | Joint |
| RSK-017 | Unverified compliance expectations surface late | Medium | High | Answer OQ-015 early; no compliance claims in marketing | Client |
