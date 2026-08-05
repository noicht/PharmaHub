from sqlalchemy.orm import Session

from app.db.models.role import RoleModel
from app.domain.roles import RoleEntity


class RoleRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, role_id: int) -> RoleEntity | None:
        role = self.db.get(RoleModel, role_id)
        if role is None:
            return None
        return self._to_entity(role)

    def get_by_name(self, name: str) -> RoleEntity | None:
        role = self.db.query(RoleModel).filter(RoleModel.name == name).first()
        if role is None:
            return None
        return self._to_entity(role)

    def get_all(self) -> list[RoleEntity]:
        roles = self.db.query(RoleModel).order_by(RoleModel.role_id).all()
        return [self._to_entity(role) for role in roles]

    def create_role(self, *, name: str, description: str = "") -> RoleEntity:
        role = RoleModel(name=name, description=description)
        self.db.add(role)
        self.db.commit()
        self.db.refresh(role)
        return self._to_entity(role)

    @staticmethod
    def _to_entity(role: RoleModel) -> RoleEntity:
        return RoleEntity(
            role_id=role.role_id,
            name=role.name,
            description=role.description,
            is_active=role.is_active,
            created_at=role.created_at,
            updated_at=role.updated_at,
        )
