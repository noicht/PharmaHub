from typing import Protocol

from fastapi import HTTPException

from app.domain.roles import RoleEntity
from app.domain.user_roles import UserRoleEntity
from app.domain.users import UserEntity


class UserRepositoryProtocol(Protocol):
    def get_by_id(self, user_id: int) -> UserEntity | None: ...


class RoleRepositoryProtocol(Protocol):
    def get_by_id(self, role_id: int) -> RoleEntity | None: ...


class UserRoleRepositoryProtocol(Protocol):
    def get_assignment(self, user_id: int, role_id: int) -> UserRoleEntity | None: ...
    def assign_role(self, *, user_id: int, role_id: int) -> UserRoleEntity: ...
    def get_roles_for_user(self, user_id: int) -> list[RoleEntity]: ...


class UserRoleService:
    def __init__(
        self,
        user_repository: UserRepositoryProtocol,
        role_repository: RoleRepositoryProtocol,
        user_role_repository: UserRoleRepositoryProtocol,
    ):
        self.user_repository = user_repository
        self.role_repository = role_repository
        self.user_role_repository = user_role_repository

    def assign_role(self, user_id: int, role_id: int) -> UserRoleEntity:
        user = self.user_repository.get_by_id(user_id)
        if user is None or user.is_deleted:
            raise HTTPException(status_code=404, detail="User not found")

        role = self.role_repository.get_by_id(role_id)
        if role is None:
            raise HTTPException(status_code=404, detail="Role not found")
        if not role.is_active:
            raise HTTPException(status_code=400, detail="Role is inactive")

        existing_assignment = self.user_role_repository.get_assignment(user_id=user_id, role_id=role_id)
        if existing_assignment is not None:
            raise HTTPException(status_code=409, detail="Role already assigned to user")

        return self.user_role_repository.assign_role(user_id=user_id, role_id=role_id)

    def get_roles_for_user(self, user_id: int) -> list[RoleEntity]:
        user = self.user_repository.get_by_id(user_id)
        if user is None or user.is_deleted:
            raise HTTPException(status_code=404, detail="User not found")

        return self.user_role_repository.get_roles_for_user(user_id)
