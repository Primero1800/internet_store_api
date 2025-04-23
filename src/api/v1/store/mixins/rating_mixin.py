from decimal import Decimal

from pydantic import computed_field

from src.tools.exceptions import UnreachableValueError


class RatingMixin:
    @computed_field
    @property
    def rating(self) -> Decimal | None:
        if hasattr(self, 'voted_count') and hasattr(self, 'rating_summary'):
            result = Decimal(self.rating_summary / self.voted_count) if self.voted_count != 0 else 0
            if result > 5:
                raise UnreachableValueError
            return result
        return None
