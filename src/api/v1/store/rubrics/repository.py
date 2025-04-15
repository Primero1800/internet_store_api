import logging
from typing import Sequence

from sqlalchemy import select, Result
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from src.core.models import Rubric


class BrandsRepository:
    def __init__(
            self,
            session: AsyncSession,
    ):
        self.session = session
        self.logger = logging.getLogger(__name__)

    async def get_all(self) -> Sequence:
        stmt = select(Rubric).options(
            joinedload(Rubric.image)
        ).order_by(Rubric.id)

        result: Result = await self.session.execute(stmt)
        return result.unique().scalars().all()