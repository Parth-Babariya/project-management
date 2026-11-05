from sqlalchemy.orm import Session

from app.core.exceptions import ForbiddenError, NotFoundError
from app.models.project import Project
from app.models.user import User
from app.repositories.project_repository import ProjectRepository
from app.schemas.project import ProjectCreate, ProjectUpdate


class ProjectService:
    def __init__(self, db: Session):
        self.projects = ProjectRepository(db)

    def get_owned_project(self, project_id: int, user: User) -> Project:
        """Return the project if it exists and belongs to the user."""
        project = self.projects.get_by_id(project_id)
        if project is None:
            raise NotFoundError("Project not found")
        if project.owner_id != user.id:
            raise ForbiddenError("You do not have access to this project")
        return project

    def create(self, data: ProjectCreate, user: User) -> Project:
        return self.projects.create(owner_id=user.id, data=data.model_dump())

    def list_for_user(self, user: User) -> list[Project]:
        return self.projects.list_by_owner(user.id)

    def get(self, project_id: int, user: User) -> Project:
        return self.get_owned_project(project_id, user)

    def update(self, project_id: int, data: ProjectUpdate, user: User) -> Project:
        project = self.get_owned_project(project_id, user)
        changes = data.model_dump(exclude_unset=True)  # only fields the client sent
        if not changes:
            return project
        return self.projects.update(project, changes)

    def delete(self, project_id: int, user: User) -> None:
        project = self.get_owned_project(project_id, user)
        self.projects.delete(project)