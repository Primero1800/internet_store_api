from decimal import Decimal
from typing import Optional

from fastapi_filter.contrib.sqlalchemy import Filter
from pydantic import Field

from src.core.models import Product


class ProductFilter(Filter):
    order_by: Optional[list[str]] = ['id']
    title__like: Optional[str] = Field(default=None, description="Filter by title contains", )
    discount__gte: Optional[int] = Field(default=None, description="Filter by discount contains", )
    price__gte: Optional[Decimal] = Field(
        default=None,
        max_digits=8,
        decimal_places=2,
        description="Filter by price greater or equal",
    )
    price__lte: Optional[Decimal] = Field(
        default=None,
        max_digits=8,
        decimal_places=2,
        description="Filter by price less or equal",
    )
    available: Optional[bool] = Field(default=None, description="Filter if available")
    search_for: Optional[str] = None

    class Constants(Filter.Constants):
        model = Product
        search_field_name = "search_for"
        search_model_fields = ["description", ]

    class Config:
            populated_by_name = True
