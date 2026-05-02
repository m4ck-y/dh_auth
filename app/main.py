"""
## Digital Hospital — Auth Service

Authentication microservice responsible for login, JWT issuance, token refresh,
session management, and current-user profile retrieval.

### Authentication Flow
1. User sends credentials via POST /v1/auth/login.
2. Server validates against AuthUser table and fetches roles/permissions from IAM.
3. Two HttpOnly cookies are set:
   - `access_token`: short-lived JWT (15 min default).
   - `refresh_token`: long-lived random token (30 days default).
4. POST /v1/auth/refresh reads the refresh_token cookie and issues a new access_token.
5. POST /v1/auth/logout clears both cookies.
6. GET /v1/auth/me reads the access_token cookie and returns the full user profile.

### Dependencies
- **PostgreSQL**: auth, people, org, iam schemas via dh_shared.
- **dh_iam** (optional): fetches roles and permissions per user.
"""

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

from dh_shared.base import sync_schemas
# Import all models to register them in shared_metadata
from dh_shared.models.auth.user import AuthUser # noqa
from dh_shared.models.people.person import Person # noqa
from dh_shared.models.organizations.employee import Employee # noqa
from dh_shared.models.organizations.company import Company # noqa
from dh_shared.models.iam.membership import Membership # noqa
from dh_shared.models.iam.tenant import Tenant # noqa

from app.settings.config import settings
from app.shared.database.postgres import engine
from app.shared.database.seeders import seed_admin_user
from app.contexts.auth.infrastructure.api.v1.router import router as auth_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Sync database schemas and seed default admin user on startup."""
    async with engine.begin() as conn:
        await sync_schemas(conn, ["auth", "people", "org", "iam"])

    await seed_admin_user()

    yield

    await engine.dispose()


app = FastAPI(
    title=settings.PROJECT_NAME,
    description=__doc__,
    version=settings.VERSION,
    lifespan=lifespan,
)


app.include_router(auth_router, prefix="/v1")

# Mount static files for testing UI
app.mount("/static", StaticFiles(directory="app/static"), name="static")

@app.get("/", tags=["UI"])
async def root():
    """Serve the login test UI page (static/index.html)."""
    return FileResponse("app/static/index.html")

@app.get("/health", tags=["Health"])
async def health_check():
    """Health check endpoint. Returns service status."""
    return {"status": "healthy", "service": "dh_auth"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

