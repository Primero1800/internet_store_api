from fastapi import APIRouter, Depends, Query, Request, status
from fastapi_filter import FilterDepends
from fastapi_users import BaseUserManager, models, schemas
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.v1.auth.backend import fastapi_users as fastapi_users_custom
from src.api.v1.users.dependencies import (
    current_superuser,
    current_user,
)
from src.api.v1.users.schemas import (
    UserRead,
    UserUpdate,
)
from src.core.config import DBConfigurer, RateLimiter
from src.scrypts.pagination import paginate_result

from .service import UsersService
from .filters import UserFilter

from ..auth.dependencies import get_user_manager

router = APIRouter()


@router.get(
    "/me",
    response_model=UserRead,
    name="users:current_user",
    responses={
        status.HTTP_401_UNAUTHORIZED: {
            "description": "Missing token or inactive user.",
        },
    },
)
@RateLimiter.rate_limit()
async def me(
        request: Request,
        user: models.UP = Depends(current_user),
):
    return schemas.model_validate(UserRead, user)


@router.patch(
    "/me",
    response_model=UserRead,
    status_code=status.HTTP_200_OK,
    name="users:patch_current_user",
)
@RateLimiter.rate_limit()
async def update_me(
    request: Request,
    user_update: UserUpdate,
    user: models.UP = Depends(current_user),
    user_manager: BaseUserManager[models.UP, models.ID] = Depends(get_user_manager),
):
    service: UsersService = UsersService(
        user_manager=user_manager
    )
    return await service.update_me(
        request=request,
        user_update=user_update,
        user=user,
    )


# /api/v1/users/me GET
# /api/v1/users/me PATCH
# /api/v1/users/{id} GET
# /api/v1/users/{id} PATCH
# /api/v1/users/{id} DELETE
router.include_router(
    fastapi_users_custom.get_users_router(
        UserRead, UserUpdate
    ),
)


@router.get(
    '/',
    response_model=list[UserRead],
    dependencies=[Depends(current_superuser),],
)
# No rate limit for superuser
async def get_users(
        request: Request,
        page: int = Query(1, gt=0),
        size: int = Query(10, gt=0),
        user_filter: UserFilter = FilterDepends(UserFilter),
        session: AsyncSession = Depends(DBConfigurer.session_getter),
        user_manager: BaseUserManager[models.UP, models.ID] = Depends(get_user_manager),
) -> list[UserRead]:

    service = UsersService(
        user_manager=user_manager,
        session=session,
    )
    result_full = await service.get_all_users(
        filter_model=user_filter,
    )

    return await paginate_result(
        query_list=result_full,
        page=page,
        size=size,
    )
