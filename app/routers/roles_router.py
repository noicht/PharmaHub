from typing import Annotated

from fastapi import APIRouter, Depends, status

from app.api.deps import get_role_service
from app.schemas.roles_schema import RoleCreateRequest, RoleResponse
from app.services.roles_service import RoleService


role_router = APIRouter(
    prefix="/api/v1/roles",
    tags=["roles"],
    responses={404: {"description": "Not found"}},
)


@role_router.get("/", response_model=list[RoleResponse])
async def get_all_roles(service: Annotated[RoleService, Depends(get_role_service)]):
    return service.get_all_roles()


@role_router.get("/{role_id}", response_model=RoleResponse)
async def get_role(role_id: int, service: Annotated[RoleService, Depends(get_role_service)]):
    return service.get_role(role_id)


@role_router.post("/", response_model=RoleResponse, status_code=status.HTTP_201_CREATED)
async def create_role(role: RoleCreateRequest, service: Annotated[RoleService, Depends(get_role_service)]):
    return service.create_role(role)
