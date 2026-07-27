from fastapi import FastAPI, Response, status

from app.repositories.users_repository import UserRepository, build_seed_users
from app.routers.users_router import user_router


app = FastAPI(title="PharmaHub API", description="API for pharmaceutical management", version="1.0.0")
app.state.user_repository = UserRepository(seed_users=build_seed_users())

app.include_router(user_router)


@app.get("/")
def read_root():
    return {"message": "Welcome to PharmaHub API"}


@app.get("/health")
def health_check(response: Response):
    db_healthy = True

    if not db_healthy:
        response.status_code = status.HTTP_503_SERVICE_UNAVAILABLE
        return {"status": "unhealthy", "reason": "DB connection failed"}

    return {"status": "healthy"}
