# 09 — Executive Brain, AI and RAG

| Field | Value |
|---|---|
| Status | DRAFT v0.1 — design PROPOSED |
| Date | 2026-10-14 |
| Important | **The customer decides how many executives they have** (BR-E-01, DEC-018). The platform ships five standard templates, whose roles are NEEDS CLARIFICATION (OQ-003). This document specifies the generic engine, which works for any number of executives. |

## 1. Concept
The **Executive Brain** is one reusable orchestration engine. An "executive" is *data*: an optional platform template plus a per-org configuration. It is not code. Customers can create as many executives as their plan's `executives.max` allows, either from a standard template or from scratch. Adding, changing or removing an executive never needs engine changes or a deployment.

```
Executive = Platform safety rules (fixed)
          + [optional] Standard template defaults
          + Customer config version (role, mandate, persona, focus, instructions)
          + Tools (registry ∩ enabled ∩ governance) + Knowledge scope + Memory
```

## 2. Executive definition contract
| Field | Description | Who sets it |
|---|---|---|
| `safety_rules` | Non-negotiable platform rules (no fabricated sources, governance obedience, untrusted-data handling, etc.) | Platform only. Always prepended, never editable |
| `role_title` | e.g. "Chief Marketing Officer" or any customer-defined role | Template default or customer |
| `mandate` | Role responsibilities, reasoning style, boundaries | Template default or customer. For template-based executives, whether the customer can replace the mandate or only extend it is OQ-004 |
| `display_name`, `avatar`, `accent` | Persona identity (unique name per org) | Customer |
| `tone` | e.g. formal ↔ conversational, concise ↔ detailed | Customer (bounded options) |
| `focus_areas` | Priorities within the role | Customer |
| `custom_instructions` | Free text in a delimited block, with a length limit (PROPOSED 4,000 characters) | Customer |
| `enabled_tools` | Chosen from the tool registry; templates suggest defaults | Customer, limited by governance |
| `knowledge_scope` | Collections | Customer |
| `model_tier` | standard / premium | Customer, if the plan allows |

Prompt-assembly order: safety rules → mandate/role → persona → custom instructions (delimited; cannot override earlier sections). Custom executives are validated on save: a role title and mandate are required, and the length limits apply.

## 3. Orchestration engine

### 3.1 Run pipeline
1. **Admission**: check entitlements, AI credits, rate limits, and that the executive is enabled. Create an `ai_run`.
2. **Context assembly** (token-budgeted, in priority order):
   1. Platform safety rules + executive role/mandate (stable per config version → prompt-cache prefix)
   2. Org DNA digest (stable per DNA version → cacheable)
   3. Executive config (persona, focus, custom instructions)
   4. Case context (if any): case summary, open tasks, recent decisions
   5. Retrieved evidence (RAG §5) with source IDs
   6. Conversation memory: a rolling summary of older turns + the last N turns verbatim
   7. The user message
3. **Model call** via the provider abstraction (§4), with tool definitions from the registry filtered by the executive config ∩ governance.
4. **Tool loop**: for each tool call → validate the args against the schema → `governance.evaluate()` → Allow: execute and return the result; Require Approval: create an `action_request`, return a "pending approval" result to the model, and tell the user; Deny: return the reason. A maximum number of tool iterations per run is enforced (PROPOSED: 8).
5. **Post-processing**: extract citations, validate that every cited source ID was actually provided (strip invented ones), detect structured proposals (tasks/decisions), persist the message, record usage, end the trace span.
6. **Streaming**: tokens and events go to SSE (spec 08).

