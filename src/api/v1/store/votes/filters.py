from typing import Optional

from fastapi_filter.contrib.sqlalchemy import Filter
from pydantic import Field

from src.core.models import Vote


class VoteFilter(Filter):
    order_by: Optional[list[str]] = ['id']
    product_id: Optional[int] = Field(default=None, description="Filter by product", )
    stars__gte: Optional[int] = Field(default=None, description="Filter by stars greater or equal", )
    stars__lte: Optional[int] = Field(default=None, description="Filter by stars less or equal", )

    class Constants(Filter.Constants):
        model = Vote
