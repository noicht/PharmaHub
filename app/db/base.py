from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    pass


def init_db() -> None:
    from app.db.models import role, user, user_role  # noqa: F401
    from app.db.session import engine

    Base.metadata.create_all(bind=engine)
