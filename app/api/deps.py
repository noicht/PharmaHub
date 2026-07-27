from fastapi import Request

from app.repositories.users_repository import UserRepository
from app.services.users_service import UserService


def get_user_repository(request: Request) -> UserRepository:
    return request.app.state.user_repository


def get_user_service(request: Request) -> UserService:
    repository = get_user_repository(request)
    return UserService(repository)
