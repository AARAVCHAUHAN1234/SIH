from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.project import Project


def create_project(
    db: Session,
    name: str,
    description: str | None = None,
) -> Project:
    project = Project(
        name=name,
        description=description,
    )

    db.add(project)
    db.commit()
    db.refresh(project)

    return project


def get_project(
    db: Session,
    project_id: UUID,
) -> Project | None:
    statement = select(Project).where(Project.id == project_id)

    return db.scalar(statement)


def get_projects(
    db: Session,
) -> list[Project]:
    statement = select(Project).order_by(Project.created_at.desc())

    return list(db.scalars(statement).all())


def delete_project(
    db: Session,
    project: Project,
) -> None:
    db.delete(project)
    db.commit()