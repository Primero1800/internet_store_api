from typing import TYPE_CHECKING
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.config import DBConfigurer
from .service import UserToolsService

if TYPE_CHECKING:
    from src.core.models import UserTools


async def get_one(
    user_id: int,
    session: AsyncSession = Depends(DBConfigurer.session_getter)
) -> "UserTools":
    service: UserToolsService = UserToolsService(
        session=session
    )
    return await service.get_one(user_id=user_id, to_schema=False)
