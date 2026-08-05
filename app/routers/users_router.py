from typing import Annotated

from fastapi import APIRouter, Depends, status

from app.api.deps import get_user_role_service, get_user_service
from app.schemas.roles_schema import AssignRoleRequest, RoleResponse
from app.schemas.users_schema import UserCreateRequest, UserResponse, UserUpdateRequest
from app.services.user_roles_service import UserRoleService
from app.services.users_service import UserService


user_router = APIRouter(
    prefix="/api/v1/users",
    tags=["users"],
    responses={404: {"description": "Not found"}},
)


@user_router.get("/{user_id}", response_model=UserResponse)
async def get_user(user_id: int, service: Annotated[UserService, Depends(get_user_service)]):
    return service.get_user(user_id)


@user_router.get("/", response_model=list[UserResponse])
async def get_all_users(service: Annotated[UserService, Depends(get_user_service)]):
    return service.get_all_users()


@user_router.post("/", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def create_user(user: UserCreateRequest, service: Annotated[UserService, Depends(get_user_service)]):
    return service.create_user(user)


@user_router.patch("/{user_id}", response_model=UserResponse)
async def update_user(
    user_id: int,
    user: UserUpdateRequest,
    service: Annotated[UserService, Depends(get_user_service)],
):
    return service.update_user(user_id, user)


@user_router.delete("/{user_id}", response_model=UserResponse)
async def delete_user(user_id: int, service: Annotated[UserService, Depends(get_user_service)]):
    return service.delete_user(user_id)


@user_router.patch("/{user_id}/deactivate", response_model=UserResponse)
async def deactivate_user(user_id: int, service: Annotated[UserService, Depends(get_user_service)]):
    return service.deactivate_user(user_id)


@user_router.post("/{user_id}/roles", response_model=RoleResponse, status_code=status.HTTP_201_CREATED)
async def assign_role_to_user(
    user_id: int,
    payload: AssignRoleRequest,
    service: Annotated[UserRoleService, Depends(get_user_role_service)],
):
    service.assign_role(user_id=user_id, role_id=payload.role_id)
    roles = service.get_roles_for_user(user_id)
    return next(role for role in roles if role.role_id == payload.role_id)


@user_router.get("/{user_id}/roles", response_model=list[RoleResponse])
async def get_roles_for_user(
    user_id: int,
    service: Annotated[UserRoleService, Depends(get_user_role_service)],
):
    return service.get_roles_for_user(user_id)
