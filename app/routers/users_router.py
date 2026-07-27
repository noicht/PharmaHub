from fastapi import APIRouter, Depends

from app.api.deps import get_user_service
from app.schemas.users_schema import UserCreateRequest, UserResponse, UserUpdateRequest
from app.services.users_service import UserService


user_router = APIRouter(
    prefix="/api/v1/users",
    tags=["users"],
    responses={404: {"description": "Not found"}},
)


@user_router.get("/{user_id}", response_model=UserResponse, tags=["users"])
async def get_user(user_id: int, service: UserService = Depends(get_user_service)):
    return service.get_user(user_id)


@user_router.get("/", response_model=list[UserResponse], tags=["users"])
async def get_all_users(service: UserService = Depends(get_user_service)):
    return service.get_all_users()


@user_router.post("/", response_model=UserResponse, tags=["users"])
async def create_user(user: UserCreateRequest, service: UserService = Depends(get_user_service)):
    return service.create_user(user)


@user_router.patch("/{user_id}", response_model=UserResponse, tags=["users"])
async def update_user(user_id: int, user: UserUpdateRequest, service: UserService = Depends(get_user_service)):
    return service.update_user(user_id, user)


@user_router.delete("/{user_id}", response_model=UserResponse, tags=["users"])
async def delete_user(user_id: int, service: UserService = Depends(get_user_service)):
    return service.delete_user(user_id)
