from fastapi import APIRouter

from app.auth import auth_backend, fastapi_users
from app.schemas import UserCreate, UserRead, UserUpdate

router = APIRouter(prefix="/auth", tags=["auth"])

# Include auth routes from fastapi-users
router.include_router(
    fastapi_users.get_auth_router(auth_backend),
    prefix="/jwt",
)

router.include_router(
    fastapi_users.get_register_router(UserRead, UserCreate),
)

router.include_router(
    fastapi_users.get_reset_password_router(),
)

router.include_router(
    fastapi_users.get_verify_router(UserRead),
)

# Users management routes
users_router = APIRouter(prefix="/users", tags=["users"])

users_router.include_router(
    fastapi_users.get_users_router(UserRead, UserUpdate),
)
