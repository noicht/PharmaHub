from dataclasses import dataclass
from datetime import datetime


@dataclass
class UserRoleEntity:
    user_role_id: int
    user_id: int
    role_id: int
    assigned_at: datetime | None = None
