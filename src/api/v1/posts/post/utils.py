from typing import TYPE_CHECKING

from .schemas import PostRead, PostShort

if TYPE_CHECKING:
    from src.core.models import (
        Post,
    )


async def get_schema_from_orm(
        orm_model: "Post",
        maximized: bool = True,
        relations: list | None = [],
):

    # BRUTE FORCE VARIANT

    short_schema: PostShort = await get_short_schema_from_orm(orm_model=orm_model)

    if maximized or 'product' in relations:
        from ...store.products.utils import get_short_schema_from_orm as get_short_product_schema_from_orm
        product_short = await get_short_product_schema_from_orm(orm_model.product)
        if 'product' in relations:
            return product_short

    if maximized or 'user' in relations:
        if orm_model.user:
            from src.api.v1.users.user.utils import get_short_schema_from_orm as get_short_user_schema_from_orm
            user_short = await get_short_user_schema_from_orm(orm_model.user)
        else:
            user_short = None
        if 'user' in relations:
            return user_short

    return PostRead(
        **short_schema.model_dump(),
        product=product_short,
        user=user_short
    )


async def get_short_schema_from_orm(
    orm_model: "Post"
) -> PostShort:

    # BRUTE FORCE VARIANT
    return PostShort(
        **orm_model.to_dict(),
    )
