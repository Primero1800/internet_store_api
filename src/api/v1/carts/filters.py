from decimal import Decimal
from typing import Optional

from fastapi_filter.contrib.sqlalchemy import Filter
from pydantic import Field

from src.core.models import Cart


class CartFilter(Filter):
    order_by: Optional[list[str]] = ['user_id']

    class Constants(Filter.Constants):
        model = Cart
