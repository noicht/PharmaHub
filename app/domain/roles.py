from dataclasses import dataclass
from datetime import datetime


@dataclass
class RoleEntity:
    role_id: int
    name: str
    description: str = ""
    is_active: bool = True
    created_at: datetime | None = None
    updated_at: datetime | None = None
