from fastapi import FastAPI
from sqlalchemy import text

from app.core.config import settings
from app.core.database import engine
from app.api.projects import router as projects_router
from app.api.bridges import router as bridges_router
from app.api.components import router as components_router
from app.api.inspections import router as inspections_router
app = FastAPI(
    title=settings.app_name,
    version="0.1.0",
)


app.include_router(projects_router)
app.include_router(bridges_router)
app.include_router(components_router)
app.include_router(inspections_router)

@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "service": "garuda-kavach-api",
    }


@app.get("/health/database")
def database_health_check():
    with engine.connect() as connection:
        result = connection.execute(text("SELECT 1"))
        result.scalar_one()

    return {
        "status": "healthy",
        "database": "postgresql",
    }