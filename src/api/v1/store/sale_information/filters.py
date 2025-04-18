from typing import Optional

from fastapi_filter import FilterDepends, with_prefix
from fastapi_filter.contrib.sqlalchemy import Filter
from pydantic import Field

from src.core.models import SaleInformation
from ..products.filters import ProductFilterShort


class SaleInfoFilter(Filter):
    order_by: Optional[list[str]] = ['product_id',]

    sold_count__gte: Optional[int] = Field(default=None, description="Filter by product sold count greater or equal", )
    sold_count__lte: Optional[int] = Field(default=None, description="Filter by product sold count less or equal", )

    viewed_count__gte: Optional[int] = Field(default=None, description="Filter by product viewed count greater or equal", )
    viewed_count__lte: Optional[int] = Field(default=None, description="Filter by product viewed count less or equal", )

    voted_count__gte: Optional[int] = Field(default=None, description="Filter by product voted count greater or equal", )
    voted_count__lte: Optional[int] = Field(default=None, description="Filter by product voted count less or equal", )

    rating__gte: Optional[int] = Field(default=None, description="Filter by product voted count greater or equal", )
    rating__lte: Optional[int] = Field(default=None, description="Filter by product voted count less or equal", )

    class Constants(Filter.Constants):
        model = SaleInformation


class SaleInfoFilterComplex(SaleInfoFilter):
    product_id: Optional[int] = Field(default=None, description="Filter by product id")
    product: Optional[ProductFilterShort] = FilterDepends(with_prefix("product", ProductFilterShort))
    search_for: Optional[str] = None

    class Constants(SaleInfoFilter.Constants):
        model = SaleInformation
        search_field_name = "search_for"
        search_model_fields = ["product__title", "product__description"]
