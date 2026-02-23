from datetime import datetime

from pydantic import BaseModel, EmailStr, Field


class UserCreate(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)
    full_name: str | None = Field(default=None, min_length=2, max_length=120)
    role_name: str = Field(default="User", min_length=4, max_length=32)


class UserOut(BaseModel):
    id: int
    email: EmailStr
    full_name: str | None
    role: str
    is_active: bool
    created_at: datetime

    model_config = {"from_attributes": True}
