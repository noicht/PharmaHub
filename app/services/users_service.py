from typing import Protocol

from fastapi import HTTPException

from app.core.security import hash_password
from app.domain.users import UserEntity
from app.schemas.users_schema import UserCreateRequest, UserUpdateRequest


class UserRepositoryProtocol(Protocol):
    def get_by_id(self, user_id: int) -> UserEntity | None: ...
    def get_by_email(self, email: str) -> UserEntity | None: ...
    def get_all(self) -> list[UserEntity]: ...
    def create_user(self, *, name: str, email: str, hashed_password: str) -> UserEntity: ...
    def update_user(self, user: UserEntity) -> UserEntity | None: ...


class UserService:
    def __init__(self, repository: UserRepositoryProtocol):
        self.repository = repository

    def get_user(self, user_id: int) -> UserEntity:
        user = self.repository.get_by_id(user_id)

        if user is None or user.is_deleted:
            raise HTTPException(status_code=404, detail="User not found")

        return user

    def get_all_users(self) -> list[UserEntity]:
        users = self.repository.get_all()
        return [user for user in users if not user.is_deleted]

    def create_user(self, user: UserCreateRequest) -> UserEntity:
        existing_user = self.repository.get_by_email(str(user.email))
        if existing_user is not None:
            raise HTTPException(status_code=409, detail="Email is already registered")

        return self.repository.create_user(
            name=user.name,
            email=str(user.email),
            hashed_password=hash_password(user.password),
        )

    def update_user(self, user_id: int, user: UserUpdateRequest) -> UserEntity:
        existing_user = self.repository.get_by_id(user_id)

        if existing_user is None:
            raise HTTPException(status_code=404, detail="User not found")

        if existing_user.is_deleted:
            raise HTTPException(status_code=400, detail="Invalid action: user is deleted")

        if user.email is not None:
            email_owner = self.repository.get_by_email(str(user.email))
            if email_owner is not None and email_owner.user_id != user_id:
                raise HTTPException(status_code=409, detail="Email is already registered")
            existing_user.email = str(user.email)

        if user.name is not None:
            existing_user.name = user.name

        if user.password is not None:
            existing_user.hashed_password = hash_password(user.password)

        updated_user = self.repository.update_user(existing_user)
        if updated_user is None:
            raise HTTPException(status_code=404, detail="User not found")

        return updated_user

    def delete_user(self, user_id: int) -> UserEntity:
        user = self.repository.get_by_id(user_id)

        if user is None:
            raise HTTPException(status_code=404, detail="User not found")
        if user.is_deleted:
            raise HTTPException(status_code=400, detail="User is already deleted")

        user.is_deleted = True
        user.is_active = False
        updated_user = self.repository.update_user(user)
        if updated_user is None:
            raise HTTPException(status_code=404, detail="User not found")

        return updated_user

    def deactivate_user(self, user_id: int) -> UserEntity:
        user = self.repository.get_by_id(user_id)

        if user is None:
            raise HTTPException(status_code=404, detail="User not found")
        if user.is_deleted:
            raise HTTPException(status_code=400, detail="Invalid action: user is deleted")
        if not user.is_active:
            raise HTTPException(status_code=400, detail="User is already deactivated")

        user.is_active = False
        updated_user = self.repository.update_user(user)
        if updated_user is None:
            raise HTTPException(status_code=404, detail="User not found")

        return updated_user
