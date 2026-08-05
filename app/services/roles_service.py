from typing import Protocol

from fastapi import HTTPException

from app.domain.roles import RoleEntity
from app.schemas.roles_schema import RoleCreateRequest


class RoleRepositoryProtocol(Protocol):
    def get_by_id(self, role_id: int) -> RoleEntity | None: ...
    def get_by_name(self, name: str) -> RoleEntity | None: ...
    def get_all(self) -> list[RoleEntity]: ...
    def create_role(self, *, name: str, description: str = "") -> RoleEntity: ...


class RoleService:
    def __init__(self, repository: RoleRepositoryProtocol):
        self.repository = repository

    def get_role(self, role_id: int) -> RoleEntity:
        role = self.repository.get_by_id(role_id)
        if role is None:
            raise HTTPException(status_code=404, detail="Role not found")
        return role

    def get_all_roles(self) -> list[RoleEntity]:
        return self.repository.get_all()

    def create_role(self, role: RoleCreateRequest) -> RoleEntity:
        existing_role = self.repository.get_by_name(role.name)
        if existing_role is not None:
            raise HTTPException(status_code=409, detail="Role already exists")
        return self.repository.create_role(name=role.name, description=role.description)
