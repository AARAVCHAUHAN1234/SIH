from fastapi import FastAPI
from sqlalchemy import text

from app.core.config import settings
from app.core.database import engine


app = FastAPI(
    title=settings.app_name,
    version="0.1.0",
)


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