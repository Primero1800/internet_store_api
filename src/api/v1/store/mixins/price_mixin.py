from decimal import Decimal

from pydantic import computed_field


class PriceMixin:
    @computed_field
    @property
    def price(self) -> Decimal | None:
        if hasattr(self, 'start_price') and hasattr(self, 'discount'):
            return Decimal(self.start_price * (100 - self.discount) / 100)
        return None
