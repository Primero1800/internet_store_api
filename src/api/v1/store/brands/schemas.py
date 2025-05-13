from typing import Annotated, Optional, Any, List
from pydantic import BaseModel, Field, ConfigDict, model_validator
from pydantic_core.core_schema import ValidationInfo

from src.api.v1.store.mixins import TitleSlugMixin


base_title_field = Annotated[str, Field(
        min_length=3, max_length=100,
        title="Brand's title",
        description="Brand's title that used in application"
    )]

base_description_field = Annotated[str, Field(
        max_length=500,
        title="Brand's description",
        description="Brand's description that used in application"
    )]


class BaseBrand(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    title: base_title_field


class BrandCreate(BaseBrand, TitleSlugMixin):
    description: base_description_field


class BrandShort(BaseBrand):
    id: int
    image_file: str
    slug: str

    @model_validator(mode="before")
    def image_file_getter(self, obj: Any, info: ValidationInfo) -> Any:
        if not hasattr(obj, "image_file") and info.context:
            setattr(obj, 'image_file', info.context.get('image_file', ''))
        return obj


class BrandRead(BrandShort):
    id: int
    description: base_description_field
    products: Optional[List[Any]]


class BrandUpdate(BaseBrand, TitleSlugMixin):
    description: base_description_field


class BrandPartialUpdate(BaseBrand, TitleSlugMixin):
    title: Optional[base_title_field] = None
    description: Optional[base_description_field] = None
