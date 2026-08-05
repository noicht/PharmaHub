from typing import Annotated

from fastapi import Depends
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.repositories.roles_repository import RoleRepository
from app.repositories.user_roles_repository import UserRoleRepository
from app.repositories.users_repository import UserRepository
from app.services.roles_service import RoleService
from app.services.user_roles_service import UserRoleService
from app.services.users_service import UserService


DbSession = Annotated[Session, Depends(get_db)]


def get_user_repository(db: DbSession) -> UserRepository:
    return UserRepository(db)


def get_role_repository(db: DbSession) -> RoleRepository:
    return RoleRepository(db)


def get_user_role_repository(db: DbSession) -> UserRoleRepository:
    return UserRoleRepository(db)


def get_user_service(
    repository: Annotated[UserRepository, Depends(get_user_repository)],
) -> UserService:
    return UserService(repository)


def get_role_service(
    repository: Annotated[RoleRepository, Depends(get_role_repository)],
) -> RoleService:
    return RoleService(repository)


def get_user_role_service(
    user_repository: Annotated[UserRepository, Depends(get_user_repository)],
    role_repository: Annotated[RoleRepository, Depends(get_role_repository)],
    user_role_repository: Annotated[UserRoleRepository, Depends(get_user_role_repository)],
) -> UserRoleService:
    return UserRoleService(user_repository, role_repository, user_role_repository)
