from typing import Any

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.project import Project


class ProjectRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, project_id: int) -> Project | None:
        return self.db.get(Project, project_id)

    def list_by_owner(self, owner_id: int) -> list[Project]:
        stmt = (
            select(Project)
            .where(Project.owner_id == owner_id)
            .order_by(Project.created_at.desc(), Project.id.desc())
        )
        return list(self.db.scalars(stmt))

    def create(self, *, owner_id: int, data: dict[str, Any]) -> Project:
        project = Project(owner_id=owner_id, **data)
        self.db.add(project)
        self.db.commit()
        self.db.refresh(project)
        return project

    def update(self, project: Project, changes: dict[str, Any]) -> Project:
        for field, value in changes.items():
            setattr(project, field, value)
        self.db.commit()
        self.db.refresh(project)  # reload updated_at set by the database
        return project

    def delete(self, project: Project) -> None:
        self.db.delete(project)
        self.db.commit()