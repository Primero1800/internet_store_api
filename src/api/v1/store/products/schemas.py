from datetime import datetime
from decimal import Decimal
from typing import Annotated, Optional, Any, List, Literal
from pydantic import BaseModel, Field, ConfigDict, conint, condecimal

from src.api.v1.store.mixins import TitleSlugMixin, PriceMixin
from src.tools.discount_choices import DiscountChoices

base_title_field = Annotated[str, Field(
        min_length=3, max_length=100,
        title="Product's title",
        description="Product's title that used in application"
    )]

base_description_field = Annotated[str, Field(
        max_length=500,
        title="Product's description",
        description="Product's description that used in application"
    )]

base_start_price_field = Annotated[condecimal(gt=0), Field(
    max_digits=8,
    decimal_places=2,
    title="Product's start price"
)]

base_discount_field = Annotated[Literal[*DiscountChoices.choices()], Field(
    title="Product's discount"
)]

base_available_filed = Annotated[bool, Field(
    title="If product is available"
)]

base_quantity_filed = Annotated[conint(ge=0), Field(
    title="Product's quantity",
)]



class BaseProduct(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    title: base_title_field
    brand_id: int

    start_price: base_start_price_field
    discount: base_discount_field
    available: base_available_filed


class ProductCreate(BaseProduct, TitleSlugMixin, PriceMixin):
    description: base_description_field
    quantity: base_quantity_filed


class ProductShort(BaseProduct):
    id: int
    image_file: str
    slug: str

    start_price: Decimal
    price: Decimal


class ProductReadPublic(ProductShort):
    description: base_description_field

    published: datetime

    rubrics: List[Any]
    images: List[Any]
    brand: Any


class ProductRead(ProductReadPublic):
    quantity: base_quantity_filed


class ProductUpdate(BaseProduct, TitleSlugMixin, PriceMixin):
    description: base_description_field
    quantity: base_quantity_filed


class ProductPartialUpdate(BaseProduct, TitleSlugMixin, PriceMixin):
    title: Optional[base_title_field] = None
    description: Optional[base_description_field] = None
    brand_id: Optional[int] = None
    start_price: Optional[base_start_price_field] = None
    discount: Optional[base_discount_field] = None
    available: Optional[base_discount_field] = None
