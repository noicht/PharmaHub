from fastapi import HTTPException

from app.domain.users import UserEntity
from app.repositories.users_repository import UserRepository
from app.schemas.users_schema import UserCreateRequest, UserUpdateRequest


class UserService:
    def __init__(self, repository: UserRepository):
        self.repository = repository

    def get_user(self, user_id: int) -> UserEntity:
        user = self.repository.get_by_id(user_id)

        if user is None:
            raise HTTPException(status_code=404, detail="User not found")

        return user

    def get_all_users(self) -> list[UserEntity]:
        return self.repository.get_all()

    def create_user(self, user: UserCreateRequest) -> UserEntity:
        return self.repository.create_user(name=user.name, email=str(user.email))

    def update_user(self, user_id: int, user: UserUpdateRequest) -> UserEntity:
        existing_user = self.repository.get_by_id(user_id)

        if existing_user is None:
            raise HTTPException(status_code=404, detail="User not found")

        if user.name is not None:
            existing_user.name = user.name

        if user.email is not None:
            existing_user.email = str(user.email)

        updated_user = self.repository.update_user(existing_user)

        if updated_user is None:
            raise HTTPException(status_code=404, detail="User not found")

        return updated_user

    def delete_user(self, user_id: int) -> UserEntity:
        deleted_user = self.repository.delete_user(user_id)

        if deleted_user is None:
            raise HTTPException(status_code=404, detail="User not found")

        return deleted_user
