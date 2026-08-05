import unittest
from datetime import UTC, datetime

from fastapi import HTTPException

from app.domain.users import UserEntity
from app.schemas.users_schema import UserCreateRequest, UserUpdateRequest
from app.services.users_service import UserService


class FakeUserRepository:
    def __init__(self, users: list[UserEntity] | None = None):
        self.users = {user.user_id: user for user in (users or [])}
        self.next_id = max(self.users.keys(), default=0) + 1

    def get_by_id(self, user_id: int) -> UserEntity | None:
        return self.users.get(user_id)

    def get_by_email(self, email: str) -> UserEntity | None:
        return next((user for user in self.users.values() if user.email == email), None)

    def get_all(self) -> list[UserEntity]:
        return list(self.users.values())

    def create_user(self, *, name: str, email: str, hashed_password: str) -> UserEntity:
        now = datetime.now(UTC)
        user = UserEntity(
            user_id=self.next_id,
            name=name,
            email=email,
            hashed_password=hashed_password,
            created_at=now,
            updated_at=now,
        )
        self.users[user.user_id] = user
        self.next_id += 1
        return user

    def update_user(self, user: UserEntity) -> UserEntity | None:
        if user.user_id not in self.users:
            return None
        self.users[user.user_id] = user
        return user


class UserServiceTestCase(unittest.TestCase):
    def setUp(self) -> None:
        repository = FakeUserRepository(
            users=[
                UserEntity(user_id=1, name="John Doe", email="john@example.com", hashed_password="hash-1"),
                UserEntity(user_id=2, name="Jane Doe", email="jane@example.com", hashed_password="hash-2"),
            ]
        )
        self.service = UserService(repository)

    def test_get_user_returns_existing_user(self) -> None:
        user = self.service.get_user(1)

        self.assertEqual(user.user_id, 1)
        self.assertEqual(user.name, "John Doe")

    def test_get_user_raises_404_when_missing(self) -> None:
        with self.assertRaises(HTTPException) as context:
            self.service.get_user(999)

        self.assertEqual(context.exception.status_code, 404)
        self.assertEqual(context.exception.detail, "User not found")

    def test_create_user_creates_and_hashes_password(self) -> None:
        request = UserCreateRequest(
            name="Alice",
            email="alice@example.com",
            password="super-secret",
        )

        created_user = self.service.create_user(request)

        self.assertEqual(created_user.user_id, 3)
        self.assertEqual(created_user.email, "alice@example.com")
        self.assertNotEqual(created_user.hashed_password, "super-secret")
        self.assertIn("$", created_user.hashed_password)

    def test_create_user_raises_409_for_duplicate_email(self) -> None:
        request = UserCreateRequest(
            name="John Clone",
            email="john@example.com",
            password="another-secret",
        )

        with self.assertRaises(HTTPException) as context:
            self.service.create_user(request)

        self.assertEqual(context.exception.status_code, 409)
        self.assertEqual(context.exception.detail, "Email is already registered")

    def test_update_user_applies_partial_changes(self) -> None:
        request = UserUpdateRequest(name="Updated Name")

        updated_user = self.service.update_user(1, request)

        self.assertEqual(updated_user.name, "Updated Name")
        self.assertEqual(updated_user.email, "john@example.com")

    def test_update_user_rejects_duplicate_email(self) -> None:
        request = UserUpdateRequest(email="jane@example.com")

        with self.assertRaises(HTTPException) as context:
            self.service.update_user(1, request)

        self.assertEqual(context.exception.status_code, 409)
        self.assertEqual(context.exception.detail, "Email is already registered")

    def test_update_user_raises_404_when_missing(self) -> None:
        request = UserUpdateRequest(name="Nobody")

        with self.assertRaises(HTTPException) as context:
            self.service.update_user(999, request)

        self.assertEqual(context.exception.status_code, 404)
        self.assertEqual(context.exception.detail, "User not found")

    def test_delete_user_marks_user_as_deleted_and_inactive(self) -> None:
        deleted_user = self.service.delete_user(1)

        self.assertTrue(deleted_user.is_deleted)
        self.assertFalse(deleted_user.is_active)

    def test_delete_user_raises_400_when_already_deleted(self) -> None:
        self.service.delete_user(1)

        with self.assertRaises(HTTPException) as context:
            self.service.delete_user(1)

        self.assertEqual(context.exception.status_code, 400)
        self.assertEqual(context.exception.detail, "User is already deleted")

    def test_deactivate_user_marks_user_as_inactive(self) -> None:
        deactivated_user = self.service.deactivate_user(1)

        self.assertFalse(deactivated_user.is_active)

    def test_deactivate_user_raises_400_for_deleted_user(self) -> None:
        self.service.delete_user(1)

        with self.assertRaises(HTTPException) as context:
            self.service.deactivate_user(1)

        self.assertEqual(context.exception.status_code, 400)
        self.assertEqual(context.exception.detail, "Invalid action: user is deleted")


if __name__ == "__main__":
    unittest.main()
