# ADVOLEVEL — SPECIFICATION AND DEVELOPMENT PLANNING ONLY

## 1. Objective

Act as a senior SaaS product architect, business analyst, technical architect, UI/UX architect, AI engineer, security architect, DevOps architect and QA lead.

We are planning **AdvoLevel**, a production-ready, multi-tenant AI Executive Operating System for businesses.

The goal of this session is strictly to:

1. Understand the client requirements.
2. Inspect the existing repository without changing application code.
3. Create all required product and technical specification documents.
4. Design the proposed architecture and workflows.
5. Prepare the development roadmap and milestone plan.
6. Identify missing information, risks, dependencies and technical decisions.
7. Prepare a clear implementation plan that can be started tomorrow.

**Do not start implementation today. We will begin coding tomorrow after reviewing the specifications and plan.**

## 2. Absolute no-coding rule

During this session, do not:

- Write application code.
- Modify existing frontend or backend source files.
- Create React components or API endpoints.
- Implement database models or migrations.
- Install dependencies.
- Run scaffolding commands.
- Initialize or modify application infrastructure.
- Configure external services.
- Deploy anything.
- Modify production data or credentials.
- Refactor or fix existing application code.

You may read source files, inspect repository structure, review existing tests and analyze configuration without exposing secret values.

You may create and edit **Markdown documentation files inside `docs/` only**. If documentation creation would overwrite existing work, preserve the existing document and create a clearly named planning version instead.

If a task cannot be completed without changing application code or accessing an external account, document the limitation and continue with planning.

## 3. Understand the client's SOW

Read the supplied AdvoLevel Statement of Work and any additional specifications already available in the repository.

Treat approved client documents as the source of truth.

The SOW describes:
- A multi-tenant SaaS application
- Approximately 57 core screens
- Five functioning configurable specialist executives
- A reusable Executive Brain
- Persistent Executive Offices
- Multi-executive Boardrooms
- Organizational DNA and tenant-isolated RAG
- Cases, projects, tasks and decisions
- Governance and human approvals
- ClickUp, GoHighLevel, Dropbox, Google Drive and Stripe integrations
- A Content Factory
- Subscription billing and entitlements
- Security, testing, monitoring, deployment and handover

Do not invent missing client decisions.

Classify every important requirement as:
- CONFIRMED
- PROPOSED
- ASSUMED
- NEEDS CLARIFICATION
- OUT OF SCOPE

The concise SOW does not establish the complete official screen inventory, exact executive identities, every integration operation or the agreed publishing destinations. Track these as unresolved until confirmed.

## 4. Inspect the existing project

Read the repository and document its current state.

Inspect:
- Repository structure
- Git branch and working-tree status
- Frontend and backend frameworks
- Dependencies
- Existing modules and routes
- Database models and migrations
- Authentication and permissions
- AI workflows and RAG implementation
- Integration adapters
- Logging and monitoring
- Tests and CI/CD
- Environment configuration
- Deployment setup
- Known errors and technical debt

Do not print secret values.

Do not fix any discovered problems today. Record them for tomorrow's implementation planning.

Create `docs/PROJECT_BASELINE.md` containing:
- Existing architecture
- Current modules
- Working functionality
- Incomplete functionality
- Known defects
- Technical debt
- Existing tests and actual results
- Missing dependencies and credentials
- Security concerns
- Recommendations

If the repository is empty or cannot be accessed, document that fact instead of pretending an inspection occurred.

## 5. Create the 15 specification documents

Create `docs/specifications/` and prepare these documents.

### 01. Product Requirements Document
`docs/specifications/01-product-requirements.md`

Include product vision, target users, business problems, features, commercial V1 scope, exclusions, functional requirements, non-functional requirements, success metrics and acceptance criteria.

### 02. Business Rules and User Roles
`docs/specifications/02-business-rules-and-roles.md`

Define platform administrators, organization administrators, organization members, executive configuration permissions, boardroom participation, task ownership, approval authority, subscription entitlements and role-based permissions.

### 03. User Journeys and Workflows
`docs/specifications/03-user-journeys-and-workflows.md`

Document registration, onboarding, team invitations, Organizational DNA, document ingestion, AI conversations, Executive Offices, Boardrooms, cases, tasks, decisions, approvals, content workflows, integrations, billing, monitoring and recovery.

For each workflow specify actors, triggers, prerequisites, steps, permissions, backend operations, expected results, failure handling and acceptance tests.

### 04. Screen Inventory and UX Specification
`docs/specifications/04-screen-inventory-and-ux.md`

Create a provisional inventory of approximately 57 screens.

For each screen document its purpose, roles, components, data, actions, API dependencies, loading/empty/error/permission states, responsive behavior and acceptance criteria.

Mark the inventory as provisional until the client confirms the official list.

### 05. Design System
`docs/specifications/05-design-system.md`

Use the requested premium executive Concept B aesthetic: deep navy, warm neutrals and restrained gold.

Document typography, colors, spacing, layout, shared components, navigation, forms, tables, cards, notifications, accessibility and responsive behavior.

Document the Figma deliverables required. Do not claim that Figma assets have been created if they have not.

### 06. System Architecture
`docs/specifications/06-system-architecture.md`

Evaluate the existing stack before recommending technology.

