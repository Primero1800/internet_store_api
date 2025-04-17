import logging
from typing import Sequence, TYPE_CHECKING

from sqlalchemy import select, Result
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from src.core.models import AdditionalInformation

if TYPE_CHECKING:
    from .filters import (
        AddInfoFilter,
    )

CLASS = "Product"


class AddInfoRepository:
    def __init__(
            self,
            session: AsyncSession,
    ):
        self.session = session
        self.logger = logging.getLogger(__name__)

    async def get_all(
            self,
            filter_model: "AddInfoFilter",
    ) -> Sequence:

        query_filter = filter_model.filter(select(AdditionalInformation))
        stmt_filtered = filter_model.sort(query_filter)

        stmt = stmt_filtered.options(
        ).order_by(AdditionalInformation.id)

        result: Result = await self.session.execute(stmt)
        return result.unique().scalars().all()
