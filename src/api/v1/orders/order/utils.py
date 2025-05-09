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
    if not isinstance(cart.cart_items[0], dict):
        order_content = [jsonable_encoder(item.to_dict()) for item in cart.cart_items]
    else:
        order_content = [jsonable_encoder(item) for item in cart.cart_items]
        for item in order_content:
            if 'product' in item:
                del item['product']
    return order_content


async def get_normalized_total_cost(
        cart: Union["Cart", "SessionCart"]
):
    return Decimal(
                sum(
                    item.quantity*item.price if hasattr(item, "quantity")
                    else item['quantity']*item['price'] for item in cart.cart_items
                )
            ).quantize(Decimal("0.01"))
