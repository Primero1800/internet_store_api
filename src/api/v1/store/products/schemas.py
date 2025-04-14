from typing import Annotated, Optional, Any, List
from pydantic import BaseModel, Field, ConfigDict, model_validator
from pydantic_core.core_schema import ValidationInfo

from src.api.v1.store.mixins import TitleSlugMixin


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


class BaseProduct(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    title: base_title_field
    brand_id: int


class ProductCreate(BaseProduct, TitleSlugMixin):
    description: base_description_field


class ProductShort(BaseProduct):
    id: int
    image_file: str
    slug: str


class ProductRead(ProductShort):
    rubrics: List[Any]
    images: List[Any]
    brand: Any


class ProductUpdate(BaseProduct, TitleSlugMixin):
    description: base_description_field


class ProductPartialUpdate(BaseProduct, TitleSlugMixin):
    title: Optional[base_title_field] = None
    description: Optional[base_description_field] = None
    brand_id: Optional[int] = None
