from typing import Optional

from fastapi_filter import FilterDepends, with_prefix
from fastapi_filter.contrib.sqlalchemy import Filter
from pydantic import Field

from src.core.models import UserTools
from ...store.products.filters import ProductFilterShort


class UserToolsFilter(Filter):
    order_by: Optional[list[str]] = ['user_id',]

    class Constants(Filter.Constants):
        model = UserTools
