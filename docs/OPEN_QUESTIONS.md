# Open Questions — Tracker

The authoritative descriptions are in `specifications/15-risks-and-open-questions.md`. This file tracks status and answers.
Update the **Status** and **Answer** columns as responses arrive, then update the affected specs and `DECISION_LOG.md`.

## Ask first (needed before or during M0–M1)
| ID | Short question | Sev | Owner | Blocks | Status | Answer |
|---|---|---|---|---|---|---|
| OQ-001 | Provide the signed SOW and annexes | Critical | Client | All | Partly answered | 2026-10-14: concise SOW reviewed (`SOW_INCLUSION_MATRIX.md`). Still need the master SOW, workflows and design inventory |
| OQ-002 | Existing screen inventory (SOW §2), to reconcile before signature | Critical | Client | Signature | Open | |
| OQ-038 | Commercial proposal: fixed price, milestone amounts, recurring third-party charges, staffing, warranty | Critical | Vendor | Signature | Open | |
| OQ-020 | Existing codebase/design or mandated stack? | Critical | Client | M0 start | Open | |
| OQ-017 | Account ownership + access (git, cloud, domain, Stripe, AI, dev apps, Sentry, email) | Critical | Client | M9, M11, M14 | Partly answered | 2026-10-14: git = `github.com/manishaj-code/Advolevel` (empty, public; private recommended). Long-term repo ownership/transfer and all other accounts still open |
| OQ-019 | Auth provider preference; SSO in V1? | High | Joint | M1 start | Partly answered | **Clerk** (user, 2026-10-15; DEC-006). SSO/SAML in V1 still open (Clerk enterprise SSO is a paid add-on); production Clerk instance must be AdvoLevel-owned (OQ-017) |
| OQ-013 | AI providers, budget, platform-paid vs BYO keys | Critical | Joint | M5 start | Open | |
| OQ-014 | Hosting, region, scale, infra budget | High | Joint | M0 (region), M12 | Open | |
| OQ-027 | Remainder of `prompt.md` after line 300 | Medium | Vendor | Tracking docs | Open | |

## Ask this week (needed for M3–M5)
| ID | Short question | Sev | Status | Answer |
|---|---|---|---|---|
| OQ-003 | The five standard executive templates (roles/mandates) | Critical | Open | |
| OQ-004 | Executive customization boundaries | Medium | Partly answered | 2026-10-14: customers decide how many executives they have and configure, add, disable and delete them (DEC-018). Open: template mandate replace vs extend; per-executive model choice |
| OQ-036 | `executives.max` per plan (any unlimited?), `boardroom.max_executives`, custom executives on which plans | High | Open | |
| OQ-025 | Figma: brand assets and the critical-flow list | Medium | Partly answered | SOW: the vendor produces the Figma files and AdvoLevel owns them |
| OQ-037 | Public website pages, copy, CMS | Medium | Open | |
| OQ-039 | Transcription volume, languages; transcripts in RAG? | Medium | Open | |
| OQ-005 | File formats and limits | High | Open | |
| OQ-006 | User/org limits and scale | High | Open | |
| OQ-029 | Email provider and sending domain | Medium | Open | Deferred by user 2026-10-15: SMTP to a local Mailpit sink behind an `EmailSender` interface until the domain exists (DEC-027) |
| OQ-026 | Data residency | Medium | Open | |

## Ask before the feature milestones (M6–M12)
| ID | Short question | Sev | Status | Answer |
|---|---|---|---|---|
| OQ-031 | Boardroom semantics | High | Open | |
| OQ-032 | Cases vs projects definitions | High | Open | |
| OQ-021 | Approval model details | Medium | Open | |
| OQ-007 | ClickUp operations | High | Open | |
| OQ-008 | GoHighLevel install model and operations | High | Open | |
| OQ-009 | Dropbox access mode | Medium | Open | |
| OQ-010 | Google Drive scope approach | High | Open | |
| OQ-011 | Plans, prices, trials, caps | Critical | Open | |
| OQ-030 | Free trial policy | Medium | Open | |
| OQ-012 | Publishing destinations | Critical | Open | |
| OQ-022 | Content types | High | Open | |
| OQ-028 | Notification channels | Medium | Open | |
| OQ-015 | Compliance requirements, pentest | High | Open | |
| OQ-016 | Retention and deletion | High | Open | |
| OQ-018 | Warranty terms (the vendor proposes them, per SOW §6), SLA | High | Open | Starting point in spec 12 §10 |
| OQ-033 | Platform admin scope | Medium | Open | |

## Low priority
| ID | Short question | Status | Answer |
|---|---|---|---|
| OQ-023 | i18n | Open | |
| OQ-024 | Web-only confirmed | Open | |
| OQ-034 | Target market / ICP | Open | |
| OQ-035 | Dark mode in V1 | Open | |
