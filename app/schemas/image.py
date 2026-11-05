from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, computed_field

from app.core.config import settings

class ImageResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    project_id: int
    original_filename: str
    content_type: str
    file_size: int
    uploaded_at: datetime
    file_path: str = Field(exclude=True)  # internal, not sent to clients

    # @computed_field
    # @property
    # def url(self) -> str:
    #     return f"/uploads/{self.file_path}"

    # @computed_field
    # @property
    # def url(self) -> str:
    #     return f"/projects/{self.project_id}/images/{self.id}/file"

    @computed_field
    @property
    def url(self) -> str:
        if settings.PUBLIC_UPLOADS:
            return f"/uploads/{self.file_path}"
        return f"/projects/{self.project_id}/images/{self.id}/file"