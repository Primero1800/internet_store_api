from typing import TYPE_CHECKING
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.config import DBConfigurer
from .service import SaleInfoService

if TYPE_CHECKING:
    from src.core.models import SaleInformation


async def get_one(
    product_id: int,
    session: AsyncSession = Depends(DBConfigurer.session_getter)
) -> "SaleInformation":
    service: SaleInfoService = SaleInfoService(
        session=session
    )
    return await service.get_one(product_id=product_id, to_schema=False)
