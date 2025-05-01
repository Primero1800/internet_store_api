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
from .service import CartsService
from .schemas import (
    CartRead,
    CartShort, CartItemShort, CartItemRead,
)
from .filters import CartFilter
from src.api.v1.users.user.dependencies import (
    current_superuser,
    current_user,
    current_user_or_none,
)
from src.core.config import DBConfigurer, RateLimiter
from ..store.products.schemas import ProductShort
from src.api.v1.users.user.schemas import UserPublicExtended
from . import dependencies as deps
from . import utils

if TYPE_CHECKING:
    from src.core.models import(
        User,
        Cart,
        CartItem,
    )


RELATIONS_LIST = [
    {
        "name": "user",
        "usage": "/{id}/user",
        "conditions": "private"
    },
    {
        "name": "user",
        "usage": "/me/user",
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
    dependencies=[Depends(current_superuser),],
    response_model=List[CartShort],
    status_code=status.HTTP_200_OK,
    description="Get items list (for superuser only)"
)
# @RateLimiter.rate_limit()
# no rate limit for superuser
async def get_all(
        request: Request,
        page: int = Query(1, gt=0),
        size: int = Query(10, gt=0),
        user_is_registered: Optional[bool] = Query(default=None, description="Filter carts of registered users"),
        filter_model: CartFilter = FilterDepends(CartFilter),
        session: AsyncSession = Depends(DBConfigurer.session_getter)
):
    service: CartsService = CartsService(
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
    response_model=List[CartRead],
    status_code=status.HTTP_200_OK,
    description="Get full items list (for superuser only)"
)
# @RateLimiter.rate_limit()
# no rate limit for superuser
async def get_all_full(
        request: Request,
        page: int = Query(1, gt=0),
        size: int = Query(10, gt=0),
        user_is_registered: Optional[bool] = Query(default=None, description="Filter carts of registered users"),
        filter_model: CartFilter = FilterDepends(CartFilter),
        session: AsyncSession = Depends(DBConfigurer.session_getter)
):
    service: CartsService = CartsService(
        session=session
    )
    result_full = await service.get_all_full(filter_model=filter_model)
    return await paginate_result(
        query_list=result_full,
        page=page,
        size=size,
    )


# 5_1
@router.get(
    "/me",
    status_code=status.HTTP_200_OK,
    response_model=CartShort,
    description="Get personal item"
)
@RateLimiter.rate_limit()
async def get_one_of_me(
        request: Request,
        user: "User" = Depends(current_user),
        session: AsyncSession = Depends(DBConfigurer.session_getter)
):
    service: CartsService = CartsService(
        session=session
    )
    return await service.get_one(
        id=user.id,
    )


# 5_2
@router.get(
    "/{id}",
    dependencies=[Depends(current_superuser), ],
    status_code=status.HTTP_200_OK,
    response_model=CartShort,
    description="Get item by id (for superuser only)"
)
# @RateLimiter.rate_limit()
# no rate limit for superuser
async def get_one_by_id(
        request: Request,
        id: int,
        session: AsyncSession = Depends(DBConfigurer.session_getter)
):
    service: CartsService = CartsService(
        session=session
    )
    return await service.get_one(
        id=id,
    )


# 6_1
@router.get(
    "/me/full",
    status_code=status.HTTP_200_OK,
    response_model=CartRead,
    description="Get personal item"
)
@RateLimiter.rate_limit()
async def get_one_full_of_me(
        request: Request,
        user: "User" = Depends(current_user),
        session: AsyncSession = Depends(DBConfigurer.session_getter)
):
    service: CartsService = CartsService(
        session=session
    )
    return await service.get_one_complex(
        id=user.id,
        maximized=True
    )


# 6_2
@router.get(
    "/{id}/full",
    dependencies=[Depends(current_superuser),],
    status_code=status.HTTP_200_OK,
    response_model=CartRead,
    description="Get full item by id (for superuser only)"
)
# @RateLimiter.rate_limit()
# no rate limit for superuser
async def get_one_full_by_id(
        request: Request,
        id: int,
        session: AsyncSession = Depends(DBConfigurer.session_getter)
):
    service: CartsService = CartsService(
        session=session
    )
    return await service.get_one_complex(
        id=id,
        maximized=True
    )


# 7
@router.post(
    "",
    dependencies=[Depends(current_superuser),],
    status_code=status.HTTP_201_CREATED,
    response_model=CartRead,
    description="Create one item (for superuser only)"
)
# @RateLimiter.rate_limit()
# no rate limit for superuser
async def create_one(
        request: Request,
        id: int = Form(gt=0),
        session: AsyncSession = Depends(DBConfigurer.session_getter)
):

    service: CartsService = CartsService(
        session=session
    )
    return await service.create_one(
        id=id,
    )


# 8
@router.delete(
    "/{id}",
    dependencies=[Depends(current_superuser), ],
    status_code=status.HTTP_204_NO_CONTENT,
    description="Delete item by id (for superuser only)"
)
# @RateLimiter.rate_limit()
# no rate limit for superuser
async def delete_one_by_id(
        request: Request,
        orm_model: "Cart" = Depends(deps.get_one_simple),
        session: AsyncSession = Depends(DBConfigurer.session_getter),
):
    service: CartsService = CartsService(
        session=session
    )
    return await service.delete_one(
        orm_model=orm_model,
    )


# 9
@router.put(
        "/{id}",
        dependencies=[Depends(current_superuser), ],
        status_code=status.HTTP_200_OK,
        response_model=CartRead,
        description="Rearrange item by id (for superuser only)"
)
# @RateLimiter.rate_limit()
# no rate limit for superuser
async def put_one(
        request: Request,
        orm_model: "Cart" = Depends(deps.get_one_simple),
        user_id: int = Form(gt=0),
        session: AsyncSession = Depends(DBConfigurer.session_getter)
):
    service: CartsService = CartsService(
        session=session
    )
    return await service.edit_one(
        orm_model=orm_model,
        id=user_id,
    )


# 10_1
@router.post(
    "/get-or-create/me",
    status_code=status.HTTP_201_CREATED,
    response_model=CartShort,
    description="Get personal item or creating empty one if not exists"
)
@RateLimiter.rate_limit()
async def get_one_of_me_or_create(
        request: Request,
        cart: "Cart" = Depends(deps.get_or_create_cart),
):
    return await utils.get_short_schema_from_orm(cart)


# 10_2
@router.post(
    "/get-or-create/me/full",
    status_code=status.HTTP_201_CREATED,
    response_model=CartRead,
    description="Get personal item full or creating empty one if not exists"
)
@RateLimiter.rate_limit()
async def get_one_full_of_me_or_create(
        request: Request,
        cart: "Cart" = Depends(deps.get_or_create_cart),
):
    return await utils.get_schema_from_orm(cart)


# 10_3
@router.post(
    "/get-or-create/{user_id}",
    dependencies=[Depends(current_superuser),],
    status_code=status.HTTP_201_CREATED,
    response_model=CartShort,
    description="Get the cart by user_id or creating empty one if not exists (for superuser only)"
)
# @RateLimiter.rate_limit()
# no rate limit for superuser
async def get_one_or_create_by_id(
        request: Request,
        user_id: int,
        session: AsyncSession = Depends(DBConfigurer.session_getter)
):
    service: CartsService = CartsService(
        session=session
    )
    return await service.get_or_create(
        user_id=user_id,
        # to_schema=True,
    )


# 10_4
@router.post(
    "/get-or-create/{user_id}/full",
    dependencies=[Depends(current_superuser),],
    status_code=status.HTTP_201_CREATED,
    response_model=CartRead,
    description="Get the item full by user_id or creating empty one if not exists (for superuser only)"
)
# @RateLimiter.rate_limit()
# no rate limit for superuser
async def get_one_full_or_create_by_id(
        request: Request,
        user_id: int,
        session: AsyncSession = Depends(DBConfigurer.session_getter)
):
    service: CartsService = CartsService(
        session=session
    )
    return await service.get_or_create(
        user_id=user_id,
        to_schema=True,
        maximized=True,
    )


# 11_1
@router.post(
    "/get-or-create-item/me",
    status_code=status.HTTP_201_CREATED,
    response_model=CartItemShort,
    description="Get cart_item of personal cart or creating one if not exists"
)
@RateLimiter.rate_limit()
async def get_one_item_of_me_or_create(
        request: Request,
        cart_item: "CartItem" = Depends(deps.get_or_create_cart_item)
):
    return await utils.get_short_item_schema_from_orm(cart_item)


# 11_2
@router.post(
    "/get-or-create-item/me/full",
    status_code=status.HTTP_201_CREATED,
    response_model=CartItemRead,
    description="Get cart_item full of personal cart or creating empty one if not exists"
)
@RateLimiter.rate_limit()
async def get_one_item_full_of_me_or_create(
        request: Request,
        cart_item: "CartItem" = Depends(deps.get_or_create_cart_item)
):
    return await utils.get_item_schema_from_orm(cart_item)


# 11_3
@router.post(
    "/get-or-create-item/{user_id}",
    dependencies=[Depends(current_superuser),],
    status_code=status.HTTP_201_CREATED,
    response_model=CartItemShort,
    description="Get cart_item of user by user_id or creating empty one if not exists (for superuser only)"
)
# @RateLimiter.rate_limit()
# no rate limit for superuser
async def get_one_or_create_by_id(
        request: Request,
        user_id: int,
        product_id: int = Form(gt=0),
        session: AsyncSession = Depends(DBConfigurer.session_getter)
):
    service: CartsService = CartsService(
        session=session
    )
    return await service.get_or_create_item(
        user_id=user_id,
        product_id=product_id,
    )


# 11_4
@router.post(
    "/get-or-create-item/{user_id}/full",
    dependencies=[Depends(current_superuser),],
    status_code=status.HTTP_201_CREATED,
    response_model=CartItemRead,
    description="Get cart_item of user by user_id or creating empty one if not exists (for superuser only)"
)
# @RateLimiter.rate_limit()
# no rate limit for superuser
async def get_one_full_or_create_by_id(
        request: Request,
        user_id: int,
        product_id: int = Form(gt=0),
        session: AsyncSession = Depends(DBConfigurer.session_getter)
):
    service: CartsService = CartsService(
        session=session
    )
    return await service.get_or_create_item(
        user_id=user_id,
        product_id=product_id,
        to_schema=True,
        maximized=True,
    )


# 12_1
@router.post(
    "/clear/me",
    status_code=status.HTTP_200_OK,
    response_model=CartShort,
    description="Clear personal item or creating empty one if not exists"
)
@RateLimiter.rate_limit()
async def clear_me_or_create(
        request: Request,
        cart: "Cart" = Depends(deps.get_or_create_cart),
        session: AsyncSession = Depends(DBConfigurer.session_getter)
):
    service: CartsService = CartsService(
        session=session
    )
    return await service.clear_cart(
        cart=cart
    )


# 12_2
@router.post(
    "/clear/{user_id}",
    dependencies=[Depends(current_superuser),],
    status_code=status.HTTP_200_OK,
    response_model=CartShort,
    description="Clear personal item by user_id or creating empty one if not exists (for superuser only)"
)
# @RateLimiter.rate_limit()
# no rate limit for superuser
async def clear_by_id_or_create(
        request: Request,
        user_id: int,
        session: AsyncSession = Depends(DBConfigurer.session_getter)
):
    service: CartsService = CartsService(
        session=session
    )
    return await service.clear_cart(
        user_id=user_id
    )


# 13_1
@router.post(
    "/change-quantity/me",
    status_code=status.HTTP_200_OK,
    description="Increase or decrease quantity of personal item or creating empty one if not exists"
)
@RateLimiter.rate_limit()
async def change_item_quantity_of_me(
        request: Request,
        delta: Optional[int] = Form(default=None),
        absolute: Optional[int] = Form(ge=0, default=None),
        cart_item: "CartItem" = Depends(deps.get_or_create_cart_item),
        session: AsyncSession = Depends(DBConfigurer.session_getter),
) -> CartItemShort | None:
    service: CartsService = CartsService(
        session=session
    )
    return await service.change_quantity(
        cart_item=cart_item,
        delta=delta,
        absolute=absolute,
    )


# 13_2
@router.post(
    "/change-quantity/{user_id}",
    dependencies=[Depends(current_superuser),],
    status_code=status.HTTP_200_OK,
    description="Increase or decrease quantity of item by user_id or creating empty one if not exists (for superuser only)"
)
# @RateLimiter.rate_limit()
# no rate limit for superuser
async def change_item_quantity_of_user_id(
        request: Request,
        user_id: int,
        product_id: int = Form(gt=0),
        delta: Optional[int] = Form(default=None),
        absolute: Optional[int] = Form(ge=0, default=None),
        session: AsyncSession = Depends(DBConfigurer.session_getter),
) -> CartItemShort | None:
    service: CartsService = CartsService(
        session=session
    )
    return await service.change_quantity(
        user_id=user_id,
        product_id=product_id,
        delta=delta,
        absolute=absolute,
    )
