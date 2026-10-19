import unittest

from fastapi import HTTPException

from app.core.jwt import create_access_token, decode_access_token
from app.core.security import hash_password
from app.domain.users import UserEntity
from app.services.auth_service import AuthService


class FakeUserRepository:
    def __init__(self, users: list[UserEntity] | None = None):
        self.users = {user.user_id: user for user in (users or [])}

    def get_by_email(self, email: str) -> UserEntity | None:
        return next((user for user in self.users.values() if user.email == email), None)


class AuthServiceTestCase(unittest.TestCase):
    def setUp(self) -> None:
        self.repository = FakeUserRepository(
            users=[
                UserEntity(
                    user_id=1,
                    name="John Doe",
                    email="john@example.com",
                    hashed_password=hash_password("correct-horse"),
                ),
                UserEntity(
                    user_id=2,
                    name="Inactive User",
                    email="inactive@example.com",
                    hashed_password=hash_password("some-password"),
                    is_active=False,
                ),
                UserEntity(
                    user_id=3,
                    name="Deleted User",
                    email="deleted@example.com",
                    hashed_password=hash_password("some-password"),
                    is_deleted=True,
                    is_active=False,
                ),
            ]
        )
        self.service = AuthService(self.repository)

    def test_login_returns_token_for_valid_credentials(self) -> None:
        token = self.service.login(email="john@example.com", password="correct-horse")

        self.assertEqual(token.token_type, "bearer")
        self.assertEqual(decode_access_token(token.access_token), "1")

    def test_login_raises_401_for_wrong_password(self) -> None:
        with self.assertRaises(HTTPException) as context:
            self.service.login(email="john@example.com", password="wrong-password")

        self.assertEqual(context.exception.status_code, 401)

    def test_login_raises_401_for_unknown_email(self) -> None:
        with self.assertRaises(HTTPException) as context:
            self.service.login(email="nobody@example.com", password="whatever")

        self.assertEqual(context.exception.status_code, 401)

    def test_login_raises_403_for_deactivated_user(self) -> None:
        with self.assertRaises(HTTPException) as context:
            self.service.login(email="inactive@example.com", password="some-password")

        self.assertEqual(context.exception.status_code, 403)

    def test_login_raises_401_for_deleted_user(self) -> None:
        with self.assertRaises(HTTPException) as context:
            self.service.login(email="deleted@example.com", password="some-password")

        self.assertEqual(context.exception.status_code, 401)

    def test_decode_returns_none_for_tampered_token(self) -> None:
        self.assertIsNone(decode_access_token("not-a-token"))
        self.assertIsNone(decode_access_token(create_access_token("1") + "tampered"))

    def test_token_round_trip(self) -> None:
        self.assertEqual(decode_access_token(create_access_token("42")), "42")


if __name__ == "__main__":
    unittest.main()
