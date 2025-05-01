from dataclasses import dataclass
from datetime import datetime
from typing import Optional, Any, Annotated

from pydantic import Field, conint, condecimal


@dataclass
class SessionCartItem:

    price: condecimal(gt=0, max_digits=8, decimal_places=2)
    product_id: conint(gt=0)
    cart_id: Optional[int] = None

    product: Optional[Any] = None
    quantity: conint(gt=0) = 1

    def __str__(self):
        return f"{self.__class__.__name__}(product_id={self.product_id})"

    def __repr__(self):
        return str(self)

    def to_dict(self):
        return {
            "product_id": self.product_id,
            "cart_id": self.cart_id,
            "price": self.price,
            "product": self.product,
            "quantity": self.quantity
        }


@dataclass
class SessionCart:
    user_id: Optional[int] = None

    user: Optional[Any] = None

    created: str = datetime.now().isoformat()

    cart_items: dict[int, SessionCartItem] = dict

    def __str__(self):
        return f"{self.__class__.__name__}()"

    def __repr__(self):
        return str(self)

    def to_dict(self):
        return {
            "user_id": self.user_id,
            "user": self.user,
            "created": datetime.fromisoformat(self.created),
            "cart_items": self.cart_items.values()
        }
