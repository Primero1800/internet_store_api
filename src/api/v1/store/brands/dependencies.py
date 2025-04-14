from typing import TYPE_CHECKING
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.config import DBConfigurer
from .service import BrandsService

if TYPE_CHECKING:
    from src.core.models import Brand

CLASS = "Brand"


async def get_one_simple(
    id: int,
    session: AsyncSession = Depends(DBConfigurer.session_getter)
) -> "Brand":
    service: BrandsService = BrandsService(
        session=session
    )
    return await service.get_one(id=id, to_schema=False)
