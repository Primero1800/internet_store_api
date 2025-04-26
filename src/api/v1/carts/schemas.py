from datetime import datetime
from decimal import Decimal
from typing import Annotated, Optional, Any

from pydantic import BaseModel, ConfigDict, Field, conint


class BaseCart(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    user_id: int


class CartShort(BaseCart):
    created: datetime
    cart_items: list[Any]


class CartRead(CartShort):
    pass


class CartCreate(BaseCart):
    pass


class CartUpdate(CartCreate):
    pass


class CartPartialUpdate(CartCreate):
    pass


base_quantity_field = Annotated[conint(ge=1), Field(
        title="Item's quantity",
        description="Item's quantity"
    )]


class BaseCartItem(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    quantity: base_quantity_field


class CartItemShort(BaseCartItem):
    product_id: int
    price: Decimal


class CartItemRead(BaseCartItem):
    product: Any
    price: Decimal


class CartItemCreate(CartItemShort):
    cart_id: Optional[int] = None


class CartItemUpdate(BaseCartItem):
    pass
