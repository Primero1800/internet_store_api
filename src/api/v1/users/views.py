from typing import Optional

from fastapi import APIRouter, Depends, Query
from fastapi_users import BaseUserManager, models
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.v1.auth.backend import fastapi_users
from src.api.v1.users.dependencies import current_superuser
from src.api.v1.users.schemas import (
    UserRead,
    UserUpdate,
)
from src.core.config import DBConfigurer
from src.scrypts.pagination import paginate_result

from .service import UsersService
from ..auth.dependencies import get_user_manager

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


@router.get(
    '/',
    response_model=list[UserRead],
    dependencies=[Depends(current_superuser),],
)
async def get_users(
        page: int = Query(1, gt=0),
        size: int = Query(10, gt=0),
        sort_by: Optional[str] = None,
        # user_filter: UserFilter = FilterDepends(UserFilter),
        session: AsyncSession = Depends(DBConfigurer.session_getter),
        user_manager: BaseUserManager[models.UP, models.ID] = Depends(get_user_manager),
) -> list[UserRead]:

    service = UsersService(
        user_manager=user_manager,
        session=session,
    )
    result_full = await service.get_all_users(
        # filter_model=user_filter,
    )

    return await paginate_result(
        query_list=result_full,
        page=page,
        size=size,
        sort_by=sort_by,
    )


