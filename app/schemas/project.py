from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, field_validator

MAX_TAGS = 20
MAX_TAG_LENGTH = 50


# ---------- Shared cleaning helpers ----------

def _clean_text(value: str) -> str:
    return " ".join(value.split())  # trim and collapse spaces


def _clean_category(value: str) -> str:
    return _clean_text(value).lower()


def _clean_tags(tags: list[str]) -> list[str]:
    cleaned: list[str] = []
    for tag in tags:
        tag = _clean_text(tag).lower()
        if not tag:
            continue
        if len(tag) > MAX_TAG_LENGTH:
            raise ValueError(f"Each tag must be at most {MAX_TAG_LENGTH} characters")
        if tag not in cleaned:  # remove duplicates, keep order
            cleaned.append(tag)
    return cleaned


# ---------- Request schemas ----------

class ProjectCreate(BaseModel):
    title: str = Field(min_length=3, max_length=200, examples=["Metro Station Retrofit"])
    description: str | None = Field(default=None, max_length=5000, examples=["Seismic retrofit of station structure"])
    category: str = Field(min_length=2, max_length=50, examples=["infrastructure"])
    tags: list[str] = Field(default_factory=list, max_length=MAX_TAGS, examples=[["steel", "urgent"]])

    @field_validator("title")
    @classmethod
    def validate_title(cls, value: str) -> str:
        value = _clean_text(value)
        if len(value) < 3:
            raise ValueError("Title must contain at least 3 characters")
        return value

    @field_validator("category")
    @classmethod
    def validate_category(cls, value: str) -> str:
        value = _clean_category(value)
        if len(value) < 2:
            raise ValueError("Category must contain at least 2 characters")
        return value

    @field_validator("tags")
    @classmethod
    def validate_tags(cls, value: list[str]) -> list[str]:
        return _clean_tags(value)


class ProjectUpdate(BaseModel):
    """All fields optional: only the fields sent are changed (partial update)."""

    title: str | None = Field(default=None, min_length=3, max_length=200)
    description: str | None = Field(default=None, max_length=5000)
    category: str | None = Field(default=None, min_length=2, max_length=50)
    tags: list[str] | None = Field(default=None, max_length=MAX_TAGS)

    @field_validator("title")
    @classmethod
    def validate_title(cls, value: str | None) -> str:
        if value is None:
            raise ValueError("Title cannot be null")
        value = _clean_text(value)
        if len(value) < 3:
            raise ValueError("Title must contain at least 3 characters")
        return value

    @field_validator("category")
    @classmethod
    def validate_category(cls, value: str | None) -> str:
        if value is None:
            raise ValueError("Category cannot be null")
        value = _clean_category(value)
        if len(value) < 2:
            raise ValueError("Category must contain at least 2 characters")
        return value

    @field_validator("tags")
    @classmethod
    def validate_tags(cls, value: list[str] | None) -> list[str]:
        if value is None:
            raise ValueError("Tags cannot be null, send [] to remove all tags")
        return _clean_tags(value)


# ---------- Response schema ----------

class ProjectResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    description: str | None
    category: str
    tags: list[str]
    owner_id: int
    created_at: datetime
    updated_at: datetime