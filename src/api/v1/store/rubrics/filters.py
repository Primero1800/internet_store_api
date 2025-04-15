from typing import Optional

from fastapi_filter.contrib.sqlalchemy import Filter
from pydantic import Field

from src.core.models import Rubric


class RubricFilter(Filter):
    order_by: Optional[list[str]] = ['id']
    title__like: Optional[str] = Field(default=None, description="Filter by title contains", )
    search_for: Optional[str] = None

    class Constants(Filter.Constants):
        model = Rubric
        search_field_name = "search_for"
        search_model_fields = ["description", ]

    class Config:
            populated_by_name = True
