from decimal import Decimal
from typing import Iterable

from pydantic import computed_field


class TotalCostMixin:
    @computed_field
    @property
    def total_cost(self) -> Decimal:
        if hasattr(self, 'cart_items') and isinstance(self.cart_items, Iterable):
            result = 0
            for cart_item in self.cart_items:
                result += cart_item.quantity * cart_item.price
            return Decimal(result)
        return Decimal(0.00)
