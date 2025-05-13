from typing import TYPE_CHECKING, Any

from ..products.utils import get_short_schema_from_orm as get_short_product_schema_from_orm

from .schemas import (
    AddInfoShort,
    AddInfoRead,
)

if TYPE_CHECKING:
    from src.core.models import (
        AdditionalInformation,
    )


async def get_short_schema_from_orm(
    orm_model: "AdditionalInformation"
) -> AddInfoShort:

    # BRUTE FORCE VARIANT
    return AddInfoShort(
        **orm_model.to_dict(),
    )


async def get_schema_from_orm(
    orm_model: "AdditionalInformation",
    maximized: bool = True,
    relations: list | None = None,
) -> AddInfoRead | Any:

    # BRUTE FORCE VARIANT

    short_schema: AddInfoShort = await get_short_schema_from_orm(orm_model=orm_model) if maximized else {}

    product_short = None
    if maximized or (relations and 'product' in relations):
        product_short = await get_short_product_schema_from_orm(orm_model.product)
    if relations and 'product' in relations:
        return product_short

    return AddInfoRead(
        **short_schema.model_dump(),
        product=product_short
    )
