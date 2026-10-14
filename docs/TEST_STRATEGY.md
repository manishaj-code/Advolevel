# Test Strategy (summary)

The full specification is in `specifications/11-testing-and-acceptance.md`. This page is the one-page view for the team.

## Principles
1. **Isolation and governance are tested like security features**: their suites are blocking CI gates from the milestone they land in (M2 and M8) onward.
2. **Test pyramid**: many fast unit tests, real-database integration tests (Testcontainers, no DB mocks for repositories), a focused set of Playwright E2E journeys.
3. **AI is tested with evaluation sets, not only assertions**: golden questions with measurable thresholds, run nightly with a cost cap and before any prompt/model change.
4. **External providers**: recorded fixtures in CI; real sandbox smoke tests nightly; never production accounts in tests.
5. **Every bug fix adds a regression test.**

## Blocking suites
| Suite | IDs | Gate from |
|---|---|---|
| Tenant isolation | TI-01…TI-11 | M2 |
| Authorization matrix | AZ-01…AZ-03 | M1 |
| Approval bypass | AB-01…AB-12 | M8 |
| Sensitive-data leakage | SD-01…SD-05 | M5 (logging), full at M13 |
| Billing | BL-01…BL-08 | M11 |
| RAG | RAG-01…RAG-08 | M4 |
| Monitoring | MON-01…MON-10 | M12 (MON-01 from M0) |

## Environments for testing
- **CI**: ephemeral Postgres+pgvector and Redis containers; mocked AI via recorded fixtures plus a deterministic fake provider.
- **Staging**: E2E, sandbox integrations, Stripe test mode, real AI providers with a low budget cap.

## Test data
Seed script with two demo orgs (A and B), users for every role, sample documents (PDF, DOCX, scanned PDF if OCR is in scope), golden Q&A per executive. **No real client data in CI.** Client sample documents are used only in staging with the client's consent.

## Ownership
Developers write unit/integration/API tests with each PR. The QA lead owns E2E, exploratory, accessibility and the release checklist. The AI engineer owns the eval sets and thresholds.
