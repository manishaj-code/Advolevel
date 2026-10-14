# Technical Debt Register

No code exists, so there is no code-level debt. This register is ready for use from M0 onward.

## How to record debt
Each entry gives: what was compromised, why, the risk if left, the payoff plan, and the target milestone. Debt that touches tenant isolation, governance or secrets is never "accepted". It must be scheduled.

| ID | Area | Description | Reason incurred | Risk | Payoff plan | Target | Status |
|---|---|---|---|---|---|---|---|
| TD-000 | Process | Local folder not under version control (the remote `manishaj-code/Advolevel` exists but is empty); no CI | Greenfield | Lost work, no review trail | M0 day 1: connect to the remote, push, add CI | M0 | Open |

## Planned / anticipated debt (accepted deliberately in the plan — PROPOSED)
| ID | Description | Why acceptable for V1 | Revisit trigger |
|---|---|---|---|
| TD-P01 | A single Postgres for OLTP + vectors | Simplicity; adequate at the assumed scale | > ~5M chunks or p95 retrieval > 300 ms |
| TD-P02 | Fixed governance condition set (no general expression language) | Reduces bypass/complexity risk | Client needs custom conditions |
| TD-P03 | Sequential boardroom turns only | Predictable cost and UX | Latency complaints |
| TD-P04 | `usage_events` not partitioned | Low volume initially | Table > 50M rows |
| TD-P05 | Light content area + dark sidebar only (no full dark theme) | Pending OQ-035 | Client request |
