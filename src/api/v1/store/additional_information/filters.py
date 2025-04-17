from decimal import Decimal
from typing import Optional

from fastapi_filter.contrib.sqlalchemy import Filter
from pydantic import Field

from src.core.models import AdditionalInformation


class AddInfoFilter(Filter):
    order_by: Optional[list[str]] = ['id']
    product__id:  Optional[int] = Field(default=None, description="Filter by product id")
    product__title__like: Optional[str] = Field(default=None, description="Filter by product title contains", )
    available: Optional[bool] = Field(default=None, description="Filter if available")
    search_for: Optional[str] = None

    class Constants(Filter.Constants):
        model = AdditionalInformation
        search_field_name = "search_for"
        search_model_fields = ["product__title", "product__description"]

    class Config:
            populated_by_name = True
