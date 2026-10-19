from typing import Protocol

from fastapi import HTTPException

from app.core.jwt import create_access_token
from app.core.security import verify_password
from app.domain.users import UserEntity
from app.schemas.auth_schema import TokenResponse


class UserRepositoryProtocol(Protocol):
    def get_by_email(self, email: str) -> UserEntity | None: ...


class AuthService:
    def __init__(self, repository: UserRepositoryProtocol):
        self.repository = repository

    def login(self, *, email: str, password: str) -> TokenResponse:
        user = self.repository.get_by_email(email)
        if user is None or user.is_deleted:
            raise HTTPException(status_code=401, detail="Invalid email or password")
        if not user.is_active:
            raise HTTPException(status_code=403, detail="User account is deactivated")
        if not verify_password(password, user.hashed_password):
            raise HTTPException(status_code=401, detail="Invalid email or password")

        return TokenResponse(access_token=create_access_token(str(user.user_id)))
