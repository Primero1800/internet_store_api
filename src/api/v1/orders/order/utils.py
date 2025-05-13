from decimal import Decimal, ROUND_HALF_UP
from typing import Union, TYPE_CHECKING, Any, Optional

from fastapi.encoders import jsonable_encoder

from src.api.v1.orders.order.schemas import (
    OrderShort,
    OrderRead,
)

if TYPE_CHECKING:
    from src.core.models import (
        Cart,
        Order,
    )
    from src.api.v1.carts.session_cart import SessionCart


async def get_schema_from_orm(
        orm_model: "Order",
        maximized: bool = True,
        relations: list | None = [],
):

    # BRUTE FORCE VARIANT
    user_short = None
    if maximized or 'user' in relations:
        if orm_model.user:
            from src.api.v1.users.user.utils import get_short_schema_from_orm as get_short_user_schema_from_orm
            user_short = await get_short_user_schema_from_orm(orm_model.user)
        if 'user' in relations:
            return user_short

    return OrderRead(
        **orm_model.to_dict(),
        user=user_short
    )


async def get_short_schema_from_orm(
    orm_model: "Order"
) -> OrderShort:

    dict_to_push = {**orm_model.to_dict(), 'order_content': [
        {
            'quantity': item['quantity'],
            'price': item['price'],
            'product_id': item['product']['id']
        } for item in orm_model.order_content
    ]}

    # BRUTE FORCE VARIANT
    return OrderShort(
        **dict_to_push
    )


async def get_normalized_order_content(
        cart_items: list[Any],
        cart: Optional[Union["Cart", "SessionCart"]] = None,
) -> list[dict]:

    from src.api.v1.carts import utils as carts_utils
    if cart:
        cart = await carts_utils.get_schema_from_orm(cart)
        return [jsonable_encoder(item) for item in cart.cart_items]
    cart_items = [await carts_utils.get_item_schema_from_orm(item) for item in cart_items]
    return [jsonable_encoder(item) for item in cart_items]


async def get_normalized_total_cost(
        cart: Union["Cart", "SessionCart"]
):
    return Decimal(
                sum(item.quantity * item.price for item in cart.cart_items)
            ).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
