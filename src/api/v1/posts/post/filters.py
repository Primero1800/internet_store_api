from typing import Optional

from fastapi_filter.contrib.sqlalchemy import Filter
from pydantic import Field

from src.core.models import Post


class PostFilter(Filter):
    order_by: Optional[list[str]] = ['id']

    name__like: Optional[str] = Field(default=None, description="Filter by name contains", )
    search_for: Optional[str] = None

    class Constants(Filter.Constants):
        model = Post
        search_field_name = "search_for"
        search_model_fields = ["review", ]
