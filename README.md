# AdvoLevel

Multi-tenant AI executive-team platform. Specs, decisions and status live in [`docs/`](docs/README.md).

| Path | Contents |
|---|---|
| `backend/` | FastAPI API (Python 3.12+, SQLAlchemy 2, Alembic), managed with [uv](https://docs.astral.sh/uv/) |
| `frontend/` | Next.js 16 (App Router, React 19, Tailwind v4), managed with npm |
| `infra/` | Local infrastructure (Postgres role setup) |
| `docs/` | Specifications, decision log, implementation status, known issues |

## Prerequisites
Docker (with compose), Python 3.12+ and uv, Node 22+ and npm.

## Run locally
```sh
docker compose up -d --build     # db, redis, s3, mailpit, migrate, api
curl http://127.0.0.1:8000/readyz  # {"status":"ok", ...}
```
API docs: http://127.0.0.1:8000/api/v1/docs. Host ports default to 5442 (Postgres), 6390 (Redis), 8333 (S3), 8000 (API); copy `.env.example` to `.env` to change them.

Frontend:
```sh
cd frontend
cp .env.example .env.local
npm ci
npm run dev                      # http://localhost:3000
```

## Authentication (Clerk) and email
Sign-in uses Clerk (DEC-006). Without keys the API answers authenticated routes with 503 `auth_not_configured`; the tests use local keys and need nothing.

1. Create a Clerk **development** instance in an AdvoLevel-owned account (KI-004). In the dashboard: require email verification, enable the password policy and MFA options you want.
2. Root `.env` (read by compose) and `backend/.env`: `AUTH_ISSUER` (the Frontend API URL, `https://<slug>.clerk.accounts.dev`), `AUTH_SECRET_KEY` (`sk_test_…`), `AUTH_WEBHOOK_SECRET` (`whsec_…`, from step 3).
3. Webhooks: point an endpoint at `<public API URL>/api/v1/webhooks/clerk` for `user.created`, `user.updated`, `user.deleted` (locally, use a tunnel; without it users are provisioned just in time on first request).
4. `frontend/.env.local`: `NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY`, `CLERK_SECRET_KEY` (see `frontend/.env.example`).

Invitation emails go to Mailpit locally: http://127.0.0.1:8025. Platform admins (needed for `/api/v1/admin/*`) are set by SQL until the admin UI exists (M12): `UPDATE users SET is_platform_admin = true WHERE email = '…';` as the owner role.

## API contract
The frontend client is generated from the backend's OpenAPI document. After changing an endpoint or schema:
```sh
cd backend && uv run python -m app.openapi ../frontend/lib/api/openapi.json
cd ../frontend && npm run api:types
```
CI fails if either generated file is out of date.

## Backend development
```sh
cd backend
cp .env.example .env             # points at the compose services
uv sync
uv run pytest                    # unit tests
uv run pytest -m integration     # needs `docker compose up`
uv run ruff format . && uv run ruff check . && uv run mypy app tests
uv run alembic revision -m "..." # new migration (runs as the owner role)
```
Use `127.0.0.1`, not `localhost`, in local URLs: compose binds IPv4 loopback only. On Windows, run the API itself through compose (KI-009).

## Frontend development
```sh
cd frontend
npm run lint && npm run format:check && npm run typecheck && npm test && npm run build
```
Next 16 differs from older versions: read `frontend/AGENTS.md` before changing framework code.

## Conventions
- Never commit secrets. Only `*.env.example` files (names, local placeholders) are tracked. Install the hooks once: `uvx pre-commit install`.
- The API connects as `advolevel_app` (no BYPASSRLS); only migrations use the owner role via `DATABASE_MIGRATION_URL`.
- Errors are RFC 9457 `application/problem+json` and carry `request_id`; every log line carries it too.
- Record decisions in `docs/DECISION_LOG.md` and progress in `docs/IMPLEMENTATION_STATUS.md`.
