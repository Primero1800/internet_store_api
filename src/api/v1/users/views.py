from fastapi import APIRouter
from src.api.v1.auth.backend import fastapi_users
from src.api.v1.users.schemas import (
    UserRead,
    UserUpdate,
)

router = APIRouter()


# /api/v1/users/me GET
# /api/v1/users/me PATCH
# /api/v1/users/{id} GET
# /api/v1/users/{id} PATCH
# /api/v1/users/{id} DELETE
router.include_router(
    fastapi_users.get_users_router(
        UserRead, UserUpdate
    ),
)




