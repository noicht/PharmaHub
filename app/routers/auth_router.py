from typing import Annotated

from fastapi import APIRouter, Depends

from app.api.deps import get_auth_service, get_current_user
from app.domain.users import UserEntity
from app.schemas.auth_schema import LoginRequest, TokenResponse
from app.schemas.users_schema import UserResponse
from app.services.auth_service import AuthService


auth_router = APIRouter(
    prefix="/api/v1/auth",
    tags=["auth"],
)


@auth_router.post("/login", response_model=TokenResponse)
async def login(payload: LoginRequest, service: Annotated[AuthService, Depends(get_auth_service)]):
    return service.login(email=str(payload.email), password=payload.password)


@auth_router.get("/me", response_model=UserResponse)
async def get_me(current_user: Annotated[UserEntity, Depends(get_current_user)]):
    return current_user
