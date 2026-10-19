from typing import Annotated

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from app.core.jwt import decode_access_token
from app.db.session import get_db
from app.domain.users import UserEntity
from app.repositories.roles_repository import RoleRepository
from app.repositories.user_roles_repository import UserRoleRepository
from app.repositories.users_repository import UserRepository
from app.services.auth_service import AuthService
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


def get_auth_service(
    repository: Annotated[UserRepository, Depends(get_user_repository)],
) -> AuthService:
    return AuthService(repository)


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")


def get_current_user(
    token: Annotated[str, Depends(oauth2_scheme)],
    repository: Annotated[UserRepository, Depends(get_user_repository)],
) -> UserEntity:
    credentials_error = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    subject = decode_access_token(token)
    if subject is None:
        raise credentials_error
    try:
        user_id = int(subject)
    except ValueError:
        raise credentials_error from None
    user = repository.get_by_id(user_id)
    if user is None or user.is_deleted:
        raise credentials_error
    if not user.is_active:
        raise HTTPException(status_code=403, detail="User account is deactivated")
    return user
