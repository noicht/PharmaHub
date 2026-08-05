from sqlalchemy.orm import Session

from app.db.models.role import RoleModel
from app.db.models.user_role import UserRoleModel
from app.domain.roles import RoleEntity
from app.domain.user_roles import UserRoleEntity


class UserRoleRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_assignment(self, user_id: int, role_id: int) -> UserRoleEntity | None:
        assignment = (
            self.db.query(UserRoleModel)
            .filter(UserRoleModel.user_id == user_id, UserRoleModel.role_id == role_id)
            .first()
        )
        if assignment is None:
            return None
        return self._to_entity(assignment)

    def assign_role(self, *, user_id: int, role_id: int) -> UserRoleEntity:
        assignment = UserRoleModel(user_id=user_id, role_id=role_id)
        self.db.add(assignment)
        self.db.commit()
        self.db.refresh(assignment)
        return self._to_entity(assignment)

    def get_roles_for_user(self, user_id: int) -> list[RoleEntity]:
        roles = (
            self.db.query(RoleModel)
            .join(UserRoleModel, UserRoleModel.role_id == RoleModel.role_id)
            .filter(UserRoleModel.user_id == user_id)
            .order_by(RoleModel.role_id)
            .all()
        )
        return [
            RoleEntity(
                role_id=role.role_id,
                name=role.name,
                description=role.description,
                is_active=role.is_active,
                created_at=role.created_at,
                updated_at=role.updated_at,
            )
            for role in roles
        ]

    @staticmethod
    def _to_entity(assignment: UserRoleModel) -> UserRoleEntity:
        return UserRoleEntity(
            user_role_id=assignment.user_role_id,
            user_id=assignment.user_id,
            role_id=assignment.role_id,
            assigned_at=assignment.assigned_at,
        )
