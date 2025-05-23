from typing import Optional

from fastapi_filter import FilterDepends, with_prefix
from fastapi_filter.contrib.sqlalchemy import Filter
from pydantic import Field

from src.api.v1.store.products.filters import ProductFilterShort
from src.core.models import Brand


class BrandFilter(Filter):
    order_by: Optional[list[str]] = ['id']
    title__like: Optional[str] = Field(default=None, description="Filter by title contains", )
    search_for: Optional[str] = None

    class Constants(Filter.Constants):
        model = Brand
        search_field_name = "search_for"
        search_model_fields = ["description", ]


class BrandFilterComplex(BrandFilter):
    product: Optional[ProductFilterShort] = FilterDepends(with_prefix("product", ProductFilterShort))
    search_for: Optional[str] = None

    class Constants(BrandFilter.Constants):
        search_model_fields = ["product__title", "product__description"]
