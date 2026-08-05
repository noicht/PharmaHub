from dataclasses import dataclass
from datetime import datetime


@dataclass
class UserEntity:
    user_id: int
    name: str
    email: str
    hashed_password: str
    is_active: bool = True
    is_deleted: bool = False
    created_at: datetime | None = None
    updated_at: datetime | None = None
