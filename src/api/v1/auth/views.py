import logging
from typing import Union, TYPE_CHECKING

from fastapi import (
    APIRouter,
    status,
    Request,
    Depends,
    Body,
)
from fastapi.security import OAuth2PasswordRequestForm
from fastapi_users import BaseUserManager, models
from fastapi_users.authentication import Strategy
from fastapi_users.router.reset import RESET_PASSWORD_RESPONSES
from pydantic import EmailStr

from src.api.v1.auth.backend import (
    auth_backend,
)
from src.api.v1.auth.dependencies import get_user_manager
from src.core.config import RateLimiter, DBConfigurer
from src.core.sessions.fastapi_sessions_config import cookie_or_none, SessionData, verifier_or_none
from .service import AuthService
from src.api.v1.users.user.dependencies import current_user_token
from src.api.v1.users.user.schemas import (
    UserRead,
    UserCreate,
)
from ..carts.dependencies import get_or_create_cart_session

if TYPE_CHECKING:
    from src.core.models import Cart
    from src.api.v1.carts.session_cart import SessionCart
    from sqlalchemy.ext.asyncio import AsyncSession

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post(
        "/login",
        name=f"auth:{auth_backend.name}.login",
        dependencies=[Depends(cookie_or_none),],
)
@RateLimiter.rate_limit()
async def login(
    request: Request,
    credentials: OAuth2PasswordRequestForm = Depends(),
    user_manager: BaseUserManager[models.UP, models.ID] = Depends(get_user_manager),
    strategy: Strategy[models.UP, models.ID] = Depends(auth_backend.get_strategy),
    session_cart: Union["Cart", "SessionCart"] = Depends(get_or_create_cart_session),
    session: "AsyncSession" = Depends(DBConfigurer.session_getter),
    session_data: SessionData = Depends(verifier_or_none),
):
    service = AuthService(
        user_manager=user_manager,
        backend=auth_backend,
        session=session,
        session_data=session_data
    )
    return await service.login(
        request=request,
        credentials=credentials,
        strategy=strategy,
        session_cart=session_cart,
    )


@router.post(
    "/logout",
    name=f"auth:{auth_backend.name}.logout",
)
@RateLimiter.rate_limit()
async def logout(
        request: Request,
        user_token: tuple[models.UP, str] = Depends(current_user_token),
        strategy: Strategy[models.UP, models.ID] = Depends(auth_backend.get_strategy),
):
    service: AuthService = AuthService(
        backend=auth_backend,
    )
    return await service.logout(
        token=user_token,
        strategy=strategy,
    )


# /login [POST]
# /logout [POST]
# router.include_router(
#     fastapi_users.get_auth_router(auth_backend),
# )


@router.post(
        "/register",
        response_model=UserRead,
        status_code=status.HTTP_201_CREATED,
        name="register:register",
)
@RateLimiter.rate_limit()
async def register(
    request: Request,
    user_create: UserCreate,
    user_manager: BaseUserManager[models.UP, models.ID] = Depends(get_user_manager),
):
    service: AuthService = AuthService(
        user_manager=user_manager
    )
    return await service.register(
        request=request,
        user_create_schema=user_create,
    )


# /register
# router.include_router(
#     fastapi_users.get_register_router(UserRead, UserCreate),
# )


# /request-verify-token
# /verify
@router.post(
        "/request-verify-token",
        status_code=status.HTTP_202_ACCEPTED,
        name="verify:request-token",
)
@RateLimiter.rate_limit()
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
)
@RateLimiter.rate_limit()
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
    )


@router.post(
        "/forgot-password",
        status_code=status.HTTP_202_ACCEPTED,
        name="reset:forgot_password",
)
async def forgot_password(
    request: Request,
    email: EmailStr = Body(..., embed=True),
    user_manager: BaseUserManager[models.UP, models.ID] = Depends(get_user_manager),
):
    service: AuthService = AuthService(
        user_manager=user_manager
    )
    return await service.forgot_password(
        request=request,
        email=email,
    )


@router.post(
        "/reset-password",
        name="reset:reset_password",
        responses=RESET_PASSWORD_RESPONSES,
        response_model=UserRead,
)
@RateLimiter.rate_limit()
async def reset_password(
    request: Request,
    token: str = Body(...),
    password: str = Body(...),
    user_manager: BaseUserManager[models.UP, models.ID] = Depends(get_user_manager),
):
    service = AuthService(
        user_manager=user_manager
    )
    return await service.reset_password(
        token=token,
        password=password,
        request=request
    )


# /forgot-password
# /reset-password
# router.include_router(
#     fastapi_users.get_reset_password_router(),
# )


@router.get(
    "/verify-hook",
    name="verify:verify-token-hook",
    response_model=UserRead,
    include_in_schema=False,
)
@RateLimiter.rate_limit()
async def hook_verify(
        request: Request,
        path: str,
        user_manager: BaseUserManager[models.UP, models.ID] = Depends(get_user_manager),
):

    logger.warning("In verify-hook: got token from outer link")

    service = AuthService(
        user_manager=user_manager
    )
    return await service.verify(
        request=request,
        token=path,
    )


@router.get(
    "/reset-password-hook",
    name="verify:reset-password-hook",
    responses=RESET_PASSWORD_RESPONSES,
    response_model=UserRead,
    include_in_schema=False,
)
@RateLimiter.rate_limit()
async def reset_password_hook(
        request: Request,
        path: str,
        # password: str = Body(...),
        user_manager: BaseUserManager[models.UP, models.ID] = Depends(get_user_manager),
):
    logger.warning("In reset-password-hook: got token from outer link")
    service = AuthService(
        user_manager=user_manager
    )
    return await service.reset_password(
        request=request,
        token=path,
        password='87654321',
    )
