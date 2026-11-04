import re
from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator


class UserCreate(BaseModel):
    name: str = Field(min_length=2, max_length=100, examples=["Parth Babariya"])
    email: EmailStr = Field(examples=["parth@example.com"])
    password: str = Field(min_length=8, max_length=72, examples=["Secret123"])

    @field_validator("name")
    @classmethod
    def clean_name(cls, value: str) -> str:
        value = " ".join(value.split())  # trim and collapse spaces
        if len(value) < 2:
            raise ValueError("Name must contain at least 2 characters")
        return value

    @field_validator("email")
    @classmethod
    def normalize_email(cls, value: str) -> str:
        return value.lower()

    @field_validator("password")
    @classmethod
    def check_password_strength(cls, value: str) -> str:
        if len(value.encode("utf-8")) > 72:
            raise ValueError("Password must be at most 72 bytes")
        if not re.search(r"[A-Za-z]", value) or not re.search(r"\d", value):
            raise ValueError("Password must contain at least one letter and one digit")
        return value


class UserLogin(BaseModel):
    email: EmailStr = Field(examples=["parth@example.com"])
    password: str = Field(min_length=1, max_length=72, examples=["Secret123"])

    @field_validator("email")
    @classmethod
    def normalize_email(cls, value: str) -> str:
        return value.lower()


class UserResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    email: EmailStr
    created_at: datetime


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int  # seconds