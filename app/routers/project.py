from typing import Annotated

from fastapi import APIRouter, Depends, Path, Response, status
from sqlalchemy.orm import Session

from app.dependencies.auth import CurrentUser
from app.dependencies.database import get_db
from app.schemas.project import ProjectCreate, ProjectResponse, ProjectUpdate
from app.services.project_service import ProjectService

router = APIRouter(prefix="/projects", tags=["Projects"])


def get_project_service(db: Session = Depends(get_db)) -> ProjectService:
    return ProjectService(db)


ServiceDep = Annotated[ProjectService, Depends(get_project_service)]
ProjectId = Annotated[int, Path(gt=0, description="Project ID")]


@router.post(
    "",
    response_model=ProjectResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a project",
)
def create_project(data: ProjectCreate, current_user: CurrentUser, service: ServiceDep):
    return service.create(data, current_user)
    

@router.get("", response_model=list[ProjectResponse], summary="List my projects")
def list_projects(current_user: CurrentUser, service: ServiceDep):
    return service.list_for_user(current_user)


@router.get("/{project_id}", response_model=ProjectResponse, summary="Get project details")
def get_project(project_id: ProjectId, current_user: CurrentUser, service: ServiceDep):
    return service.get(project_id, current_user)


@router.patch("/{project_id}", response_model=ProjectResponse, summary="Update a project")
def update_project(
    project_id: ProjectId, data: ProjectUpdate, current_user: CurrentUser, service: ServiceDep
):
    return service.update(project_id, data, current_user)


@router.delete(
    "/{project_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a project",
)
def delete_project(project_id: ProjectId, current_user: CurrentUser, service: ServiceDep):
    service.delete(project_id, current_user)
    return Response(status_code=status.HTTP_204_NO_CONTENT)