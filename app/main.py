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
    async with engine.begin() as conn:
        # Sync all schemas required for auth and profile information
        await sync_schemas(conn, ["auth", "people", "org", "iam"])

    await seed_admin_user()

    yield

    await engine.dispose()


app = FastAPI(
    title=settings.PROJECT_NAME,
    description="Microservicio encargado de la Identidad y Autenticación (JWT, OAuth, Sesiones).",
    version=settings.VERSION,
    lifespan=lifespan,
)


app.include_router(auth_router, prefix="/v1")

# Mount static files for testing UI
app.mount("/static", StaticFiles(directory="app/static"), name="static")

@app.get("/", tags=["UI"])
async def root():
    return FileResponse("app/static/index.html")

@app.get("/health", tags=["Health"])
async def health_check():
    return {"status": "healthy", "service": "dh_auth"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
