# dh_auth

Microservice responsible for Identity, Authentication, and Session management (JWT, OAuth, Cookies).

## Endpoints

### Authentication

| Method | Path | Description |
|--------|------|-------------|
| POST | `/v1/auth/login` | Authenticate user and set HttpOnly session cookie |
| POST | `/v1/auth/logout` | Clear session cookie and terminate session |
| GET  | `/v1/auth/me` | [PENDING] Get current authenticated user profile |
| POST | `/v1/auth/refresh` | [PENDING] Refresh access token |

### Health

| Method | Path | Description |
|--------|------|-------------|
| GET | `/health` | Health check |

## Architecture & DTOs

This service follows the "Screaming Architecture" pattern with Bounded Contexts.

- **DTOs**: [`app/contexts/auth/application/dtos/auth_dto.py`](app/contexts/auth/application/dtos/auth_dto.py) — Request and Response data transfer objects.
- **Use Cases**: [`app/contexts/auth/application/use_cases/`](app/contexts/auth/application/use_cases/) — Orchestration of authentication logic.
- **Security Utils**: [`app/shared/utils/security.py`](app/shared/utils/security.py) — Password hashing (pwdlib/Argon2) and JWT signing (pyjwt).
- **Session Strategy**: Silent Refresh at Gateway Level (see [ADR 019](../docs/decisions/019-silent-refresh-gateway-level.md)).

## Setup

```bash
uv sync
cp .env.example .env
uv run uvicorn app.main:app --reload --port 8004
```

## Environment Variables

Copy `.env.example` to `.env`. Required variables:

| Variable | Example | Description |
|----------|---------|-------------|
| `PROJECT_NAME` | `"Digital Hospital - Auth Service"` | Service display name |
| `VERSION` | `1.0.0` | Service version |
| `ENVIRONMENT` | `development` | Environment (`development`, `staging`, `production`) |
| `POSTGRES_URL` | `postgresql+asyncpg://...` | PostgreSQL connection string |
| `JWT_SECRET_KEY` | `your-secret-here` | Secret key for JWT signing |
| `JWT_ALGORITHM` | `HS256` | Hashing algorithm for JWT |
| `SERVICE_IAM_URL` | `http://localhost:8005` | dh_iam base URL (Roles & Permissions) |
| `SERVICE_LOGGER_TRACER_URL` | `http://localhost:8010` | VitalTrace base URL |

## Dependencies

| Service | Env Variable | Purpose |
|---------|-------------|---------|
| `dh_iam` | `SERVICE_IAM_URL` | Fetching user roles and permissions for JWT payload |
| `app_logger_tracer` | `SERVICE_LOGGER_TRACER_URL` | VitalTrace observability logging |
| `dh_shared` | `path = "../dh_shared"` | Shared SQLAlchemy models (AuthUser) |
