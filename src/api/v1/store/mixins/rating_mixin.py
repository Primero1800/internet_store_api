from decimal import Decimal

from pydantic import computed_field


class RatingMixin:
    @computed_field
    @property
    def rating(self) -> Decimal | None:
        if hasattr(self, 'voted_count') and hasattr(self, 'rating_summary'):
            return Decimal(self.rating_summary / self.voted_count)
        return None
