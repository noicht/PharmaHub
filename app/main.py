from fastapi import FastAPI, Response, status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError

from app.core.config import get_settings
from app.db.base import init_db
from app.db.session import SessionLocal
from app.routers.auth_router import auth_router
from app.routers.roles_router import role_router
from app.routers.users_router import user_router


settings = get_settings()
app = FastAPI(title=settings.app_name, description="API for pharmaceutical management", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.frontend_url],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def startup_event() -> None:
    init_db()


app.include_router(auth_router)
app.include_router(user_router)
app.include_router(role_router)


@app.get("/")
def read_root():
    return {"message": f"Welcome to {settings.app_name}", "environment": settings.environment}


@app.get("/health/live")
def liveness_check():
    return {"status": "alive"}


@app.get("/health/ready")
def readiness_check(response: Response):
    try:
        with SessionLocal() as session:
            session.execute(text("SELECT 1"))
    except SQLAlchemyError as exc:
        response.status_code = status.HTTP_503_SERVICE_UNAVAILABLE
        return {"status": "unhealthy", "reason": str(exc)}

    return {"status": "healthy"}
