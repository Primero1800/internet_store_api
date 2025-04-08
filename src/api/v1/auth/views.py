import logging

from fastapi import (
    APIRouter,
    status,
    Request,
    Response, Depends, Body,
)
from fastapi_users import BaseUserManager, models, exceptions
from fastapi_users.router import ErrorCode
from fastapi_users.router.common import ErrorModel
from fastapi_users.router.reset import RESET_PASSWORD_RESPONSES
from pydantic import EmailStr

from src.api.v1.auth.backend import (
    fastapi_users,
    auth_backend,
)
from src.api.v1.auth.dependencies import get_user_manager
from src.core.settings import settings
from .service import AuthService
from ..users.schemas import (
    UserRead,
    UserCreate,
)


logger = logging.getLogger(__name__)

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


@router.post(
    "/verify",
    response_model=UserRead,
    name="verify:verify",
    responses={
        status.HTTP_400_BAD_REQUEST: {
            "model": ErrorModel,
            "content": {
                "application/json": {
                    "examples": {
                        ErrorCode.VERIFY_USER_BAD_TOKEN: {
                            "summary": "Bad token, not existing user or"
                            "not the e-mail currently set for the user.",
                            "value": {"detail": ErrorCode.VERIFY_USER_BAD_TOKEN},
                        },
                        ErrorCode.VERIFY_USER_ALREADY_VERIFIED: {
                            "summary": "The user is already verified.",
                            "value": {
                                "detail": ErrorCode.VERIFY_USER_ALREADY_VERIFIED
                            },
                        },
                    }
                }
            },
        }
    },
)
async def verify(
    request: Request,
    token: str = Body(..., embed=True),
    user_manager: BaseUserManager[models.UP, models.ID] = Depends(get_user_manager),
):
    service = AuthService(
        user_manager=user_manager
    )
    return await service.verify(
        request=request,
        token=token,
        schema=UserRead,
    )


# /forgot-password
# /reset-password
router.include_router(
    fastapi_users.get_reset_password_router(),
)


@router.get(
    "/verify-hook",
    name="verify:verify-token-hook",
    response_model=UserRead,
    include_in_schema=False,
)
async def hook_verify(
        request: Request,
        path: str,
        user_manager: BaseUserManager[models.UP, models.ID] = Depends(get_user_manager),
) -> UserRead:

    logger.warning("In verify-hook: got token from outer link")

    service = AuthService(
        user_manager=user_manager
    )
    return await service.verify(
        request=request,
        token=path,
        schema=UserRead,
    )


@router.post(
    "/reset-password-hook",
    name="verify:reset-password-hook",
    responses=RESET_PASSWORD_RESPONSES,
    include_in_schema=False
)
async def reset_password_hook(
        request: Request,
        path: str,
        password: str = Body(...),
        user_manager: BaseUserManager[models.UP, models.ID] = Depends(get_user_manager),
):
    logger.warning("In reset-password-hook: got token from outer link")
    service = AuthService(
        user_manager=user_manager
    )
    return await service.reset_password(
        request=request,
        token=path,
        password=password,
    )
