from typing import TYPE_CHECKING

from src.api.v1.store.votes.schemas import VoteRead, VoteShort

if TYPE_CHECKING:
    from src.core.models import (
        Vote,
    )


async def get_schema_from_orm(
        orm_model: "Vote",
        maximized: bool = True,
        relations: list | None = [],
):

    # BRUTE FORCE VARIANT

    short_schema: VoteShort = await get_short_schema_from_orm(orm_model=orm_model)

    if maximized or 'product' in relations:
        from ..products.utils import get_short_schema_from_orm as get_short_product_schema_from_orm
        product_short = await get_short_product_schema_from_orm(orm_model.product)
    if 'product' in relations:
        return product_short

    if maximized or 'user' in relations:
        user_short = orm_model.user.to_dict() if orm_model.user else None
    if 'user' in relations:
        return user_short

    return VoteRead(
        **short_schema.model_dump(),
        product=product_short,
        user=user_short
    )


async def get_short_schema_from_orm(
    orm_model: "Vote"
) -> VoteShort:

    # BRUTE FORCE VARIANT
    return VoteShort(
        **orm_model.to_dict(),
    )