Consider Next.js/React/TypeScript, FastAPI, PostgreSQL/pgvector, managed authentication, object storage, background workers, Stripe and configurable AI providers.

Document architecture diagrams, services, data flows, boundaries, AI orchestration, RAG, integrations, deployment, observability, security and cost considerations.

Prefer a modular architecture and avoid unnecessary complexity.

### 07. Database and Data Model
`docs/specifications/07-database-and-data-model.md`

Design the conceptual and logical data model for organizations, users, memberships, permissions, executives, conversations, Boardrooms, decisions, documents, embeddings, cases, tasks, approvals, integrations, subscriptions, audit records, errors, incidents and usage.

Document fields, relationships, constraints, indexes, tenant ownership, retention and deletion.

Do not create actual database models or migrations during this planning session.

### 08. API and Integration Specification
`docs/specifications/08-api-and-integrations.md`

Document proposed API boundaries, endpoints, request/response contracts, authentication, validation, errors and idempotency.

Create an operations matrix for ClickUp, GoHighLevel, Dropbox, Google Drive, Stripe, AI providers and the Content Factory publishing destination.

Identify exact read/write operations, scopes, triggers, approvals, retries, credentials and acceptance tests.

Mark unknown integration details as questions.

### 09. Executive Brain, AI and RAG
`docs/specifications/09-executive-brain-and-rag.md`

Document the reusable orchestration engine, configurable specialist executives, model-provider abstraction, tool registry, persistent conversation history, Boardroom coordination, case context, decisions, task follow-through and source-grounded retrieval.

Specify document parsing, chunking, embeddings, retrieval filters, source references, insufficient-evidence behavior, deletion and tenant isolation.

Do not invent the five initial executive roles.

### 10. Security and Governance
`docs/specifications/10-security-and-governance.md`

Document authentication, authorization, tenant isolation, secrets, validation, audit logs, data retention, secure webhooks, governance policies and access-controlled tool execution.

Specify Allow, Deny and Require Approval behavior.

Explain how approval bypasses will be prevented and tested.

Do not claim unverified compliance certifications.

### 11. Testing and Acceptance
`docs/specifications/11-testing-and-acceptance.md`

Define unit, integration, API, frontend, end-to-end, security, tenant isolation, RAG, AI orchestration, billing, governance and monitoring tests.

Write measurable acceptance criteria for each milestone.

Include negative tests for cross-tenant access, unauthorized actions, approval bypass, duplicate webhooks, failed operations and sensitive-data leakage.

### 12. Deployment and DevOps
`docs/specifications/12-deployment-and-devops.md`

Document environments, environment variables, CI/CD, migrations, deployment, secrets, TLS, rollback, infrastructure ownership and release checks.

Do not deploy or configure infrastructure today.

### 13. Monitoring, Backup and Recovery
`docs/specifications/13-monitoring-backup-recovery.md`

Design the production operations system covering:
- Structured application logs
- Centralized error tracking
- Correlation IDs
- API and database health
- AI execution traces
- Integration monitoring
- Background job monitoring
- Metrics and dashboards
- Alerts and notifications
- Issue tracking
- Incident timelines
- Safe retries and recovery
- Database and file backups
- Recovery procedures
- Usage and cost monitoring

Evaluate Sentry, OpenTelemetry and appropriate metrics/logging tools. Recommend tools based on the existing stack and budget.

Specify what information is recorded, who can access it, retention periods and how sensitive data is redacted.

Define tests to verify that errors are captured, recurring issues are grouped, alerts work and recovery actions are authorized.

### 14. Development Roadmap and Milestones
`docs/specifications/14-development-roadmap.md`

Prepare an ordered implementation plan covering repository foundation, authentication, tenant isolation, UI, Organizational DNA, RAG, Executive Brain, Boardrooms, work management, governance, integrations, Content Factory, billing, monitoring, testing and deployment.

For each milestone include:
- Objectives
- Scope
- Dependencies
- Expected deliverables
- Files or modules likely to be affected
- Acceptance criteria
- Required tests
- Risks
- Estimated effort range with assumptions
- Completion definition

Do not invent precise delivery dates or guaranteed effort estimates without enough information.

### 15. Risks and Open Questions
`docs/specifications/15-risks-and-open-questions.md`

Track unresolved client requirements, technical decisions, dependencies and risks.

At minimum, include:
- Official screen inventory
- Five initial executive roles
- Executive customization boundaries
- Supported file formats and limits
- User and organization limits
- Integration operations and permissions
- Publishing destinations
- AI models and budget
- Hosting and scale
- Security and compliance
- Retention and deletion
- Subscription plans and entitlements
- Credentials and account ownership
- Support, warranty and maintenance

Classify each item by severity, owner, dependency and whether it blocks implementation.

## 6. Create project-planning and tracking documents

In addition to the 15 specifications, create:

- `docs/REQUIREMENTS_TRACEABILITY.md`
- `docs/IMPLEMENTATION_STATUS.md`
- `docs/TECHNICAL_DEBT.md`
- `docs/DECISION_LOG.md`
- `docs/OPEN_QUESTIONS.md`
- `docs/KNOWN_ISSUES.md`
- `docs/DEVELOPMENT_PLAN.md`
- `docs/TEST_STRATEGY.md`
- `docs/OBSERVABILITY_PLAN.md`
- `docs/RE