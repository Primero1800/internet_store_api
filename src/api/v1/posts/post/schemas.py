from datetime import datetime
from typing import Annotated, Literal, Optional, Any

from pydantic import BaseModel, ConfigDict, Field


base_name_field = Annotated[str, Field(
        min_length=3, max_length=75,
        title="Author's name",
        description="Displayed author's name"
    )]

base_review_field = Annotated[str, Field(
        max_length=1000,
        title="Author's review",
        description="Author's review"
    )]


class BasePost(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    product_id: Optional[int]
    user_id: int

    name: base_name_field
    review: base_review_field


class PostShort(BasePost):
    id: int
    published: datetime


class PostRead(PostShort):
    product: Optional[Any]
    user: Any


class PostCreate(BasePost):
    pass


class PostUpdate(PostCreate):
    pass


class PostPartialUpdate(BasePost):
    product_id: Optional[int]
    user_id: Optional[int]

    name: Optional[base_name_field]
    review: Optional[base_review_field]
