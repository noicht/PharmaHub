from app.domain.users import UserEntity


class UserRepository:
    def __init__(self, seed_users: list[UserEntity] | None = None):
        users = seed_users or []
        self._users = {user.user_id: user for user in users}
        self._next_id = max(self._users.keys(), default=0) + 1

        print(self._users)
        print(self._next_id)

    def get_by_id(self, user_id: int) -> UserEntity | None:
        return self._users.get(user_id)

    def get_all(self) -> list[UserEntity]:
        return list(self._users.values())

    def create_user(self, *, name: str, email: str) -> UserEntity:
        new_user = UserEntity(user_id=self._next_id, name=name, email=email)
        self._users[new_user.user_id] = new_user
        self._next_id += 1
        return new_user

    def update_user(self, user: UserEntity) -> UserEntity | None:
        if user.user_id not in self._users:
            return None

        self._users[user.user_id] = user
        return user

    def delete_user(self, user_id: int) -> UserEntity | None:
        return self._users.pop(user_id, None)


def build_seed_users() -> list[UserEntity]: # funcion para crear un seed de usuarios fake
    return [
        UserEntity(user_id=1, name="John Doe", email="jdoe@email.com"),
        UserEntity(user_id=2, name="Aldana Paniagua", email="alpa@email.com"),
        UserEntity(user_id=3, name="Martin Cabrera", email="mcab@email.com"),
    ]
