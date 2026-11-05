from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.image import ProjectImage


class ImageRepository:
    def __init__(self, db: Session):
        self.db = db

    def add_many(self, images: list[ProjectImage]) -> list[ProjectImage]:
        self.db.add_all(images)
        self.db.commit()
        for image in images:
            self.db.refresh(image)
        return images

    def list_by_project(self, project_id: int) -> list[ProjectImage]:
        stmt = (
            select(ProjectImage)
            .where(ProjectImage.project_id == project_id)
            .order_by(ProjectImage.id)
        )
        return list(self.db.scalars(stmt))

    def get_in_project(self, project_id: int, image_id: int) -> ProjectImage | None:
        stmt = select(ProjectImage).where(
            ProjectImage.id == image_id,
            ProjectImage.project_id == project_id,
        )
        return self.db.scalar(stmt)