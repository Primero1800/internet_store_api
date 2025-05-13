from typing import TYPE_CHECKING, Any, Optional

from sqlalchemy.ext.asyncio import AsyncSession

from ..products.utils import get_short_schema_from_orm as get_short_product_schema_from_orm

from .schemas import (
    SaleInfoShort,
    SaleInfoRead,
)

if TYPE_CHECKING:
    from src.core.models import (
        SaleInformation,
    )


CLASS = "SaleInformation"


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
    relations: list | None = None,
) -> SaleInfoRead | Any:

    # BRUTE FORCE VARIANT

    short_schema: SaleInfoShort = await get_short_schema_from_orm(orm_model=orm_model) if maximized else {}

    product_short = None
    if maximized or (relations and 'product' in relations):
        product_short = await get_short_product_schema_from_orm(orm_model.product)
    if relations and 'product' in relations:
        return product_short

    return SaleInfoRead(
        **short_schema.model_dump(),
        product=product_short
    )


# /get-or-create/{product_id}
async def get_or_create(
        product_id: int,
        session: AsyncSession,
) -> "SaleInformation":
    from .service import SaleInfoService
    service = SaleInfoService(
        session=session
    )
    return await service.get_or_create(product_id)


# /do-vote
async def do_vote(
        session: AsyncSession,
        product_id_vote_add: Optional[int] = None,
        vote_add: Optional[int] = None,
        product_id_vote_del: Optional[int] = None,
        vote_del: Optional[int] = None,
):
    from .service import SaleInfoService
    service = SaleInfoService(
        session=session
    )
    return await service.do_vote(
        product_id_vote_add=product_id_vote_add,
        vote_add=vote_add,
        product_id_vote_del=product_id_vote_del,
        vote_del=vote_del,
    )


# /do-view
async def do_view(
        session: AsyncSession,
        product_id: int,
):
    from .service import SaleInfoService
    service = SaleInfoService(
        session=session
    )
    return await service.do_view_or_sell(
        product_id=product_id,
    )


# /do-sell
async def do_sell(
        session: AsyncSession,
        product_id: int,
        count: int = 1,
):
    from .service import SaleInfoService
    service = SaleInfoService(
        session=session
    )
    return await service.do_view_or_sell(
        product_id=product_id,
        action='sell',
        count=count,
    )
