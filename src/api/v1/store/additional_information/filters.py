from decimal import Decimal
from typing import Optional

from fastapi_filter import FilterDepends, with_prefix
from fastapi_filter.contrib.sqlalchemy import Filter
from pydantic import Field

from src.core.models import AdditionalInformation
from ..products.filters import ProductFilterShort


class AddInfoFilter(Filter):
    order_by: Optional[list[str]] = ['id']
    guarantee__like: Optional[str] = Field(default=None, description="Filter by product guarantee contains", )

    class Constants(Filter.Constants):
        model = AdditionalInformation


class AddInfoFilterComplex(AddInfoFilter):
    product_id: Optional[int] = Field(default=None, description="Filter by product id")
    product: Optional[ProductFilterShort] = FilterDepends(with_prefix("product", ProductFilterShort))
    search_for: Optional[str] = None

    class Constants(AddInfoFilter.Constants):
        model = AdditionalInformation
        search_field_name = "search_for"
        search_model_fields = ["product__title", "product__description"]
