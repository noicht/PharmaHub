from pydantic import BaseModel, ConfigDict, EmailStr


class UserCreateRequest(BaseModel):
    name: str
    email: EmailStr


class UserUpdateRequest(BaseModel):
    name: str | None = None
    email: EmailStr | None = None


class UserResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    user_id: int
    name: str
    email: EmailStr
    is_deleted: bool = False
