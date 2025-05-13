from typing import Optional
from fastapi_filter.contrib.sqlalchemy import Filter

from src.core.models import UserTools


class UserToolsFilter(Filter):
    order_by: Optional[list[str]] = ['user_id',]

    class Constants(Filter.Constants):
        model = UserTools