### 3.2 Memory
- **Conversation memory**: persisted messages. A rolling summary is regenerated every K turns (cheap model).
- **Executive office memory** (PROPOSED): pinned notes per executive per org, which the user can edit. The executive may *suggest* adding a note, but not write one silently.
- **Contextual case memory** (CONFIRMED, SOW §3): each case has a persisted `case_memory`, a structured summary (key facts, open questions, constraints, stakeholders, decisions so far, next steps). A cheap model updates it after significant events (a boardroom closes, a decision is accepted, a task completes, or a long conversation linked to the case ends). Every update is a version with a source link. The case owner can edit it. It is injected into every run that has the case attached (context step 4) and is searchable.
- **Organizational memory**: Org DNA + documents + decisions log (decisions are retrievable as evidence).
- No cross-tenant memory, ever. No training on customer data.

### 3.3 Proposals (task and decision follow-through)
Executives emit structured proposals through dedicated tools (`propose_task`, `propose_decision`, `propose_case`). These create `proposals` rows (status `pending`), never final records. The user confirms them in the UI (BR-W-04, FR-07).

Executive-owned tasks get a scheduled **follow-through job**: the executive reviews the task state and posts an update or question to the linked conversation, or proposes the next action through governance. Frequency PROPOSED: daily, configurable.

## 4. Model-provider abstraction
```python
# interface sketch (documentation only — not implementation)
class LLMProvider(Protocol):
    def stream(self, req: ChatRequest) -> AsyncIterator[ChatEvent]: ...
    def count_tokens(self, req: ChatRequest) -> int: ...
class EmbeddingProvider(Protocol):
    def embed(self, texts: list[str], kind: Literal["document","query"]) -> list[list[float]]: ...
```
- A normalized request/response model (messages, tools, tool calls, usage, stop reasons).
- Adapters: Anthropic (default), OpenAI-compatible (secondary).
- Routing table: `(purpose, model_tier) → provider/model`. Purposes: `executive`, `boardroom_turn`, `synthesis`, `summary`, `router`, `content`, `dna_draft`.
- Use prompt caching for stable prefixes (safety + template + DNA).
- Pricing table per model, to compute `cost_micro_usd` per run.

## 5. Tool registry
| Field | Description |
|---|---|
| `key` | e.g. `clickup.create_task` |
| `integration` | provider or `internal` |
| `action_class` | `read`, `write`, `external_comm`, `publish`, `financial` |
| `input_schema` | JSON Schema (also passed to the model) |
| `risk_level` | low / medium / high |
| `idempotent` | bool |
| `handler` | Calls `governance.execute_action` for anything other than internal reads |

Internal tools (PROPOSED): `search_knowledge`, `get_case_context`, `list_tasks`, `propose_task`, `propose_decision`, `propose_case`, `draft_content`, `ask_executive` (boardroom only).

