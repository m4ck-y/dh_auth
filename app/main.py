from contextlib import asynccontextmanager

from fastapi import FastAPI
from sqlalchemy import text

from dh_shared.base import sync_schemas
from dh_shared.models.auth import AuthBase
import dh_shared.models.auth    # noqa
from dh_shared.models.people.person import Person # noqa

from app.settings.config import settings
from app.shared.database.postgres import engine
from app.contexts.auth.infrastructure.api.v1.router import router as auth_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    async with engine.begin() as conn:
        # This will create both 'auth' and 'people' schemas if they don't exist,
        # but only create the tables belonging to 'auth' schema.
        # Person must be imported to be in the shared_metadata for FK resolution.
        await sync_schemas(conn, ["auth"])

    yield

    await engine.dispose()


app = FastAPI(
    title=settings.PROJECT_NAME,
    description="Microservicio encargado de la Identidad y Autenticación (JWT, OAuth, Sesiones).",
    version=settings.VERSION,
    lifespan=lifespan,
)


app.include_router(auth_router, prefix="/v1")


@app.get("/health", tags=["Health"])
async def health_check():
    return {"status": "healthy", "service": "dh_auth"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
