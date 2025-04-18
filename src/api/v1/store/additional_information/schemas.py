from typing import Annotated, Optional, Any

from pydantic import BaseModel, ConfigDict, condecimal, Field

base_weight_field = Annotated[condecimal(gt=0), Field(
    title="Product's weight",
)]

base_size_field = Annotated[str, Field(
    title="Product's size"
)]

base_guarantee_field = Annotated[str, Field(
    title="Product's guarantee"
)]


class BaseAddInfo(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    product_id: int
    weight: Optional[base_weight_field]
    size: Optional[base_size_field]
    guarantee: Optional[base_guarantee_field]


class AddInfoShort(BaseAddInfo):
    pass


class AddInfoRead(AddInfoShort):
    product: Any


class AddInfoCreate(BaseAddInfo):
    weight: Optional[base_weight_field]
    size: Optional[base_size_field]
    guarantee: Optional[base_guarantee_field]


class AddInfoUpdate(AddInfoCreate):
    pass


class AddInfoPartialUpdate(AddInfoCreate):
    product_id: Optional[int]
