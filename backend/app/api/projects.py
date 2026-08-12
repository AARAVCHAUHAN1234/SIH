from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.project import Project


router = APIRouter(
    prefix="/api/v1/projects",
    tags=["Projects"],
)


class ProjectCreate(BaseModel):
    name: str
    description: str | None = None


@router.post("/", status_code=201)
def create_project(
    project: ProjectCreate,
    db: Session = Depends(get_db),
):
    new_project = Project(
        name=project.name,
        description=project.description,
    )

    db.add(new_project)
    db.commit()
    db.refresh(new_project)

    return {
        "message": "Project created successfully",
        "project": {
            "id": str(new_project.id),
            "name": new_project.name,
            "description": new_project.description,
            "status": new_project.status,
        },
    }