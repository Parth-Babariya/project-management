from dataclasses import dataclass
from pathlib import Path
from uuid import uuid4

from fastapi import UploadFile
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.exceptions import (
    BadRequestError,
    NotFoundError,
    PayloadTooLargeError,
    UnsupportedMediaTypeError,
)
from app.models.image import ProjectImage
from app.models.user import User
from app.repositories.image_repository import ImageRepository
from app.services.project_service import ProjectService
from app.core.logging import logger


@dataclass
class _PreparedFile:
    content: bytes
    content_type: str
    extension: str
    original_filename: str


def _detect_image_type(content: bytes) -> tuple[str, str] | None:
    """Identify the real file type from its first bytes (not from its name)."""
    if content.startswith(b"\xff\xd8\xff"):
        return "image/jpeg", ".jpg"
    if content.startswith(b"\x89PNG\r\n\x1a\n"):
        return "image/png", ".png"
    if content[:4] == b"RIFF" and content[8:12] == b"WEBP":
        return "image/webp", ".webp"
    return None


def _safe_filename(name: str | None) -> str:
    """Keep only the file name part; used for display, never as a path."""
    cleaned = Path((name or "image").replace("\\", "/")).name
    return cleaned[:255] or "image"


class ImageService:
    def __init__(self, db: Session):
        self.db = db
        self.images = ImageRepository(db)
        self.projects = ProjectService(db)

    def _prepare(self, file: UploadFile) -> _PreparedFile:
        name = _safe_filename(file.filename)

        if file.content_type not in settings.ALLOWED_IMAGE_TYPES:
            raise UnsupportedMediaTypeError(
                f"'{name}': only JPEG, PNG and WEBP images are allowed"
            )

        # Read one byte past the limit so oversized files are detected
        content = file.file.read(settings.max_upload_size_bytes + 1)
        if not content:
            raise BadRequestError(f"'{name}' is empty")
        if len(content) > settings.max_upload_size_bytes:
            raise PayloadTooLargeError(
                f"'{name}' is larger than {settings.MAX_UPLOAD_SIZE_MB} MB"
            )

        detected = _detect_image_type(content)
        if detected is None or detected[0] != file.content_type:
            raise UnsupportedMediaTypeError(
                f"'{name}' is not a valid {file.content_type} image"
            )

        return _PreparedFile(content, detected[0], detected[1], name)

    def upload(self, project_id: int, files: list[UploadFile], user: User) -> list[ProjectImage]:
        # 404 / 403 first, before touching any file
        self.projects.get_owned_project(project_id, user)

        if not files:
            raise BadRequestError("No files were uploaded")
        if len(files) > settings.MAX_IMAGES_PER_UPLOAD:
            raise BadRequestError(
                f"At most {settings.MAX_IMAGES_PER_UPLOAD} images can be uploaded at once"
            )

        # Validate EVERY file before saving ANY (all-or-nothing)
        prepared = [self._prepare(f) for f in files]

        project_dir = settings.UPLOAD_DIR / str(project_id)
        project_dir.mkdir(parents=True, exist_ok=True)

        saved: list[Path] = []
        records: list[ProjectImage] = []
        try:
            for item in prepared:
                stored_name = f"{uuid4().hex}{item.extension}"
                path = project_dir / stored_name
                path.write_bytes(item.content)
                saved.append(path)
                records.append(
                    ProjectImage(
                        project_id=project_id,
                        file_path=f"{project_id}/{stored_name}",
                        original_filename=item.original_filename,
                        content_type=item.content_type,
                        file_size=len(item.content),
                    )
                )
            uploaded_images = self.images.add_many(records)
            logger.info("Images uploaded successfully: project_id=%s user_id=%s count=%s", project_id, user.id, len(uploaded_images))
            return uploaded_images
        except Exception:
            # Database or disk failure: don't leave orphan files behind
            logger.exception(
                "Image upload failed: project_id=%s user_id=%s",
                project_id,
                user.id,
            )
            self.db.rollback()
            for path in saved:
                path.unlink(missing_ok=True)
            raise

    def list_for_project(self, project_id: int, user: User) -> list[ProjectImage]:
        self.projects.get_owned_project(project_id, user)
        return self.images.list_by_project(project_id)

    def get_file(self, project_id: int, image_id: int, user: User) -> tuple[Path, ProjectImage]:
        self.projects.get_owned_project(project_id, user)  # 404 / 403
        image = self.images.get_in_project(project_id, image_id)
        if image is None:
            logger.warning(
                "Image not found: project_id=%s image_id=%s",
                project_id,
                image_id,
            )
            raise NotFoundError("Image not found")

        base = settings.UPLOAD_DIR.resolve()
        path = (base / image.file_path).resolve()
        # Defence in depth: the resolved path must stay inside the uploads folder
        if base not in path.parents or not path.is_file():
            raise NotFoundError("Image file not found")
        return path, image