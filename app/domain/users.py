from dataclasses import dataclass


@dataclass
class UserEntity:
    user_id: int
    name: str
    email: str
    is_deleted: bool = False
