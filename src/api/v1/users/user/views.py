from typing import Dict, Any

from fastapi import APIRouter, Depends, Query, Request, status
from fastapi.responses import ORJSONResponse
from fastapi_filter import FilterDepends
from fastapi_users import BaseUserManager, models, schemas
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.v1.auth.backend import fastapi_users as fastapi_users_custom
from .dependencies import (
    current_superuser,
    current_user,
)
from .schemas import (
    UserRead,
    UserUpdate,
)
from src.core.config import DBConfigurer, RateLimiter
from src.scrypts.pagination import paginate_result

from .service import UsersService
from .filters import UserFilter


from src.api.v1.store.votes.schemas import (
    VoteShort,
)
from src.api.v1.posts.post.schemas import (
    PostShort,
)

from src.api.v1.auth.dependencies import get_user_manager


router = APIRouter()


RELATIONS_LIST = [
    {
        "name": "votes",
        "usage": "/me/votes",
        "conditions": "public"
    },
    {
        "name": "votes",
        "usage": "/{id}/votes",
        "conditions": "private"
    },
    {
        "name": "posts",
        "usage": "/me/posts",
        "conditions": "public"
    },
    {
        "name": "posts",
        "usage": "/{id}/posts",
        "conditions": "private"
    },
]


# 1
@router.get(
    "/routes",
    status_code=status.HTTP_200_OK,
    description="Getting all the routes of the current branch",
)
@RateLimiter.rate_limit()
async def get_routes(
        request: Request,
) -> list[Dict[str, Any]]:
    from src.scrypts.get_routes import get_routes as scrypt_get_routes
    return await scrypt_get_routes(
        application=router,
        tags=False,
        desc=True
    )


# 2
@router.get(
    "/relations",
    status_code=status.HTTP_200_OK,
    description="Getting the relations info for the branch items"
)
@RateLimiter.rate_limit()
async def get_relations(
        request: Request,
) -> list[Dict[str, Any]]:
    return RELATIONS_LIST


@router.get(
    "/me",
    response_model=UserRead,
    name="users:current_user",
    responses={
        status.HTTP_401_UNAUTHORIZED: {
            "description": "Missing token or inactive user.",
        },
    },
    description="Getting personal information"
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
    description="Changing personal information"
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


# 3
@router.get(
    '',
    response_model=list[UserRead],
    dependencies=[Depends(current_superuser),],
    description="Getting the list of registered users"
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


# 4_1
@router.get(
    "/me/votes",
    status_code=status.HTTP_200_OK,
    description="Getting the list of personal votes"
)
@RateLimiter.rate_limit()
async def get_relations_votes(
        request: Request,
        page: int = Query(1, gt=0),
        size: int = Query(10, gt=0),
        user: models.UP = Depends(current_user),
        session: AsyncSession = Depends(DBConfigurer.session_getter),
        user_manager: BaseUserManager[models.UP, models.ID] = Depends(get_user_manager),
) -> list[VoteShort] | ORJSONResponse:
    service: UsersService = UsersService(
        session=session,
        user_manager=user_manager
    )
    result_full = await service.get_one_complex(
        id=user.id,
        maximized=False,
        relations=['votes',]
    )
    if isinstance(result_full, ORJSONResponse):
        return result_full
    return await paginate_result(
        query_list=result_full,
        page=page,
        size=size,
    )


# 4_2
@router.get(
    "/{id}/votes",
    dependencies=[Depends(current_superuser,)],
    status_code=status.HTTP_200_OK,
    description="Getting the list of personal votes of user by id"
)
# @RateLimiter.rate_limit()
# no rate limit for superuser
async def get_relations_votes_by_id(
        request: Request,
        id: int,
        page: int = Query(1, gt=0),
        size: int = Query(10, gt=0),
        session: AsyncSession = Depends(DBConfigurer.session_getter),
        user_manager: BaseUserManager[models.UP, models.ID] = Depends(get_user_manager),
) -> list[VoteShort] | ORJSONResponse:
    service: UsersService = UsersService(
        session=session,
        user_manager=user_manager
    )
    result_full = await service.get_one_complex(
        id=id,
        maximized=False,
        relations=['votes',]
    )
    if isinstance(result_full, ORJSONResponse):
        return result_full
    return await paginate_result(
        query_list=result_full,
        page=page,
        size=size,
    )


# 5_1
@router.get(
    "/me/posts",
    status_code=status.HTTP_200_OK,
    description="Getting the list of personal posts"
)
@RateLimiter.rate_limit()
async def get_relations_posts(
        request: Request,
        page: int = Query(1, gt=0),
        size: int = Query(10, gt=0),
        user: models.UP = Depends(current_user),
        session: AsyncSession = Depends(DBConfigurer.session_getter),
        user_manager: BaseUserManager[models.UP, models.ID] = Depends(get_user_manager),
) -> list[PostShort] | ORJSONResponse:
    service: UsersService = UsersService(
        session=session,
        user_manager=user_manager
    )
    result_full = await service.get_one_complex(
        id=user.id,
        maximized=False,
        relations=['posts',]
    )
    if isinstance(result_full, ORJSONResponse):
        return result_full
    return await paginate_result(
        query_list=result_full,
        page=page,
        size=size,
    )


# 5_2
@router.get(
    "/{id}/posts",
    dependencies=[Depends(current_superuser,)],
    status_code=status.HTTP_200_OK,
    description="Getting the list of personal posts of user by id"
)
# @RateLimiter.rate_limit()
# no rate limit for superuser
async def get_relations_posts_by_id(
        request: Request,
        id: int,
        page: int = Query(1, gt=0),
        size: int = Query(10, gt=0),
        session: AsyncSession = Depends(DBConfigurer.session_getter),
        user_manager: BaseUserManager[models.UP, models.ID] = Depends(get_user_manager),
) -> list[PostShort] | ORJSONResponse:
    service: UsersService = UsersService(
        session=session,
        user_manager=user_manager
    )
    result_full = await service.get_one_complex(
        id=id,
        maximized=False,
        relations=['posts',]
    )
    if isinstance(result_full, ORJSONResponse):
        return result_full
    return await paginate_result(
        query_list=result_full,
        page=page,
        size=size,
    )
