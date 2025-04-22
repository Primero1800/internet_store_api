from datetime import datetime
from typing import Annotated, Literal, Optional

from pydantic import BaseModel, ConfigDict, Field

from src.tools.stars_choices import StarsChoices

base_name_field = Annotated[str, Field(
        min_length=3, max_length=50,
        title="Author's name",
        description="Displayed author's name"
    )]

base_review_field = Annotated[str, Field(
        max_length=500,
        title="Product's review",
        description="product's review"
    )]

base_stars_field = Annotated[Literal[*StarsChoices.choices()], Field(
    title="Rating",
    description="Author's rating for product"
)]


class BaseVote(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    product_id: int
    user_id: int

    name: base_name_field
    review: base_review_field
    stars: base_stars_field


class VoteRead(BaseVote):
    published: datetime


class VoteCreate(BaseVote):
    pass


class VoteUpdate(VoteCreate):
    pass


class VotePartialUpdate(BaseVote):
    product_id: Optional[int]
    user_id: Optional[int]

    name: Optional[base_name_field]
    review: Optional[base_review_field]
    stars: Optional[base_stars_field]
