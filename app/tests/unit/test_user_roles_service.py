import unittest

from fastapi import HTTPException

from app.domain.roles import RoleEntity
from app.domain.user_roles import UserRoleEntity
from app.domain.users import UserEntity
from app.services.user_roles_service import UserRoleService


class FakeUserRepository:
    def __init__(self, users: list[UserEntity] | None = None):
        self.users = {user.user_id: user for user in (users or [])}

    def get_by_id(self, user_id: int) -> UserEntity | None:
        return self.users.get(user_id)


class FakeRoleRepository:
    def __init__(self, roles: list[RoleEntity] | None = None):
        self.roles = {role.role_id: role for role in (roles or [])}

    def get_by_id(self, role_id: int) -> RoleEntity | None:
        return self.roles.get(role_id)


class FakeUserRoleRepository:
    def __init__(self, assignments: list[UserRoleEntity] | None = None, roles: list[RoleEntity] | None = None):
        self.assignments = assignments or []
        self.roles = {role.role_id: role for role in (roles or [])}
        self.next_id = max((assignment.user_role_id for assignment in self.assignments), default=0) + 1

    def get_assignment(self, user_id: int, role_id: int) -> UserRoleEntity | None:
        return next(
            (
                assignment
                for assignment in self.assignments
                if assignment.user_id == user_id and assignment.role_id == role_id
            ),
            None,
        )

    def assign_role(self, *, user_id: int, role_id: int) -> UserRoleEntity:
        assignment = UserRoleEntity(user_role_id=self.next_id, user_id=user_id, role_id=role_id)
        self.assignments.append(assignment)
        self.next_id += 1
        return assignment

    def get_roles_for_user(self, user_id: int) -> list[RoleEntity]:
        role_ids = [assignment.role_id for assignment in self.assignments if assignment.user_id == user_id]
        return [self.roles[role_id] for role_id in role_ids if role_id in self.roles]


class UserRoleServiceTestCase(unittest.TestCase):
    def setUp(self) -> None:
        self.users = [UserEntity(user_id=1, name="John Doe", email="john@example.com", hashed_password="hash-1")]
        self.roles = [
            RoleEntity(role_id=1, name="admin", description="System administrator"),
            RoleEntity(role_id=2, name="pharmacist", description="Dispenses medication"),
        ]
        self.user_repository = FakeUserRepository(self.users)
        self.role_repository = FakeRoleRepository(self.roles)
        self.user_role_repository = FakeUserRoleRepository(roles=self.roles)
        self.service = UserRoleService(self.user_repository, self.role_repository, self.user_role_repository)

    def test_assign_role_creates_assignment(self) -> None:
        assignment = self.service.assign_role(user_id=1, role_id=1)
        self.assertEqual(assignment.user_id, 1)
        self.assertEqual(assignment.role_id, 1)

    def test_assign_role_raises_409_when_already_assigned(self) -> None:
        self.service.assign_role(user_id=1, role_id=1)

        with self.assertRaises(HTTPException) as context:
            self.service.assign_role(user_id=1, role_id=1)

        self.assertEqual(context.exception.status_code, 409)
        self.assertEqual(context.exception.detail, "Role already assigned to user")

    def test_get_roles_for_user_returns_assigned_roles(self) -> None:
        self.service.assign_role(user_id=1, role_id=2)

        roles = self.service.get_roles_for_user(1)

        self.assertEqual(len(roles), 1)
        self.assertEqual(roles[0].name, "pharmacist")

    def test_assign_role_raises_404_when_user_missing(self) -> None:
        with self.assertRaises(HTTPException) as context:
            self.service.assign_role(user_id=999, role_id=1)

        self.assertEqual(context.exception.status_code, 404)
        self.assertEqual(context.exception.detail, "User not found")


if __name__ == "__main__":
    unittest.main()
