from uuid import UUID

from sqlalchemy.orm import Session

from app.models.project import Project
from app.repositories import project as project_repository


def create_project(
    db: Session,
    name: str,
    description: str | None = None,
) -> Project:
    return project_repository.create_project(
        db=db,
        name=name,
        description=description,
    )


def get_project(
    db: Session,
    project_id: UUID,
) -> Project | None:
    return project_repository.get_project(
        db=db,
        project_id=project_id,
    )


def get_projects(
    db: Session,
) -> list[Project]:
    return project_repository.get_projects(db=db)


def delete_project(
    db: Session,
    project_id: UUID,
) -> bool:
    project = project_repository.get_project(
        db=db,
        project_id=project_id,
    )

    if project is None:
        return False

    project_repository.delete_project(
        db=db,
        project=project,
    )

    return True