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
    )
    from src.api.v1.carts.session_cart import SessionCart


async def get_schema_from_orm(
        orm_model: "Cart",
        maximized: bool = True,
        relations: list | None = [],
):
    # BRUTE FORCE VARIANT

    # short_schema: CartShort = await get_short_schema_from_orm(orm_model=orm_model)

    cart_items = None
    if maximized or 'products' in relations:
        cart_items = []
        from ..store.products.utils import get_short_schema_from_orm as get_short_product_schema_from_orm
        for cart_item in orm_model.cart_items:
            cart_items.append(
                CartItemRead(
                    **cart_item.to_dict(),
                    product=await get_short_product_schema_from_orm(cart_item.product)
                )
            )
        if 'products' in relations:
            return cart_items

    user_short = None
    if maximized or 'user' in relations:
        if orm_model.user:
            from src.api.v1.users.user.utils import get_short_schema_from_orm as get_short_user_schema_from_orm
            user_short = await get_short_user_schema_from_orm(orm_model.user)
        if 'user' in relations:
            return user_short

    return CartRead(
        **orm_model.to_dict(),
        cart_items=cart_items,
        user=user_short
    )


async def get_short_schema_from_orm(
        orm_model: Union["Cart", "SessionCart"]
) -> CartShort:

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
        orm_model: Union["CartItem",dict]
) -> CartItemShort | ORJSONResponse:

    if isinstance(orm_model, ORJSONResponse):
        return orm_model

    if isinstance(orm_model, dict): # For SessionCartItem
        return CartItemShort(
            **orm_model
        )

    # BRUTE FORCE VARIANT
    return CartItemShort(
        **orm_model.to_dict()
    )


async def get_item_schema_from_orm(
        orm_model: "CartItem"
) -> CartItemRead | ORJSONResponse:

    if isinstance(orm_model, ORJSONResponse):
        return orm_model

    from ..store.products.utils import get_short_schema_from_orm as get_short_product_schema_from_orm
    return CartItemRead(
        **orm_model.to_dict(),
        product=await get_short_product_schema_from_orm(orm_model.product)
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
