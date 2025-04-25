from typing import TYPE_CHECKING, List, Optional, Dict, Any

from fastapi import (
    APIRouter,
    Form,
    Depends,
    status,
    Request,
    Query,
)
from fastapi_filter import FilterDepends
from sqlalchemy.ext.asyncio import AsyncSession

from src.scrypts.pagination import paginate_result
from .service import PostsService
from .schemas import (
    PostRead,
    PostShort,
)
from .filters import PostFilter
from src.api.v1.users.user.dependencies import current_superuser, current_user
from src.core.config import DBConfigurer, RateLimiter
from ...store.products.schemas import ProductShort
from src.api.v1.users.user.schemas import UserPublicExtended
from . import dependencies as deps

if TYPE_CHECKING:
    from src.core.models import(
        User,
        Vote,
    )


RELATIONS_LIST = [
    {
        "name": "user",
        "usage": "/{id}/user",
        "conditions": "private"
    },
    {
        "name": "product",
        "usage": "/{id}/product",
        "conditions": "public"
    },
]


router = APIRouter()


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


# 3
@router.get(
    "",
    response_model=List[PostShort],
    status_code=status.HTTP_200_OK,
    description="Get items list"
)
@RateLimiter.rate_limit()
async def get_all(
        request: Request,
        page: int = Query(1, gt=0),
        size: int = Query(10, gt=0),
        filter_model: PostFilter = FilterDepends(PostFilter),
        session: AsyncSession = Depends(DBConfigurer.session_getter)
):
    service: PostsService = PostsService(
        session=session
    )
    result_full = await service.get_all(filter_model=filter_model)
    return await paginate_result(
        query_list=result_full,
        page=page,
        size=size,
    )


# 4
@router.get(
    "/full",
    dependencies=[Depends(current_superuser),],
    response_model=List[PostRead],
    status_code=status.HTTP_200_OK,
    description="Get full items list (for superuser only)"
)
# @RateLimiter.rate_limit()
# no rate limit for superuser
async def get_all_full(
        request: Request,
        page: int = Query(1, gt=0),
        size: int = Query(10, gt=0),
        filter_model: PostFilter = FilterDepends(PostFilter),
        session: AsyncSession = Depends(DBConfigurer.session_getter)
):
    service: PostsService = PostsService(
        session=session
    )
    result_full = await service.get_all_full(filter_model=filter_model)
    return await paginate_result(
        query_list=result_full,
        page=page,
        size=size,
    )


# 5
@router.get(
    "/{id}",
    status_code=status.HTTP_200_OK,
    response_model=PostShort,
    description="Get item by id"
)
@RateLimiter.rate_limit()
async def get_one(
        request: Request,
        id: int,
        session: AsyncSession = Depends(DBConfigurer.session_getter)
):
    service: PostsService = PostsService(
        session=session
    )
    return await service.get_one(
        id=id,
    )


# 6
@router.get(
    "/{id}/full",
    dependencies=[Depends(current_superuser),],
    status_code=status.HTTP_200_OK,
    response_model=PostRead,
    description="Get full item by id (for superuser only)"
)
# @RateLimiter.rate_limit()
# no rate limit for superuser
async def get_one_full(
        request: Request,
        id: int,
        session: AsyncSession = Depends(DBConfigurer.session_getter)
):
    service: PostsService = PostsService(
        session=session
    )
    return await service.get_one_complex(
        id=id,
        maximized=True
    )
