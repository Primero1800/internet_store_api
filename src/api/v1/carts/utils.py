from typing import TYPE_CHECKING, Optional, Union

from fastapi.responses import ORJSONResponse
from sqlalchemy.ext.asyncio import AsyncSession

from .schemas import (
    CartRead,
    CartShort,
    CartItemRead,
    CartItemShort,
)

if TYPE_CHECKING:
    from src.core.models import (
        Cart,
        CartItem,
        User,
    )
    from src.api.v1.carts.session_cart import SessionCart, SessionCartItem
    from src.core.sessions.fastapi_sessions_config import SessionData


async def get_schema_from_orm(
        orm_model: Union["Cart", "SessionCart"],
        maximized: bool = True,
        relations: list | None = None,
):
    # BRUTE FORCE VARIANT

    dict_to_push_to_schema = orm_model.to_dict()
    if 'user' in dict_to_push_to_schema:
        del dict_to_push_to_schema['user']

    cart_items = None
    if maximized or (relations and 'products' in relations):
        cart_items = []
        for cart_item in orm_model.cart_items:
            cart_items.append(
                await get_item_schema_from_orm(cart_item)
            )
        if relations and 'products' in relations:
            return cart_items

    user_short = None
    if maximized or (relations and 'user' in relations):
        if orm_model.user:
            from src.api.v1.users.user.utils import get_short_schema_from_orm as get_short_user_schema_from_orm
            user_short = await get_short_user_schema_from_orm(orm_model.user)
        if relations and 'user' in relations:
            return user_short

    return CartRead(
        **dict_to_push_to_schema,
        cart_items=cart_items,
        user=user_short
    )


async def get_short_schema_from_orm(
        orm_model: Union["Cart", "SessionCart", ORJSONResponse]
) -> CartShort | ORJSONResponse:

    if isinstance(orm_model, ORJSONResponse):
        return orm_model

    cart_item_shorts = None
    if hasattr(orm_model, "cart_items"):
        cart_item_shorts = []
        for cart_item in orm_model.cart_items:
            cart_item_shorts.append(await get_short_item_schema_from_orm(cart_item))

    # BRUTE FORCE VARIANT
    return CartShort(
        **orm_model.to_dict(),
        cart_items=cart_item_shorts
    )


async def get_short_item_schema_from_orm(
        orm_model: Union["CartItem", "SessionCartItem", dict]
) -> CartItemShort | ORJSONResponse:

    if isinstance(orm_model, ORJSONResponse):
        return orm_model

    if isinstance(orm_model, dict):  # For SessionCartItem
        return CartItemShort(
            **orm_model
        )

    # BRUTE FORCE VARIANT
    return CartItemShort(
        **orm_model.to_dict()
    )


async def get_item_schema_from_orm(
        orm_model: Union["CartItem", "SessionCartItem", dict]
) -> CartItemRead | ORJSONResponse:

    if isinstance(orm_model, ORJSONResponse):
        return orm_model

    if isinstance(orm_model, dict):  # For SessionCartItem straight as dict
        dict_to_push = orm_model
        product = dict_to_push.pop("product")
    elif not orm_model.cart_id:  # For SessionCartItem
        dict_to_push = orm_model.to_dict()
        product = dict_to_push.pop("product")
    else:
        dict_to_push = orm_model.to_dict()
        from ..store.products.utils import get_short_schema_from_orm as get_short_product_schema_from_orm
        product = await get_short_product_schema_from_orm(orm_model.product)

    return CartItemRead(
        **dict_to_push,
        product=product
    )


# /get-or-create/me
# /get-or-create/{user_id}
async def get_or_create(
        user_id: int,
        session: AsyncSession,
) -> "Cart":
    from .service import CartsService
    service = CartsService(
        session=session
    )
    return await service.get_or_create(user_id)


# /get-or-create-item/me
# /get-or-create-item/{user_id}
async def get_or_create_item(
        product_id: int,
        session: AsyncSession,
        user_id: Optional[int] = None,
        cart: Optional["Cart"] = None,
) -> "Cart":
    from .service import CartsService
    service = CartsService(
        session=session
    )
    return await service.get_or_create_item(
        user_id=user_id,
        cart=cart,
        product_id=product_id,
    )


async def serve_carts_after_logging(
        user: "User",
        session_cart: "SessionCart",
        session: AsyncSession,
        session_data: "SessionData",
):
    from .service import CartsService
    service = CartsService(
        session=session,
        session_data=session_data
    )
    user_cart = await service.get_or_create(user_id=user.id)
    await service.sum_carts(
        user_cart=user_cart,
        session_cart=session_cart,
    )


# /me-session/normalize
async def serve_normalize_item_quantity(
        cart: Union["Cart", "SessionCart"],
        session: AsyncSession,
        session_data: "SessionData",
):
    from .service import CartsService
    service: CartsService = CartsService(
        session=session,
        session_data=session_data
    )
    result = await service.normalize_items_quantity(
        cart=cart,
        return_none=False,
    )
    return result


# /clear/me-session
async def clear_cart(
        cart: Union["Cart", "SessionCart"],
        session: AsyncSession,
        session_data: "SessionData",
):
    from .service import CartsService
    service: CartsService = CartsService(
        session=session,
        session_data=session_data
    )
    await service.clear_cart(
        cart=cart
    )
