from decimal import Decimal
from typing import Union, TYPE_CHECKING

from fastapi.encoders import jsonable_encoder

if TYPE_CHECKING:
    from src.core.models import (
        Cart,
    )
    from src.api.v1.carts.session_cart import SessionCart


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
