# Known Issues

There is no application code yet. These are planning- and process-level issues found on 2026-10-14.

| ID | Issue | Impact | Workaround / next step | Status |
|---|---|---|---|---|
| KI-001 | The concise SOW (`d:\POC\AdvoLevel_Concise_Integrated_SOW.pdf`) was reviewed on 2026-10-14 and the specs were updated (`SOW_INCLUSION_MATRIX.md`). The **detailed master SOW, workflows and existing screen inventory** it references are still not available. | Remaining conflicts or omissions are possible | Request them (OQ-001, OQ-002); reconcile in writing before award | Partly resolved |
| KI-002 | `prompt.md` is truncated at line 300 (`docs/RE…`). One or more requested tracking documents are unknown. | Possible missing deliverable(s) | Created `docs/README.md` as an index; obtain the full brief (OQ-027) | Open |
| KI-003 | The local project directory is not a git repository. The remote `github.com/manishaj-code/Advolevel` exists but is empty. | No history, no review, risk of loss | M0 day 1: `git init`, add the remote, push `docs/` to `main`, enable branch protection | Open |
| KI-006 | The repo `manishaj-code/Advolevel` is under a personal account. SOW §6 requires the source repository to be AdvoLevel's | Ownership and handover non-compliance | Transfer it to an AdvoLevel GitHub organization (GitHub Settings → Transfer), or create the repo there and push | Open |
| KI-005 | The GitHub repository `manishaj-code/Advolevel` is **public** | Specs and code for a commercial product would be publicly visible | Change visibility to private before the first push (repo Settings → Danger Zone), unless the client decides otherwise | Open |
| KI-004 | No credentials or accounts exist for any service | Blocks environment setup beyond local | Ownership checklist OQ-017 | Open |