## 6. Boardroom coordination
- **Moderator**: an orchestrator role (not one of the org's executives) that plans the turn order based on the agenda and relevance, and later synthesizes.
- **Turn protocol**: round r = 1…R. Each selected executive receives: the agenda, a shared session context (a summary of prior turns + the full last turn), its own persona and its own knowledge scope. It must address the previous points (agree, disagree or add) in a bounded length.
- **Human interjection**: inserted as a turn. The moderator may re-plan.
- **Synthesis**: summary, consensus, dissent (attributed), open questions, proposed decisions and tasks (as proposals).
- **Concurrency**: one generating turn at a time per session (a distributed lock). Turns can run in parallel in a "quick poll" mode (V1.1).
- **Cost guard**: estimate before start; stop if the budget is exceeded.
- **Team size**: an org may have many executives, but a session is capped by `boardroom.max_executives` (PROPOSED default 5) to keep cost and quality under control. The moderator can suggest relevant executives from the team based on the agenda (using their role titles and mandates).

## 7. RAG pipeline

### 7.1 Parsing
| Format | Parser (PROPOSED) | Status |
|---|---|---|
| PDF (text) | PyMuPDF / pdfplumber | Assumed in scope |
| PDF (scanned) | OCR (Tesseract or a cloud OCR service) | NEEDS CLARIFICATION (OQ-005) |
| DOCX | python-docx / unstructured | Assumed |
| PPTX, XLSX/CSV | python-pptx, openpyxl/pandas (tables → markdown) | NEEDS CLARIFICATION |
| TXT, MD, HTML | native / readability | Assumed |
| Google Docs/Sheets/Slides | Drive export to DOCX/CSV/PDF | Assumed via Drive |
| Audio, video | Third-party speech-to-text API → timestamped transcript → text pipeline | **IN SCOPE for the Content Factory** (SOW §4: "transcription when applicable"). Whether transcripts are also added to the RAG knowledge base is NEEDS CLARIFICATION (OQ-005) |
| Images | — | ASSUMED OUT OF SCOPE for RAG V1 (no OCR of photos); images may be attached to content items as assets |
File-size limit PROPOSED: 50 MB per file, 500 pages. NEEDS CLARIFICATION (OQ-005).

### 7.2 Chunking
- Structure-aware: split on headings/sections first, then by tokens.
- Target 500–800 tokens, 10–15% overlap. Tables kept whole where possible.
- Each chunk stores `heading_path`, page range, and a document title prefix (contextual header) to improve retrieval.

### 7.3 Embeddings
- One embedding model per environment, recorded in each chunk (`embedding_model`). A model change means a background re-embed job.
- Batched calls with retry. Content-hash dedupe.

### 7.4 Retrieval
1. Query rewriting (cheap model) using the conversation context. Optional, behind a flag.
2. **Hybrid search**: vector (HNSW cosine) top-k=30 + keyword (tsvector) top-k=30 → reciprocal rank fusion.
3. **Mandatory filters**: `organization_id = ctx.org_id` (+ RLS), `deleted_at IS NULL`, `status='ready'`, `collection_id ∈ executive.knowledge_scope`, optionally `case` documents.
4. Optional reranking (a reranker model) → top 6–10 chunks within the token budget.
5. Each chunk is passed with a stable source ID: `[S1] {doc title} — p.{pages}`.

### 7.5 Source references
- The model is instructed to cite `[S#]` for factual claims drawn from documents.
- Post-processing maps `[S#]` → `{document_id, chunk_id, page_from, page_to, title}`. Unknown IDs are removed and a metric is incremented.
- The UI shows citation chips that open a source preview (S-13 citations panel).

### 7.6 Insufficient-evidence behaviour
- If the retrieval score is below a threshold, or no chunks pass the filters, the context includes an `EVIDENCE: NONE` marker.
- Required behaviour: the executive states clearly that the organization's documents do not cover the question. It may offer general expertise, **labelled as general knowledge, not organizational fact**, and suggests which document or DNA section would help.
- This is verified by the golden test set (spec 11 §5).

### 7.7 Deletion
Document delete → status `deleting` (excluded from retrieval immediately) → the job deletes chunks and embeddings, then the stored file → audit event. Citations in old messages remain as text but are marked "source deleted".

### 7.8 Tenant isolation in AI
- Retrieval always passes through a repository that requires `TenantContext`. RLS acts as a backstop.
- Prompt caches are keyed per org for any segment containing tenant data.
- No shared vector namespaces. No cross-tenant few-shot examples.
- Provider data-retention settings: use zero-retention/no-training options where available (OQ-015).

## 8. Evaluation (quality gates)
- Golden question sets for each standard template, plus a generic suite that runs against custom executives (role adherence, staying within the mandate, safety rules not overridable by custom instructions), per demo org: grounding accuracy, citation precision, refusal correctness on insufficient evidence, tool-choice correctness.
- Boardroom rubric: each executive contributes distinctly, the synthesis is faithful.
- Run in CI nightly (with a cost cap) and before any prompt or model change.

## 9. Prompt-injection and safety
- Retrieved documents and integration data are wrapped as **untrusted data** in delimited blocks. Instructions inside them are not followed.
- Tools are never executed only because a document says so. Governance still applies, and high-risk classes always require approval.
- Output filtering: no secrets or credentials in responses (redaction scan).
- Customer `custom_instructions` cannot override the safety rules (they are placed after the rules and wrapped in a delimited block).
