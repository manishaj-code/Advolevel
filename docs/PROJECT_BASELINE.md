# AdvoLevel — Project Baseline

| Field | Value |
|---|---|
| Document status | DRAFT v0.1 — planning session |
| Date | 2026-10-14 |
| Inspected path | `D:\Projects\Advolevel` |
| Inspection method | Recursive directory listing; read of every file present |

## 1. Inspection result (factual)

The repository was inspected on 2026-10-14. **It contains no application code.**

| Item inspected | Finding |
|---|---|
| Repository structure | One file: `prompt.md` (12,365 bytes) — the planning brief for this session. No other files or folders existed before `docs/` was created. |
| Git branch / working tree | The local folder is **not a git repository** (no `.git` directory). |
| Remote repository | `https://github.com/manishaj-code/Advolevel` (named by the user on 2026-10-14). Checked read-only with `git ls-remote` and the GitHub API: **empty**, with no branches and no commits, size 0. Default branch `main`. Created 2026-10-14. **Visibility: PUBLIC.** |
| Frontend framework | None present. |
| Backend framework | None present. |
| Dependencies | No `package.json`, `pyproject.toml`, `requirements.txt` or lockfiles. |
| Modules and routes | None. |
| Database models / migrations | None. |
| Authentication / permissions | None. |
| AI workflows / RAG | None. |
| Integration adapters | None. |
| Logging / monitoring | None. |
| Tests / CI/CD | No tests, no CI configuration (`.github/`, etc.). |
| Environment configuration | No `.env`, `.env.example` or config files. No secrets were found, so none were exposed. |
| Deployment setup | No Dockerfiles, IaC, or platform config. |
| Client SOW | Not in the repository. The **concise integrated SOW** was supplied separately (`d:\POC\AdvoLevel_Concise_Integrated_SOW.pdf`) and reviewed on 2026-10-14 (see `SOW_INCLUSION_MATRIX.md`). The detailed master SOW, workflows and design inventory it references are still not available. |
| Planning brief | `prompt.md` is **truncated at line 300**, mid-way through the list of tracking documents (`docs/RE…`). Content after that point is unknown. |

## 2. Existing architecture
None. This is a greenfield project. All architecture in `docs/specifications/06-system-architecture.md` is **PROPOSED**.

## 3. Current modules
None.

## 4. Working functionality
None.

## 5. Incomplete functionality
Everything in scope is unimplemented. See `docs/IMPLEMENTATION_STATUS.md`.

## 6. Known defects
None (no code). Documentation-level issues are recorded in `docs/KNOWN_ISSUES.md`:
- KI-001: SOW document not available.
- KI-002: Planning brief truncated.
- KI-003: No version control.

## 7. Technical debt
None in code. Process debt (no VCS, no CI) is recorded in `docs/TECHNICAL_DEBT.md`.

## 8. Existing tests and actual results
No tests exist. **No tests were run.** Result: N/A.

## 9. Missing dependencies and credentials
Everything is missing. Required before or during implementation (see `15-risks-and-open-questions.md`, OQ-17):

| Needed for | Credential / account | Owner (proposed) |
|---|---|---|
| Source control | GitHub repo `manishaj-code/Advolevel` exists (empty, public) | Owned by a personal GitHub account. Long-term ownership and transfer to the client is NEEDS CLARIFICATION (OQ-017) |
| Hosting | Cloud/PaaS account | NEEDS CLARIFICATION |
| Database | Managed PostgreSQL with pgvector | NEEDS CLARIFICATION |
| Auth | Managed auth provider tenant | NEEDS CLARIFICATION |
| Object storage | S3-compatible bucket | NEEDS CLARIFICATION |
| AI | LLM provider API key(s); embeddings provider key | Client (billing) — NEEDS CLARIFICATION |
| Billing | Stripe account (test + live) | Client |
| Integrations | ClickUp, GoHighLevel, Dropbox, Google Cloud (Drive OAuth app) developer apps | Client — NEEDS CLARIFICATION |
| Monitoring | Sentry org, metrics/logs backend | NEEDS CLARIFICATION |
| Email | Transactional email provider | NEEDS CLARIFICATION |
| Design | Figma workspace | NEEDS CLARIFICATION |

## 10. Security concerns
- **The GitHub repository is public.** Anything pushed (specs, architecture, governance design, and later the code) is visible to everyone. For a commercial SaaS product, **make the repository private before the first push** unless the client explicitly wants it open (KI-005).
- The local folder isn't yet connected to the remote, so there's no change history. Connect it before writing any code.
- No secret-management approach exists yet. Define one before any credentials are issued (see spec 10 and 12).
- Integration OAuth tokens and AI keys will be high-value secrets. The encryption design must be approved before the integration milestones.

## 11. Recommendations (for tomorrow)
1. **Obtain the official SOW** and reconcile it against these specifications. Update every item marked NEEDS CLARIFICATION or ASSUMED.
2. **Obtain the remainder of `prompt.md`** (after line 300) and add any missing tracking documents.
3. Make `manishaj-code/Advolevel` private, initialize the local folder as a git repository, connect it to that remote, set up branch protection on `main`, and push `docs/` as the first commit (Milestone M0 in `14-development-roadmap.md`).
4. Get approval for the PROPOSED stack decisions in `docs/DECISION_LOG.md` (DEC-001 … DEC-015) before M0 begins.
5. Get answers to the blocking open questions in `docs/OPEN_QUESTIONS.md` that M0–M2 depend on.
