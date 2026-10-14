# Requirements Traceability Matrix

Maps each requirement → classification → specs → screens → workflows → milestone → verifying tests.
Status values: Not started · In progress · Done · Verified. All are **Not started** as of 2026-10-14.

| Req | Requirement | Class | Specs | Screens | Workflows | Milestone | Tests | Status |
|---|---|---|---|---|---|---|---|---|
| REQ-001 | Multi-tenant SaaS | CONFIRMED | 02, 06, 07, 10 | all | WF-02 | M1, M2 | TI-01…11 | Not started |
| REQ-002 | ~57 core screens | CONFIRMED (list NC: OQ-002) | 04, 05 | S-01…S-57 | — | M3–M12 | E2E, axe | Not started |
| REQ-003 | Five configurable specialist executives (as standard templates) | CONFIRMED (roles NC: OQ-003) | 02, 09 | S-12, S-15–17 | WF-07 | M5 | AI-01…07, golden set | Not started |
| REQ-003a | Customer decides executive count; create/configure/enable/disable/delete within `executives.max` | CONFIRMED (user, DEC-018) | 02, 03, 04, 07, 08, 09 | S-06, S-12, S-15, S-56 | WF-02, WF-07 | M5, M11 | AT-07-1…7, AZ-04, AZ-05 | Not started |
| REQ-004 | Reusable Executive Brain | CONFIRMED | 06, 09 | S-13 | WF-06 | M5 | AI-01…04 | Not started |
| REQ-005 | Persistent Executive Offices | CONFIRMED | 07, 09 | S-13, S-14 | WF-06 | M5 | WF-06 AT | Not started |
| REQ-006 | Multi-executive Boardrooms | CONFIRMED | 09 §6 | S-18–21 | WF-08 | M6 | AI-05, WF-08 AT | Not started |
| REQ-007 | Organizational DNA | CONFIRMED | 07, 09 | S-08, S-22, S-23 | WF-04 | M4 | WF-04 AT | Not started |
| REQ-008 | Tenant-isolated RAG | CONFIRMED | 09 §7, 10 | S-24–27 | WF-05 | M4 | RAG-01…08, TI-05 | Not started |
| REQ-009 | Cases | CONFIRMED | 07 | S-28, S-29 | WF-09 | M7 | WF-09 AT | Not started |
| REQ-010 | Projects | CONFIRMED | 07 | S-30, S-31 | WF-09 | M7 | WF-09 AT | Not started |
| REQ-011 | Tasks | CONFIRMED | 07 | S-32, S-33 | WF-10 | M7 | WF-10 AT | Not started |
| REQ-012 | Decisions | CONFIRMED | 07 | S-34, S-35 | WF-11 | M7 | WF-11 AT | Not started |
| REQ-013 | Governance policies | CONFIRMED | 10 §8 | S-38, S-39 | WF-12 | M8 | AB-01…12 | Not started |
| REQ-014 | Human approvals | CONFIRMED | 10 §8 | S-36, S-37 | WF-12 | M8 | AB-01…12 | Not started |
| REQ-015 | ClickUp | CONFIRMED (ops NC) | 08 §4.1 | S-45–47 | WF-13 | M9 | §7 suite | Not started |
| REQ-016 | GoHighLevel | CONFIRMED (ops NC) | 08 §4.2 | S-45–47 | WF-13 | M9 | §7 suite | Not started |
| REQ-017 | Dropbox | CONFIRMED (ops NC) | 08 §4.3 | S-27, S-45–47 | WF-05, WF-13 | M9 | §7 suite | Not started |
| REQ-018 | Google Drive | CONFIRMED (ops NC) | 08 §4.4 | S-27, S-45–47 | WF-05, WF-13 | M9 | §7 suite | Not started |
| REQ-019 | Stripe | CONFIRMED | 08 §4.5 | S-07, S-51 | WF-15 | M11 | BL-01…08 | Not started |
| REQ-020 | Content Factory | CONFIRMED (destinations NC) | 08 §4.7 | S-41–44 | WF-14 | M10 | WF-14 AT | Not started |
| REQ-021 | Subscription billing | CONFIRMED (plans NC) | 02, 08 | S-07, S-51 | WF-15 | M11 | BL-01…08 | Not started |
| REQ-022 | Entitlements | CONFIRMED | 02 | S-52, S-56 | WF-15 | M11 | BL-06, BL-07 | Not started |
| REQ-023 | Security | CONFIRMED | 10 | — | — | M2, M13 | AZ, AB, SD suites | Not started |
| REQ-024 | Testing | CONFIRMED | 11 | — | — | all | CI gates | Not started |
| REQ-025 | Monitoring | CONFIRMED | 13 | S-57 | WF-16 | M0, M12 | MON-01…10 | Not started |
| REQ-026 | Deployment | CONFIRMED | 12 | — | — | M0, M14 | Release checklist | Not started |
| REQ-027 | Handover | CONFIRMED | 12 §10 | — | — | M14 | Handover checklist | Not started |
| REQ-028 | Concept B design | CONFIRMED (brief) | 05 | all | — | M3 | axe, visual review | Not started |
| REQ-029 | Audit log | PROPOSED | 10 §7 | S-40 | — | M2 | Audit chain test | Not started |
| REQ-030 | Configurable AI providers | PROPOSED | 09 §4 | S-15 | — | M5 | AI-01 | Not started |
| REQ-031 | Citations + insufficient evidence | PROPOSED | 09 §7.5–7.6 | S-13 | WF-06 | M4, M5 | RAG-05, RAG-06 | Not started |
| REQ-032 | Notifications | PROPOSED | 04 | S-11 | — | M3, M7 | — | Not started |
| REQ-033 | Platform admin console | PROPOSED | 02, 04 | S-54–57 | WF-16, 17 | M12 | MON-07, 08 | Not started |
| REQ-034 | Usage metering | PROPOSED | 07, 13 | S-52 | — | M5, M11 | AI-04 | Not started |
| REQ-035 | Team invitations | PROPOSED | 02, 03 | S-05, S-49 | WF-03 | M1 | WF-03 AT | Not started |
| REQ-036 | MFA | PROPOSED | 10 §1 | S-53 | — | M1 | Manual + E2E | Not started |
| REQ-005a | Searchable office/boardroom history | CONFIRMED (SOW §3) | 04 | S-10, S-14, S-18 | — | M5, M6 | Search E2E | Not started |
| REQ-008a | Contextual case memory | CONFIRMED (SOW §3) | 07, 09 §3.2 | S-29 | WF-09 | M7 | AT-09-2 | Not started |
| REQ-008b | Retention/deletion controls | CONFIRMED (SOW §3) | 07 §3.11 | S-48 | — | M4, M12 | Purge job tests | Not started |
| REQ-020a | Approved actions actually execute, with retries and failure reporting | CONFIRMED (SOW §4) | 10 §8, 13 §11 | S-37, S-47 | WF-12 | M8, M9 | AB suite, §8 | Not started |
| REQ-027a | Deploy to AdvoLevel-controlled accounts | CONFIRMED (SOW §6) | 12 §10 | — | — | M14 | Handover checklist | Not started |
| REQ-027b | IP to AdvoLevel, licence disclosure, warranty terms | CONFIRMED (SOW §6) | 12 §10 | — | — | M14 | SBOM, signed terms | Not started |
| REQ-028a | Editable Figma design system + clickable prototype | CONFIRMED (SOW §2) | 05 §9 | all | — | D1 | Client sign-off | Not started |
| REQ-028b | Public website screens | CONFIRMED (SOW §2) | 04 | S-W1…S-W5 | — | M3 | Lighthouse, E2E | Not started |
| REQ-028c | Responsive + loading/empty/error/permission/approval states | CONFIRMED (SOW §2) | 04 §0 | all | — | M3+ | axe, E2E-10 | Not started |
| NFR-01…11 | Non-functional | PROPOSED | 01 §7 | — | — | M2, M13 | Perf, TI, MON | Not started |
