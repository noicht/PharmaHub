import unittest

from fastapi import HTTPException

from app.domain.roles import RoleEntity
from app.schemas.roles_schema import RoleCreateRequest
from app.services.roles_service import RoleService


class FakeRoleRepository:
    def __init__(self, roles: list[RoleEntity] | None = None):
        self.roles = {role.role_id: role for role in (roles or [])}
        self.next_id = max(self.roles.keys(), default=0) + 1

    def get_by_id(self, role_id: int) -> RoleEntity | None:
        return self.roles.get(role_id)

    def get_by_name(self, name: str) -> RoleEntity | None:
        return next((role for role in self.roles.values() if role.name == name), None)

    def get_all(self) -> list[RoleEntity]:
        return list(self.roles.values())

    def create_role(self, *, name: str, description: str = "") -> RoleEntity:
        role = RoleEntity(role_id=self.next_id, name=name, description=description)
        self.roles[role.role_id] = role
        self.next_id += 1
        return role


class RoleServiceTestCase(unittest.TestCase):
    def setUp(self) -> None:
        repository = FakeRoleRepository(
            roles=[
                RoleEntity(role_id=1, name="admin", description="System administrator"),
                RoleEntity(role_id=2, name="pharmacist", description="Dispenses medication"),
            ]
        )
        self.service = RoleService(repository)

    def test_get_role_returns_existing_role(self) -> None:
        role = self.service.get_role(1)
        self.assertEqual(role.name, "admin")

    def test_get_role_raises_404_when_missing(self) -> None:
        with self.assertRaises(HTTPException) as context:
            self.service.get_role(999)

        self.assertEqual(context.exception.status_code, 404)
        self.assertEqual(context.exception.detail, "Role not found")

    def test_create_role_creates_new_role(self) -> None:
        created_role = self.service.create_role(RoleCreateRequest(name="auditor", description="Reads audit data"))
        self.assertEqual(created_role.role_id, 3)
        self.assertEqual(created_role.name, "auditor")

    def test_create_role_raises_409_for_duplicate_name(self) -> None:
        with self.assertRaises(HTTPException) as context:
            self.service.create_role(RoleCreateRequest(name="admin", description="duplicate"))

        self.assertEqual(context.exception.status_code, 409)
        self.assertEqual(context.exception.detail, "Role already exists")


if __name__ == "__main__":
    unittest.main()
