from decimal import Decimal
from typing import Union, TYPE_CHECKING

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
    short_schema: OrderShort = await get_short_schema_from_orm(orm_model=orm_model)

    if maximized or 'user' in relations:
        if orm_model.user:
            from src.api.v1.users.user.utils import get_short_schema_from_orm as get_short_user_schema_from_orm
            user_short = await get_short_user_schema_from_orm(orm_model.user)
        else:
            user_short = None
        if 'user' in relations:
            return user_short

    return OrderRead(
        **short_schema.model_dump(),
        user=user_short
    )


async def get_short_schema_from_orm(
    orm_model: "Order"
) -> OrderShort:

    # BRUTE FORCE VARIANT
    return OrderShort(
        **orm_model.to_dict(),
    )


async def get_normalized_order_content(
        cart: Union["Cart", "SessionCart"]
) -> list[dict]:

    from src.api.v1.carts import utils as carts_utils
    cart = await carts_utils.get_schema_from_orm(cart)
    return [jsonable_encoder(item) for item in cart.cart_items]


async def get_normalized_total_cost(
        cart: Union["Cart", "SessionCart"]
):
    return Decimal(
                sum(
                    item.quantity*item.price if hasattr(item, "quantity")
                    else item['quantity']*item['price'] for item in cart.cart_items
                )
            ).quantize(Decimal("0.01"))
