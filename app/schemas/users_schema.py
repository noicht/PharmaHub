from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr


class UserCreateRequest(BaseModel):
    name: str
    email: EmailStr
    password: str


class UserUpdateRequest(BaseModel):
    name: str | None = None
    email: EmailStr | None = None
    password: str | None = None


class UserResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    user_id: int
    name: str
    email: EmailStr
    is_active: bool
    is_deleted: bool
    created_at: datetime | None = None
    updated_at: datetime | None = None
