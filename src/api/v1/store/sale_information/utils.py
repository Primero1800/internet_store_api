from typing import TYPE_CHECKING, Any

from ..products.utils import get_short_schema_from_orm as get_short_product_schema_from_orm

from .schemas import (
    SaleInfoShort,
    SaleInfoRead,
)

if TYPE_CHECKING:
    from src.core.models import (
        SaleInformation,
    )


async def get_short_schema_from_orm(
    orm_model: "SaleInformation"
) -> SaleInfoShort:

    # BRUTE FORCE VARIANT
    return SaleInfoShort(
        **orm_model.to_dict(),
    )


async def get_schema_from_orm(
    orm_model: "SaleInformation",
    maximized: bool = True,
    relations: list | None = [],
) -> SaleInfoRead | Any:

    # BRUTE FORCE VARIANT

    short_schema: SaleInfoShort = await get_short_schema_from_orm(orm_model=orm_model) if maximized else {}

    product_short = None
    if maximized or 'product' in relations:
        product_short = await get_short_product_schema_from_orm(orm_model.product)
    if 'product' in relations:
        return product_short

    return SaleInfoRead(
        **short_schema.model_dump(),
        product=product_short
    )
