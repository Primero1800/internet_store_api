from typing import Annotated, Optional, Any

from pydantic import BaseModel, ConfigDict, Field, conint, condecimal

from src.api.v1.store.mixins import RatingMixin

base_sold_count_field = Annotated[conint(ge=0), Field(
    title="Product's sold count",
)]

base_viewed_count_field = Annotated[conint(ge=0), Field(
    title="Product's viewed count",
)]

base_voted_count_field = Annotated[conint(ge=0), Field(
    title="Product's voted count",
)]

base_rating_summary_field = Annotated[conint(ge=0), Field(
    title="Product's summary rating",
)]

base_rating_field = Annotated[Optional[condecimal(ge=0)], Field(
    title="Product's summary rating",
    decimal_places=2,
    default=None
)]


class BaseSaleInfo(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    product_id: int


class SaleInfoShort(BaseSaleInfo):
    sold_count: base_sold_count_field
    viewed_count: base_viewed_count_field
    voted_count: base_voted_count_field
    rating_summary: base_rating_summary_field
    rating: base_rating_field


class SaleInfoRead(SaleInfoShort):
    product: Any


class SaleInfoCreate(BaseSaleInfo):
    pass


class SaleInfoUpdate(SaleInfoCreate):
    pass


class SaleInfoPartialUpdate(SaleInfoCreate, RatingMixin):
    product_id: Optional[int]
    voted_count: Optional[base_voted_count_field]
    viewed_count: Optional[base_viewed_count_field]
    sold_count: Optional[base_sold_count_field]
    rating_summary: Optional[base_rating_summary_field]
