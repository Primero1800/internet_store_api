from typing import TYPE_CHECKING
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.config import DBConfigurer
from .service import AddInfoService

if TYPE_CHECKING:
    from src.core.models import AdditionalInformation


async def get_one_simple(
    id: int,
    session: AsyncSession = Depends(DBConfigurer.session_getter)
) -> "AdditionalInformation":
    service: AddInfoService = AddInfoService(
        session=session
    )
    return await service.get_one(id=id, to_schema=False)


async def get_one_simple_by_product_id(
    product_id: int,
    session: AsyncSession = Depends(DBConfigurer.session_getter)
) -> "AdditionalInformation":
    service: AddInfoService = AddInfoService(
        session=session
    )
    return await service.get_one(product_id=product_id, to_schema=False)
