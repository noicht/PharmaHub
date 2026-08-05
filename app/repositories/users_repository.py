from sqlalchemy.orm import Session

from app.db.models.user import UserModel
from app.domain.users import UserEntity


class UserRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, user_id: int) -> UserEntity | None:
        user = self.db.get(UserModel, user_id)
        if user is None:
            return None
        return self._to_entity(user)

    def get_by_email(self, email: str) -> UserEntity | None:
        user = self.db.query(UserModel).filter(UserModel.email == email).first()
        if user is None:
            return None
        return self._to_entity(user)

    def get_all(self) -> list[UserEntity]:
        users = self.db.query(UserModel).order_by(UserModel.user_id).all()
        return [self._to_entity(user) for user in users]

    def create_user(self, *, name: str, email: str, hashed_password: str) -> UserEntity:
        user = UserModel(name=name, email=email, hashed_password=hashed_password)
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        return self._to_entity(user)

    def update_user(self, user: UserEntity) -> UserEntity | None:
        stored_user = self.db.get(UserModel, user.user_id)
        if stored_user is None:
            return None

        stored_user.name = user.name
        stored_user.email = user.email
        stored_user.hashed_password = user.hashed_password
        stored_user.is_active = user.is_active
        stored_user.is_deleted = user.is_deleted
        self.db.commit()
        self.db.refresh(stored_user)
        return self._to_entity(stored_user)

    @staticmethod
    def _to_entity(user: UserModel) -> UserEntity:
        return UserEntity(
            user_id=user.user_id,
            name=user.name,
            email=user.email,
            hashed_password=user.hashed_password,
            is_active=user.is_active,
            is_deleted=user.is_deleted,
            created_at=user.created_at,
            updated_at=user.updated_at,
        )
