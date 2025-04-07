from fastapi import (
    APIRouter,
    status,
    Request,
    Response, Depends, Body,
)
from fastapi_users import BaseUserManager, models, exceptions
from pydantic import EmailStr

from src.api.v1.auth.backend import (
    fastapi_users,
    auth_backend,
)
from src.api.v1.auth.dependencies import get_user_manager
from .service import AuthService
from ..users.schemas import (
    UserRead,
    UserCreate,
)


router = APIRouter()

# /login [POST]
# /logout [POST]
router.include_router(
    fastapi_users.get_auth_router(auth_backend),
)


# /register
router.include_router(
    fastapi_users.get_register_router(UserRead, UserCreate),
)


# /request-verify-token
# /verify
@router.post(
        "/request-verify-token",
        status_code=status.HTTP_202_ACCEPTED,
        name="verify:request-token",
    )
async def request_verify_token(
    request: Request,
    email: EmailStr = Body(..., embed=True),
    user_manager: BaseUserManager[models.UP, models.ID] = Depends(get_user_manager),
):
    service = AuthService(
        user_manager=user_manager,
    )
    return await service.request_verify_token(
        request=request,
        email=email
    )


router.include_router(
    fastapi_users.get_verify_router(UserRead),
)


# /forgot-password
# /reset-password
router.include_router(
    fastapi_users.get_reset_password_router(),
)