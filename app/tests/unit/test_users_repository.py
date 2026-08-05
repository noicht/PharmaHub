import unittest

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.db.base import Base
from app.db.models import RoleModel, UserModel, UserRoleModel  # noqa: F401
from app.repositories.users_repository import UserRepository


class UserRepositoryTestCase(unittest.TestCase):
    def setUp(self) -> None:
        self.engine = create_engine("sqlite+pysqlite:///:memory:")
        Base.metadata.create_all(self.engine)
        self.session = sessionmaker(bind=self.engine, autocommit=False, autoflush=False)()
        self.repository = UserRepository(self.session)
        self.repository.create_user(name="John Doe", email="john@example.com", hashed_password="hash-1")
        self.repository.create_user(name="Jane Doe", email="jane@example.com", hashed_password="hash-2")

    def tearDown(self) -> None:
        self.session.close()
        self.engine.dispose()

    def test_get_by_id_returns_matching_user(self) -> None:
        user = self.repository.get_by_id(1)

        self.assertIsNotNone(user)
        assert user is not None
        self.assertEqual(user.user_id, 1)
        self.assertEqual(user.email, "john@example.com")

    def test_get_by_email_returns_matching_user(self) -> None:
        user = self.repository.get_by_email("jane@example.com")

        self.assertIsNotNone(user)
        assert user is not None
        self.assertEqual(user.user_id, 2)
        self.assertEqual(user.name, "Jane Doe")

    def test_get_all_returns_all_users(self) -> None:
        users = self.repository.get_all()

        self.assertEqual(len(users), 2)

    def test_create_user_persists_user(self) -> None:
        created_user = self.repository.create_user(
            name="Alice",
            email="alice@example.com",
            hashed_password="hash-3",
        )

        self.assertEqual(created_user.user_id, 3)
        self.assertEqual(created_user.name, "Alice")

    def test_update_user_persists_changes(self) -> None:
        user = self.repository.get_by_id(1)
        assert user is not None
        user.name = "John Updated"

        updated_user = self.repository.update_user(user)

        self.assertIsNotNone(updated_user)
        stored_user = self.repository.get_by_id(1)
        assert stored_user is not None
        self.assertEqual(stored_user.name, "John Updated")


if __name__ == "__main__":
    unittest.main()
