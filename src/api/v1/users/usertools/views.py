from typing import Dict, Any, TYPE_CHECKING

from fastapi import APIRouter, Depends, Query, Request, status, Form
from fastapi_filter import FilterDepends
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.v1.users.user.dependencies import (
    current_superuser,
    current_user,
)
from src.api.v1.users.user.schemas import (
    UserPublicExtended,
)
from src.core.config import DBConfigurer, RateLimiter
from src.scrypts.pagination import paginate_result

from .service import UserToolsService
from .filters import UserToolsFilter
from . import dependencies as deps
from ...store.products.dependencies import get_one_simple as deps_products_get_one_simple
from . import utils


from .schemas import (
    UserToolsShort,
    UserToolsRead,
)

if TYPE_CHECKING:
    from src.core.models import (
        UserTools,
        User,
        Product,
    )


router = APIRouter()


RELATIONS_LIST = [
    {
        "name": "user",
        "usage": "/me/user",
        "conditions": "public"
    },
    {
        "name": "user",
        "usage": "/{id}/user",
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


# 3
@router.get(
    "",
    dependencies=[Depends(current_superuser)],
    response_model=list[UserToolsShort],
    status_code=status.HTTP_200_OK,
    description="Get the list of the all items (for superuser only)"
)
# @RateLimiter.rate_limit()
# no rate limit for superuser
async def get_all(
        request: Request,
        page: int = Query(1, gt=0),
        size: int = Query(10, gt=0),
        filter_model: UserToolsFilter = FilterDepends(UserToolsFilter),
        session: AsyncSession = Depends(DBConfigurer.session_getter)
):
    service: UserToolsService = UserToolsService(
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
    response_model=list[UserToolsRead],
    status_code=status.HTTP_200_OK,
    description="Get the list of the all items with product relations (for superuser only)"
)
# @RateLimiter.rate_limit()
# no rate limit for superuser
async def get_all_full(
        request: Request,
        page: int = Query(1, gt=0),
        size: int = Query(10, gt=0),
        filter_model: UserToolsFilter = FilterDepends(UserToolsFilter),
        session: AsyncSession = Depends(DBConfigurer.session_getter)
):
    service: UserToolsService = UserToolsService(
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
    "/{user_id}",
    dependencies=[Depends(current_superuser), ],
    status_code=status.HTTP_200_OK,
    response_model=UserToolsShort,
    description="Get item of the user by user_id"
)
# @RateLimiter.rate_limit()
# no rate limit for superuser
async def get_one(
        request: Request,
        user_id: int,
        session: AsyncSession = Depends(DBConfigurer.session_getter)
):
    service: UserToolsService = UserToolsService(
        session=session
    )
    return await service.get_one(
        user_id=user_id
    )


# 6
@router.get(
    "/{user_id}/full",
    dependencies=[Depends(current_superuser), ],
    status_code=status.HTTP_200_OK,
    response_model=UserToolsRead,
    description="Get item of the user by user_id with all relations (for superuser only)"
)
# @RateLimiter.rate_limit()
# no rate limit for superuser
async def get_one_complex(
        request: Request,
        user_id: int,
        session: AsyncSession = Depends(DBConfigurer.session_getter)
):
    service: UserToolsService = UserToolsService(
        session=session
    )
    return await service.get_one_complex(
        user_id=user_id
    )


# 7
@router.post(
    "",
    dependencies=[Depends(current_superuser),],
    status_code=status.HTTP_201_CREATED,
    response_model=UserToolsRead,
    description="Create item for existing user (for superuser only)"
)
# @RateLimiter.rate_limit()
# no rate limit for superuser
async def create_one(
        request: Request,
        user_id: int = Form(gt=0),
        session: AsyncSession = Depends(DBConfigurer.session_getter)
) -> UserToolsRead:

    service: UserToolsService = UserToolsService(
        session=session
    )
    return await service.create_one(
        user_id=user_id,
    )


# 8
@router.delete(
    "/{user_id}",
    dependencies=[Depends(current_superuser), ],
    status_code=status.HTTP_204_NO_CONTENT,
    description="Delete item of the user by user_id (for superuser only)"
)
# @RateLimiter.rate_limit()
# no rate limit for superuser
async def delete_one(
        request: Request,
        orm_model: "UserTools" = Depends(deps.get_one),
        session: AsyncSession = Depends(DBConfigurer.session_getter),
):
    service: UserToolsService = UserToolsService(
        session=session
    )
    return await service.delete_one(orm_model)


# 10
@router.put(
    "",
    dependencies=[Depends(current_superuser),],
    status_code=status.HTTP_200_OK,
    response_model=UserToolsRead,
    description="Edit item for existing product (for superuser only)"
)
# @RateLimiter.rate_limit()
# no rate limit for superuser
async def edit_one(
        request: Request,
        orm_model: "UserTools" = Depends(deps.get_one),
        user_id: int = Form(gt=0),
        session: AsyncSession = Depends(DBConfigurer.session_getter)
) -> UserToolsRead:

    service: UserToolsService = UserToolsService(
        session=session
    )
    return await service.edit_one(
        orm_model=orm_model,
        user_id=user_id,
    )


# 11_1
@router.get(
    "/me/user",
    status_code=status.HTTP_200_OK,
    response_model=UserPublicExtended,
    description="Get the relations user of usertools of current user"
)
# @RateLimiter.rate_limit()
# no rate limit for superuser
async def get_one_relations_user_me(
        request: Request,
        user: "User" = Depends(current_user),
        session: AsyncSession = Depends(DBConfigurer.session_getter)
):
    service: UserToolsService = UserToolsService(
        session=session
    )
    return await service.get_one_complex(
        user_id=user.id,
        maximized=False,
        relations=['user']
    )


# 11_2
@router.get(
    "/{user_id}/user",
    dependencies=[Depends(current_superuser), ],
    status_code=status.HTTP_200_OK,
    response_model=UserPublicExtended,
    description="Get the relations user of usertools by user_id"
)
@RateLimiter.rate_limit()
async def get_one_relations_user_id(
        request: Request,
        user_id: int,
        session: AsyncSession = Depends(DBConfigurer.session_getter)
):
    service: UserToolsService = UserToolsService(
        session=session
    )
    return await service.get_one_complex(
        user_id=user_id,
        maximized=False,
        relations=['user']
    )


# 12_1
@router.post(
    "/get-or-create/me",
    status_code=status.HTTP_201_CREATED,
    response_model=UserToolsShort,
    description="Get the usertools by user_id or creating empty one if not exists"
)
@RateLimiter.rate_limit()
async def get_one_or_create(
        request: Request,
        usertools: "UserTools" = Depends(deps.get_or_create_usertools),
):
    return await utils.get_short_schema_from_orm(usertools)


# 12_2
@router.post(
    "/get-or-create/{user_id}",
    dependencies=[Depends(current_superuser),],
    status_code=status.HTTP_201_CREATED,
    response_model=UserToolsShort,
    description="Get the usertools by user_id or creating empty one if not exists"
)
# @RateLimiter.rate_limit()
# no rate limit for superuser
async def get_one_or_create(
        request: Request,
        user_id: int,
        session: AsyncSession = Depends(DBConfigurer.session_getter)
):
    service: UserToolsService = UserToolsService(
        session=session
    )
    return await service.get_or_create(
        user_id=user_id,
        to_schema=True
    )


# 13_1
@router.post(
    "/me/wishlist-add/{product_id}",
    status_code=status.HTTP_200_OK,
    response_model=UserToolsShort,
    description="Add item by product_id to personal wishlist"
)
@RateLimiter.rate_limit()
async def add_to_wishlist(
        request: Request,
        usertools: "UserTools" = Depends(deps.get_or_create_usertools),
        product: "Product" = Depends(deps_products_get_one_simple),
        session: AsyncSession = Depends(DBConfigurer.session_getter)
):
    service: UserToolsService = UserToolsService(
        session=session
    )
    return await service.add_to_list(
        usertools=usertools,
        product=product,
        add_to='w',
        to_schema=True,
    )


# 13_2
@router.post(
    "/me/comparison-add/{product_id}",
    status_code=status.HTTP_200_OK,
    response_model=UserToolsShort,
    description="Add item by product_id to personal comparison list"
)
@RateLimiter.rate_limit()
async def add_to_comparison(
        request: Request,
        usertools: "UserTools" = Depends(deps.get_or_create_usertools),
        product: "Product" = Depends(deps_products_get_one_simple),
        session: AsyncSession = Depends(DBConfigurer.session_getter)
):
    service: UserToolsService = UserToolsService(
        session=session
    )
    return await service.add_to_list(
        usertools=usertools,
        product=product,
        add_to='c',
        to_schema=True,
    )


# 13_3
@router.post(
    "/me/recently-viewed-add/{product_id}",
    status_code=status.HTTP_200_OK,
    response_model=UserToolsShort,
    description="Add item by product_id to personal recently viewed list"
)
@RateLimiter.rate_limit()
async def add_to_comparison(
        request: Request,
        usertools: "UserTools" = Depends(deps.get_or_create_usertools),
        product: "Product" = Depends(deps_products_get_one_simple),
        session: AsyncSession = Depends(DBConfigurer.session_getter)
):
    service: UserToolsService = UserToolsService(
        session=session
    )
    return await service.add_to_list(
        usertools=usertools,
        product=product,
        to_schema=True,
    )


# 14_1
@router.post(
    "/me/wishlist-del/{product_id}",
    status_code=status.HTTP_200_OK,
    response_model=UserToolsShort,
    description="Remove item by product_id from personal wishlist"
)
@RateLimiter.rate_limit()
async def del_from_wishlist(
        request: Request,
        product_id: int,
        usertools: "UserTools" = Depends(deps.get_or_create_usertools),
        session: AsyncSession = Depends(DBConfigurer.session_getter)
):
    service: UserToolsService = UserToolsService(
        session=session
    )
    return await service.del_from_list(
        usertools=usertools,
        product_id=product_id,
        del_from='w',
        to_schema=True,
    )


# 14_2
@router.post(
    "/me/comparison-del/{product_id}",
    status_code=status.HTTP_200_OK,
    response_model=UserToolsShort,
    description="Remove item by product_id from personal comparison list"
)
@RateLimiter.rate_limit()
async def del_from_comparison(
        request: Request,
        product_id: int,
        usertools: "UserTools" = Depends(deps.get_or_create_usertools),
        session: AsyncSession = Depends(DBConfigurer.session_getter)
):
    service: UserToolsService = UserToolsService(
        session=session
    )
    return await service.del_from_list(
        usertools=usertools,
        product_id=product_id,
        del_from='c',
        to_schema=True,
    )


# 14_3
@router.post(
    "/me/recently-viewed-del/{product_id}",
    status_code=status.HTTP_200_OK,
    response_model=UserToolsShort,
    description="remove item by product_id from personal recently viewed list"
)
@RateLimiter.rate_limit()
async def del_from_recently_viewed(
        request: Request,
        product_id: int,
        usertools: "UserTools" = Depends(deps.get_or_create_usertools),
        session: AsyncSession = Depends(DBConfigurer.session_getter)
):
    service: UserToolsService = UserToolsService(
        session=session
    )
    return await service.del_from_list(
        usertools=usertools,
        product_id=product_id,
        to_schema=True,
    )
