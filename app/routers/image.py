from typing import Annotated

from fastapi import APIRouter, Depends, File, Path, UploadFile, status
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from app.dependencies.auth import CurrentUser
from app.dependencies.database import get_db
from app.schemas.image import ImageResponse
from app.services.image_service import ImageService

router = APIRouter(prefix="/projects/{project_id}/images", tags=["Images"])


def get_image_service(db: Session = Depends(get_db)) -> ImageService:
    return ImageService(db)


ServiceDep = Annotated[ImageService, Depends(get_image_service)]
ProjectId = Annotated[int, Path(gt=0, description="Project ID")]


@router.post(
    "",
    response_model=list[ImageResponse],
    status_code=status.HTTP_201_CREATED,
    summary="Upload one or more images to a project",
)
def upload_images(
    project_id: ProjectId,
    current_user: CurrentUser,
    service: ServiceDep,
    files: Annotated[list[UploadFile], File(description="JPEG, PNG or WEBP images")],
):
    return service.upload(project_id, files, current_user)


@router.get(
    "",
    response_model=list[ImageResponse],
    summary="List all images of a project",
)
def list_images(project_id: ProjectId, current_user: CurrentUser, service: ServiceDep):
    return service.list_for_project(project_id, current_user)


@router.get(
    "/{image_id}/file",
    response_class=FileResponse,
    summary="Download an image (owner only)",
)
def download_image(
    project_id: ProjectId,
    image_id: Annotated[int, Path(gt=0, description="Image ID")],
    current_user: CurrentUser,
    service: ServiceDep,
):
    path, image = service.get_file(project_id, image_id, current_user)
    return FileResponse(
        path,
        media_type=image.content_type,
        content_disposition_type="inline",
        filename=image.original_filename,
        headers={
            "Cache-Control": "private, max-age=3600",
            "X-Content-Type-Options": "nosniff",
        },
    )