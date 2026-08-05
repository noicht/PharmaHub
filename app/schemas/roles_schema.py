from datetime import datetime

from pydantic import BaseModel, ConfigDict


class RoleCreateRequest(BaseModel):
    name: str
    description: str = ""


class RoleResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    role_id: int
    name: str
    description: str
    is_active: bool
    created_at: datetime | None = None
    updated_at: datetime | None = None


class AssignRoleRequest(BaseModel):
    role_id: int
